# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AWS SAM serverless backend that bridges ElevenLabs voice agents with Mem0 Cloud for conversational memory management. Three Lambda functions handle the complete memory lifecycle with <500ms latency targets.

## Commands

### Build & Deploy
```bash
# Build Lambda layer (REQUIRED first step)
cd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..

# Build SAM application
sam build

# Deploy (first time - guided)
sam deploy --guided

# Deploy (subsequent)
sam deploy
```

### Local Testing
```bash
# Invoke function locally
sam local invoke AgenticMemoriesClientData -e events/client_data.json

# Start local API
sam local start-api
```

### Testing
```bash
# Install dev dependencies
pip install -r requirements.txt

# Run unit tests
pytest tests/

# Run integration tests (requires deployed stack)
python3 test_clientdata.py      # Test ClientData endpoint with auth
python3 test_postcall.py         # Test PostCall endpoint with HMAC
python3 test_personalized_greetings.py  # Test greeting generation
python3 test_production_ready.py # Comprehensive production tests
```

### Monitoring
```bash
# Tail CloudWatch logs
aws logs tail /aws/lambda/AgenticMemoriesClientData --follow
aws logs tail /aws/lambda/AgenticMemoriesRetrieve --follow
aws logs tail /aws/lambda/AgenticMemoriesPostCall --follow
```

### Cleanup
```bash
aws cloudformation delete-stack --stack-name AgenticMemoriesStack
```

## Architecture

### Three-Function Design
- **ClientData** (`src/client_data/handler.py`): Pre-call memory retrieval triggered by ElevenLabs Conversation Initiation webhook. Returns all memories for caller, extracts caller name, generates personalized greeting, and formats context into prompt override for agent.
- **Retrieve** (`src/retrieve/handler.py`): In-call semantic search triggered by agent tool. Returns top N relevant memories based on query.
- **PostCall** (`src/post_call/handler.py`): Post-call async memory storage triggered by webhook. Stores both factual (summary) and semantic (transcript) memories.

### API Gateway Separation
Each function has its own HTTP API Gateway for minimal latency (no routing overhead). All use shared Lambda layer containing `mem0ai` package.

### Memory Types
- **Factual Memory**: Stored knowledge, preferences, summaries (`metadata.type = "factual"`)
- **Semantic Memory**: Full conversation context from transcript (`metadata.type = "semantic"`)
- **User ID**: Phone number format (e.g., `+16129782029`) used as Mem0 `user_id`

## Critical Patterns

### Personalized Greetings (ClientData)
ClientData automatically extracts caller names from memories using regex patterns and generates personalized greetings based on:
- Caller name (if found in factual or semantic memories)
- Returning vs new caller status
- Account status (premium, VIP, gold, silver tiers)
- Last interaction context (inquiry, issue resolution)
- Communication preferences (email, phone)

Key functions in `src/client_data/handler.py`:
- `extract_caller_name()` - Extracts name from memory strings using multiple patterns
- `generate_personalized_greeting()` - Creates contextual greeting based on caller info

The greeting is returned in the `first_message` field of the agent config override.

### Mem0 Client Initialization
**ALWAYS initialize Mem0 client OUTSIDE the handler** for reuse across Lambda invocations:

```python
from mem0 import MemoryClient
import os

# Initialize OUTSIDE handler - critical for performance
client = MemoryClient(
    api_key=os.environ['MEM0_API_KEY'],
    org_id=os.environ['MEM0_ORG_ID'],
    project_id=os.environ['MEM0_PROJECT_ID']
)

def lambda_handler(event, context):
    # Use client here
    memories = client.get_all(user_id="...")
```

### Authentication Patterns

**ClientData** - Workspace key validation:
```python
headers = event.get('headers', {})
workspace_key = headers.get('x-workspace-key') or headers.get('X-Workspace-Key')
if workspace_key != WORKSPACE_KEY:
    return {'statusCode': 401, 'body': json.dumps({'error': 'Unauthorized'})}
```

**PostCall** - HMAC signature verification:
- Parse `ElevenLabs-Signature` header format: `t=timestamp,v0=hash`
- Build signed payload: `{timestamp}.{raw_body}`
- Verify with HMAC-SHA256 using `ELEVENLABS_HMAC_KEY`
- Reject signatures older than 30 minutes
- See `verify_hmac_signature()` in `src/post_call/handler.py`

**Retrieve** - No authentication (trusted agent-backend connection)

### Response Format Conventions

**ClientData** returns ElevenLabs-specific format with prompt override and personalized greeting:
```python
{
    "type": "conversation_initiation_client_data",
    "dynamic_variables": {
        "caller_id": "...",
        "caller_name": "...",  # Extracted from memories if available
        "memory_count": "...",
        "memory_summary": "...",
        "returning_caller": "yes/no"
    },
    "conversation_config_override": {
        "agent": {
            "prompt": {
                "prompt": "# Known Information About This Caller:\n..."
            },
            "first_message": "Hello [Name]! ..."  # Personalized greeting
        }
    }
}
```

**Note**: ClientData supports both `caller_id` and `system__caller_id` field names from ElevenLabs.

**Retrieve** returns simple memory array:
```python
{"memories": [...]}
```

**PostCall** returns immediate `200 OK`, processes asynchronously:
```python
# Return immediately
response = {'statusCode': 200, 'body': json.dumps({'status': 'ok'})}
# Then process async (errors logged but don't affect response)
```

### Memory Storage Pattern (PostCall)

Store two types of memories from call data:

```python
# 1. Factual Memory (summary + evaluation)
client.add(
    messages=[{'role': 'assistant', 'content': summary + evaluation_rationale}],
    user_id=caller_id,
    metadata={'type': 'factual', 'agent_id': ..., 'conversation_id': ..., 'timestamp': ...},
    version="v2"
)

# 2. Semantic Memory (full transcript)
client.add(
    messages=transcript,  # Full chat messages array
    user_id=caller_id,
    metadata={'type': 'semantic', 'agent_id': ..., 'conversation_id': ..., 'timestamp': ...},
    version="v2"
)
```

## Environment Variables

All Lambdas share these environment variables (configured via SAM template parameters):

**Required:**
- `MEM0_API_KEY` - Mem0 API key
- `MEM0_ORG_ID` - Mem0 organization ID
- `MEM0_PROJECT_ID` - Mem0 project ID
- `ELEVENLABS_WORKSPACE_KEY` - Workspace secret for ClientData auth
- `ELEVENLABS_HMAC_KEY` - HMAC signing key for PostCall auth

**Configured:**
- `MEM0_DIR=/tmp/.mem0` - SDK cache directory
- `MEM0_SEARCH_LIMIT=3` - Max results for semantic search
- `MEM0_TIMEOUT=5` - Timeout in seconds

## Error Handling

**Synchronous functions** (ClientData, Retrieve):
- Log error with full context including user_id
- Return appropriate HTTP error (400/401/500)
- Error message visible to ElevenLabs

**Asynchronous function** (PostCall):
- Return 200 OK immediately
- Log all processing errors with context
- Continue execution (catch exceptions, don't throw)
- No retry mechanism (ElevenLabs handles retries)

## Project Structure

```
AgenticMemory/
├── template.yaml              # SAM CloudFormation template
├── requirements.txt           # Dev dependencies (pytest, boto3)
├── test_*.py                  # Integration test scripts (clientdata, postcall, greetings, etc.)
├── layer/
│   ├── requirements.txt       # Lambda layer dependencies (mem0ai only)
│   └── python/                # Built layer contents (generated)
├── tests/
│   └── test_client_data_unit.py  # Unit tests
└── src/
    ├── client_data/handler.py # Pre-call: auth + get_all() + name extraction + greeting generation
    ├── retrieve/handler.py    # In-call: search() with limit
    └── post_call/handler.py   # Post-call: HMAC + async add() for 2 memory types
```

**Layer separation**: `layer/requirements.txt` only contains `mem0ai`. Root `requirements.txt` has dev dependencies.

**Test organization**: Unit tests in `tests/`, integration tests as `test_*.py` scripts in root.

## Integration Points

### ElevenLabs Configuration
After deployment, configure three webhook URLs (from SAM outputs):

1. **Conversation Initiation webhook** → `ClientDataApiUrl`
   - Add header: `X-Workspace-Key: <your-workspace-key>`

2. **Agent tool** → `RetrieveApiUrl`
   - Method: POST
   - Request body: `{"query": "{{query}}", "user_id": "{{caller_id}}"}`

3. **Post-call webhook** → `PostCallApiUrl`
   - Authentication: HMAC signature (automatic)

### Mem0 Operations
- `client.get_all(user_id=caller_id)` - Retrieve all memories
- `client.search(query, user_id, limit)` - Semantic search
- `client.add(messages, user_id, metadata)` - Store new memories

## Performance Considerations

- **Separate HTTP APIs**: Eliminates routing overhead for minimal latency
- **Client reuse**: Mem0 client initialized outside handler (warm start optimization)
- **Async PostCall**: Returns 200 immediately, processes in background
- **256MB memory**: Balanced for network-bound operations
- **7-day log retention**: Cost optimization
- **Target latencies**: ClientData 200-500ms, Retrieve 150-400ms, PostCall <50ms

## Testing Endpoints

### ClientData
```bash
curl -X POST <ClientDataApiUrl> \
  -H "Content-Type: application/json" \
  -H "X-Workspace-Key: <key>" \
  -d '{"caller_id": "+16129782029", "agent_id": "test", "called_number": "+18005551234", "call_sid": "test-123"}'

# Alternative field name (both supported)
curl -X POST <ClientDataApiUrl> \
  -H "Content-Type: application/json" \
  -H "X-Workspace-Key: <key>" \
  -d '{"system__caller_id": "+16129782029"}'
```

### Retrieve
```bash
curl -X POST <RetrieveApiUrl> \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the user preferences?", "user_id": "+16129782029"}'
```

### PostCall
```bash
curl -X POST <PostCallApiUrl> \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "conv-123", "transcript": [{"role": "user", "content": "Hello"}], "analysis": {"summary": "Test call"}, "metadata": {"caller_id": "+16129782029"}}'
```

## Common Issues

- **Lambda timeout**: Increase timeout in `template.yaml` (default 30s for sync, 60s for PostCall)
- **Mem0 connection issues**: Verify environment variables with `aws lambda get-function-configuration`
- **HMAC validation failing**: Ensure `ELEVENLABS_HMAC_KEY` matches ElevenLabs signing key
- **Cold start latency**: Consider adding Provisioned Concurrency for production

## References

### Internal Documentation
- [SPECIFICATION.md](./SPECIFICATION.md) - Complete technical specification with architecture details
- [README.md](./README.md) - Comprehensive deployment guide, monitoring, and troubleshooting
- [ELEVENLABS_SETUP_GUIDE.md](./ELEVENLABS_SETUP_GUIDE.md) - Step-by-step ElevenLabs integration
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Quick command reference
- [SYSTEM_FLOW.md](./SYSTEM_FLOW.md) - System flow diagrams
- [CHANGELOG.md](./CHANGELOG.md) - Version history and changes

### External Documentation
- [Mem0 Lambda FAQ](https://docs.mem0.ai/faqs#how-do-i-configure-mem0-for-aws-lambda)
- [Mem0 ElevenLabs Integration](https://docs.mem0.ai/integrations/elevenlabs)
- [ElevenLabs Post-Call Webhooks](https://elevenlabs.io/docs/agents-platform/workflows/post-call-webhooks)
