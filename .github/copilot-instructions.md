# AgenticMemory Copilot Instructions

## Big Picture Architecture

This is an **AWS SAM serverless backend** that bridges **ElevenLabs voice agents** with **Mem0 Cloud** for conversational memory. Three Lambda functions handle the complete memory lifecycle:

- **ClientData**: Pre-call memory retrieval (auth: workspace key)
- **Retrieve**: In-call semantic search (no auth - trusted agent connection) 
- **PostCall**: Async memory storage (auth: HMAC signature)

**Critical**: Each function has its own HTTP API Gateway for minimal latency. All use shared Lambda layer containing `mem0ai`.

## Key Patterns & Conventions

### Memory Client Initialization
**Always initialize Mem0 client OUTSIDE the handler** for reuse across invocations:
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
```

### Memory Type Distinction
- **Factual Memory**: Stored knowledge, preferences (`metadata.type = "factual"`)
- **Semantic Memory**: Full conversation context (`metadata.type = "semantic"`)

Both use `caller_id` (phone number like `+16129782029`) as Mem0 `user_id`.

### Response Patterns

**ClientData** returns ElevenLabs-specific format with prompt override:
```python
{
    "type": "conversation_initiation_client_data",
    "dynamic_variables": {"caller_id": "...", "memory_count": "..."},
    "conversation_config_override": {
        "agent": {"prompt": {"prompt": memory_context}}
    }
}
```

**Retrieve** returns simple memory array:
```python
{"memories": [...]}
```

**PostCall** returns immediate `200 OK`, processes asynchronously.

## Authentication Patterns

### ClientData (Workspace Key)
```python
headers = event.get('headers', {})
workspace_key = headers.get('x-workspace-key') or headers.get('X-Workspace-Key')
if workspace_key != WORKSPACE_KEY:
    return {'statusCode': 401, ...}
```

### PostCall (HMAC Validation)
Complex HMAC signature verification with timestamp tolerance. See `verify_hmac_signature()` in `post_call/handler.py`.

## Development Workflows

### Build & Deploy
```bash
# Build layer first (required step)
cd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..

# Build and deploy
sam build
sam deploy --guided  # First time
sam deploy           # Subsequent deployments
```

### Testing Endpoints
All three endpoints require different request formats:
- ClientData: needs `X-Workspace-Key` header + `caller_id` in body
- Retrieve: needs `query` + `user_id` in body
- PostCall: needs proper HMAC signature + full ElevenLabs payload

### Environment Variables
SAM template uses CloudFormation parameters for secrets. All Lambdas share:
```yaml
MEM0_API_KEY, MEM0_ORG_ID, MEM0_PROJECT_ID, MEM0_DIR=/tmp/.mem0
ELEVENLABS_WORKSPACE_KEY, ELEVENLABS_HMAC_KEY
MEM0_SEARCH_LIMIT=3, MEM0_TIMEOUT=5
```

## Project Structure Insights

```
src/
├── client_data/handler.py    # Pre-call: auth + get_all() + prompt formatting
├── retrieve/handler.py       # In-call: search() with limit
└── post_call/handler.py      # Post-call: HMAC + async add() for 2 memory types
```

**Layer separation**: `layer/requirements.txt` only contains `mem0ai`. Main `requirements.txt` has dev dependencies (`pytest`, `boto3`).

## Performance Optimizations

- **Reserved concurrency**: 10 per function (set in template.yaml)
- **Separate HTTP APIs**: Eliminates routing overhead
- **Client reuse**: Mem0 client initialized outside handler
- **Async PostCall**: Returns 200 immediately, processes in background
- **7-day log retention**: Cost optimization

## Integration Points

### ElevenLabs Configuration
1. **Conversation Initiation webhook** → ClientData URL + workspace key header
2. **Agent tool** → Retrieve URL (POST with query/user_id JSON)
3. **Post-call webhook** → PostCall URL + HMAC signing

### Mem0 Cloud Operations
- `client.get_all(user_id=caller_id)` - retrieve all memories
- `client.search(query, user_id, limit)` - semantic search
- `client.add(messages, user_id, metadata)` - store new memories

## Error Handling Strategy

**Sync functions** (ClientData/Retrieve): Log error + return 500 with message
**Async function** (PostCall): Return 200 immediately, log all processing errors but don't throw

**Common issues**: Mem0 timeouts, missing auth headers, malformed payloads. All errors include user_id context for debugging.