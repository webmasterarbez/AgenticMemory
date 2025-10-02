# AgenticMemory Copilot Instructions

## Big Picture Architecture

This is an **AWS SAM serverless backend** that bridges **ElevenLabs voice agents** with **Mem0 Cloud** for conversational memory. Three Lambda functions handle the complete memory lifecycle:

- **ClientData** (`src/client_data/handler.py`): Pre-call memory retrieval + personalized greeting generation (auth: workspace key)
- **Retrieve** (`src/retrieve/handler.py`): In-call semantic search (no auth - trusted agent connection) 
- **PostCall** (`src/post_call/handler.py`): Async memory storage (auth: HMAC signature)

**Critical architectural decisions:**
- Each function has its own HTTP API Gateway (eliminates routing latency)
- Shared Lambda layer (`layer/`) contains only `mem0ai` package
- Phone numbers serve as user IDs: `+16129782029` format
- Two memory types: factual (summaries) vs semantic (full transcripts)

## Key Patterns & Conventions

### Lambda Performance Pattern
**Always initialize Mem0 client OUTSIDE the handler** for connection reuse across invocations:
```python
from mem0 import MemoryClient
import os

# CRITICAL: Initialize outside handler - reused across warm starts
client = MemoryClient(
    api_key=os.environ['MEM0_API_KEY'],
    org_id=os.environ['MEM0_ORG_ID'], 
    project_id=os.environ['MEM0_PROJECT_ID']
)

def lambda_handler(event, context):
    # Use pre-initialized client here
```

### Memory Type System
Both types use `caller_id` (phone) as Mem0 `user_id`:

- **Factual** (`metadata.type = "factual"`): Call summaries + evaluation rationale
  ```python
  client.add(
      messages=[{'role': 'assistant', 'content': summary + evaluation}],
      user_id=caller_id,
      metadata={'type': 'factual', 'agent_id': ..., 'timestamp': ...}
  )
  ```

- **Semantic** (`metadata.type = "semantic"`): Full conversation transcript
  ```python
  client.add(
      messages=transcript,  # Full messages array
      user_id=caller_id,
      metadata={'type': 'semantic', 'agent_id': ..., 'timestamp': ...}
  )
  ```

### Personalized Greeting Generation (ClientData Only)
ClientData extracts caller names from memories using regex patterns and generates contextual greetings:

```python
# Extract name from memory strings
name = extract_caller_name(all_memories)  # Returns "Stefan" from "User name is Stefan"

# Generate greeting based on context
greeting = generate_personalized_greeting(
    caller_name=name,
    is_returning=len(memories) > 0,
    account_status="premium customer",  # Parsed from memories
    last_interaction="inquiry"
)
# Result: "Hello Stefan! I see you're a premium customer. How can I assist you?"
```

Greeting is returned in `conversation_config_override.agent.first_message`.

### Response Format Conventions

**ClientData** returns ElevenLabs-specific nested structure:
```python
{
    "type": "conversation_initiation_client_data",
    "dynamic_variables": {
        "caller_id": "+16129782029",
        "caller_name": "Stefan",  # Extracted via regex
        "memory_count": "5",
        "returning_caller": "yes"
    },
    "conversation_config_override": {
        "agent": {
            "prompt": {"prompt": "# Known Information...\n" + formatted_memories},
            "first_message": "Hello Stefan! ..."  # Generated greeting
        }
    }
}
```

**Retrieve** returns flat structure:
```python
{"memories": [...]}  # Top N from semantic search
```

**PostCall** returns immediate ack (async processing):
```python
# Return instantly to prevent webhook timeout
return {'statusCode': 200, 'body': json.dumps({'status': 'ok'})}
# Then process (errors logged but don't affect response)
```

## Authentication Patterns

### ClientData: Header-Based (Workspace Key)
```python
headers = event.get('headers', {})
# Case-insensitive header lookup
workspace_key = headers.get('x-workspace-key') or headers.get('X-Workspace-Key')
if workspace_key != WORKSPACE_KEY:
    return {'statusCode': 401, 'body': json.dumps({'error': 'Unauthorized'})}
```

### Retrieve: None (Trusted Agent Connection)
No auth validation - assumes secure agent-to-backend channel.

### PostCall: HMAC-SHA256 Signature
```python
# Header format: "t=1234567890,v0=abc123..."
# Signed payload: "{timestamp}.{raw_body}"
# Tolerance: 30 minutes
signature_header = headers.get('elevenlabs-signature') or headers.get('ElevenLabs-Signature')
if not verify_hmac_signature(raw_body, signature_header):
    return response  # Still returns 200 (async pattern)
```

See `verify_hmac_signature()` in `src/post_call/handler.py` for implementation details.

## Development Workflows

### Build & Deploy (Order Matters!)
```bash
# STEP 1: Build layer FIRST (all functions depend on it)
cd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..

# STEP 2: Build SAM application
sam build

# STEP 3: Deploy
sam deploy --guided  # First time - saves config to samconfig.toml
sam deploy           # Subsequent deploys use saved config
```

**Important**: After deploy, capture the three API URLs from outputs:
- `ClientDataApiUrl` (for ElevenLabs webhook config)
- `RetrieveApiUrl` (for agent tool config)
- `PostCallApiUrl` (for post-call webhook)

### Testing Patterns
Project uses integration tests (not unit tests). Each `test_*.py` directly hits deployed endpoints:

```bash
# Interactive tests (prompt for credentials)
python3 test_clientdata.py         # Tests workspace key auth
python3 test_personalized_greetings.py  # Tests name extraction + greeting gen
python3 test_postcall.py           # Tests HMAC signature validation

# Automated test (uses .env file)
python3 test_production_ready.py   # Comprehensive check of all 3 endpoints
```

**Test data**: Stefan (`+16129782029`) has existing memories. New numbers have none.

### Monitoring & Debugging
```bash
# Tail CloudWatch logs (7-day retention)
aws logs tail /aws/lambda/AgenticMemoriesClientData --follow
aws logs tail /aws/lambda/AgenticMemoriesRetrieve --follow
aws logs tail /aws/lambda/AgenticMemoriesPostCall --follow

# All logs include user_id/caller_id for filtering
```

### Environment Variables in SAM
Template uses CloudFormation parameters (NOT env vars directly). Secrets stored in `samconfig.toml`:

```yaml
# template.yaml defines Parameters, then maps to Environment.Variables
Parameters:
  Mem0ApiKey: {Type: String, NoEcho: true}

Environment:
  Variables:
    MEM0_API_KEY: !Ref Mem0ApiKey
    MEM0_DIR: /tmp/.mem0  # Lambda writable directory
```

All functions share: `MEM0_API_KEY`, `MEM0_ORG_ID`, `MEM0_PROJECT_ID`, `ELEVENLABS_WORKSPACE_KEY`, `ELEVENLABS_HMAC_KEY`

## Project Structure Insights

```
AgenticMemory/
├── layer/
│   └── requirements.txt          # ONLY mem0ai (shared by all functions)
├── src/
│   ├── client_data/handler.py    # 318 lines: auth, get_all(), name extraction, greeting
│   ├── retrieve/handler.py       # 94 lines: search() with limit
│   └── post_call/handler.py      # 187 lines: HMAC, async add() x2 memory types
├── requirements.txt              # Dev deps: pytest, boto3 (NOT deployed)
├── template.yaml                 # 227 lines: 3 functions, 3 APIs, 1 layer
└── test_*.py                     # Integration tests (hit real endpoints)
```

**Dependency separation**: Lambda layer has only `mem0ai`. Dev deps (pytest, boto3) in root `requirements.txt` are NOT packaged.

## Performance Optimizations

- **Reserved concurrency**: 10 per function (prevents cold start pileup)
- **Separate HTTP APIs**: Each function has own API Gateway (no shared routing)
- **Client reuse**: Mem0 client initialized at module level
- **Async PostCall**: Returns 200 in <50ms, processes memory storage afterward
- **7-day log retention**: CloudWatch cost optimization
- **Timeout tuning**: 30s for sync functions, 60s for PostCall

## Integration Points

### ElevenLabs Configuration
Three webhook/tool integrations required:

1. **Conversation Initiation webhook**: 
   - URL: ClientDataApiUrl from deployment
   - Method: POST
   - Headers: `X-Workspace-Key: wsec_...`
   - Payload: `{"caller_id": "..."}`

2. **Agent tool** (mid-call search):
   - URL: RetrieveApiUrl
   - Method: POST
   - Auth: None
   - Payload: `{"query": "...", "user_id": "{{caller_phone}}"}`

3. **Post-call webhook**:
   - URL: PostCallApiUrl
   - Method: POST
   - Auth: HMAC signature in `ElevenLabs-Signature` header
   - Payload: Full call data (transcript, analysis, metadata)

### Mem0 Cloud Operations
Three main API methods used:

```python
# ClientData: Get all memories for prompt context
memories = client.get_all(user_id=caller_id)  # Returns {"results": [...]}

# Retrieve: Semantic search during call
results = client.search(query="...", user_id=caller_id, limit=3)

# PostCall: Store new memories (called twice per call)
client.add(messages=[...], user_id=caller_id, metadata={...}, version="v2")
```

## Error Handling Strategy

**Sync functions** (ClientData/Retrieve): Return error status immediately
```python
try:
    # ... process
except Exception as e:
    logger.error(f"Error: {str(e)}", exc_info=True)
    return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
```

**Async function** (PostCall): Return 200 immediately, log errors internally
```python
response = {'statusCode': 200, 'body': json.dumps({'status': 'ok'})}
try:
    # ... process async
except Exception as e:
    logger.error(f"Error: {str(e)}", exc_info=True)  # Logged but doesn't throw
return response  # Always returns success
```

**Common issues**: Mem0 timeouts, missing auth headers, malformed ElevenLabs payloads. All logs include `caller_id`/`user_id` for debugging.

## Testing & Validation

### Integration Test Suite
Project uses **integration tests** (not unit tests) that hit real deployed endpoints:

```bash
# Interactive tests (prompt for credentials)
python3 test_clientdata.py              # Auth + memory retrieval + greeting
python3 test_personalized_greetings.py  # Name extraction patterns
python3 test_postcall.py                # HMAC signature validation
python3 test_hmac_auth.py               # HMAC edge cases

# Automated test (uses .env file)
python3 test_production_ready.py        # Comprehensive 3-endpoint check
```

### Test Data Conventions
- **Stefan** (`+16129782029`): Has existing memories (factual + semantic)
- **New numbers**: No memories (tests first-time caller flow)
- **Test payloads**: `elevenlabs_post_call_payload.json` contains real webhook structure

### Local Testing with SAM
```bash
# Invoke function locally with test event
sam local invoke AgenticMemoriesClientData -e events/client_data.json

# Start local API Gateway
sam local start-api  # Endpoints at http://localhost:3000
```

### Test File Organization
```
test_*.py                    # Root: Integration tests (hit deployed APIs)
tests/test_*.py              # tests/: Unit tests (mock Mem0 client)
elevenlabs_post_call_payload.json  # Real webhook payload for testing
```

## Environment Setup

### Local Development (.env file)
Create `.env` file for test scripts:

```bash
# API Endpoints (from sam deploy outputs)
ELEVENLABS_CLIENT_DATA_URL=https://abc123.execute-api.us-east-1.amazonaws.com/Prod/client-data
ELEVENLABS_POST_CALL_URL=https://def456.execute-api.us-east-1.amazonaws.com/Prod/post-call

# Credentials (same as SAM deployment)
ELEVENLABS_WORKSPACE_KEY=wsec_...
ELEVENLABS_HMAC_KEY=wsec_...
MEM0_API_KEY=m0-...
MEM0_ORG_ID=org_...
MEM0_PROJECT_ID=proj_...
```

**Usage in test scripts:**
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file
CLIENT_DATA_URL = os.getenv("ELEVENLABS_CLIENT_DATA_URL")
```

### SAM Configuration (samconfig.toml)
Secrets stored in `samconfig.toml` after first `sam deploy --guided`:

```toml
[default.deploy.parameters]
stack_name = "sam-app"
region = "us-east-1"
parameter_overrides = "Mem0ApiKey=... ElevenLabsWorkspaceKey=..."
```

**Critical**: `samconfig.toml` is gitignored (contains secrets). Each developer needs their own.

## Deployment Troubleshooting

### Common SAM Deploy Issues

**1. Layer Build Failures**
```bash
# Symptom: "Unable to import module 'handler': No module named 'mem0'"
# Cause: Lambda layer not built or built incorrectly
# Fix:
cd layer
rm -rf python  # Clean old build
mkdir -p python
pip install -r requirements.txt -t python/
cd .. && sam build
```

**2. Parameter Override Errors**
```bash
# Symptom: "Parameter validation failed: Missing required parameter"
# Cause: samconfig.toml missing or parameters not set
# Fix: Run sam deploy --guided again, answer all prompts
```

**3. IAM Permission Denied**
```bash
# Symptom: "User is not authorized to perform: cloudformation:CreateStack"
# Cause: AWS credentials lack necessary permissions
# Fix: Ensure AWS credentials have permissions for:
# - CloudFormation (CreateStack, UpdateStack)
# - Lambda (CreateFunction, UpdateFunctionCode)
# - API Gateway (CreateApi, CreateRoute)
# - IAM (CreateRole, AttachRolePolicy)
# - Logs (CreateLogGroup)
```

**4. S3 Bucket Errors**
```bash
# Symptom: "Unable to upload artifact... S3 Bucket does not exist"
# Cause: No S3 bucket for SAM deployment artifacts
# Fix: Use --guided flag or add --resolve-s3 flag:
sam deploy --resolve-s3  # Auto-creates S3 bucket
```

**5. Stack Rollback**
```bash
# Symptom: "Stack sam-app is in ROLLBACK_COMPLETE state"
# Cause: Previous deployment failed and left stack in bad state
# Fix: Delete and redeploy
aws cloudformation delete-stack --stack-name sam-app
# Wait ~2 min for deletion, then:
sam build && sam deploy --guided
```

**6. API Gateway URL Not in Outputs**
```bash
# Symptom: Deployment succeeds but no URLs shown
# Cause: Terminal output scrolled past or deployment logs not visible
# Fix: Query CloudFormation stack outputs:
aws cloudformation describe-stacks \
  --stack-name sam-app \
  --query 'Stacks[0].Outputs'
```

### Runtime Troubleshooting

**Lambda Timeout Errors (502 Bad Gateway)**
```yaml
# template.yaml - increase timeout for specific function
AgenticMemoriesClientData:
  Properties:
    Timeout: 60  # Up from 30 seconds
```

**Mem0 Connection Issues**
```bash
# Verify environment variables are set correctly
aws lambda get-function-configuration \
  --function-name AgenticMemoriesClientData \
  --query 'Environment.Variables'

# Test Mem0 connectivity directly
python3 test_memory_direct.py
```

**HMAC Validation Failures**
```python
# Check PostCall logs for signature details
aws logs tail /aws/lambda/AgenticMemoriesPostCall --follow

# Common causes:
# 1. ELEVENLABS_HMAC_KEY mismatch with ElevenLabs settings
# 2. Timestamp drift >30 minutes (check server time)
# 3. Body modification (ensure raw body is used for signature)
```

**Cold Start Latency (3-5 seconds)**
```yaml
# Add reserved concurrency to keep instances warm
AgenticMemoriesClientData:
  Properties:
    ReservedConcurrentExecutions: 10  # Already set in template
    ProvisionedConcurrencyConfig:      # Add this for sub-100ms
      ProvisionedConcurrencyEnabled: true
      ProvisionedConcurrency: 2        # Costs ~$12/month per instance
```

### Debugging Workflow
```bash
# 1. Check stack status
aws cloudformation describe-stacks --stack-name sam-app

# 2. Check Lambda function status
aws lambda list-functions \
  --query 'Functions[?contains(FunctionName, `AgenticMemories`)].{Name:FunctionName,State:State,LastModified:LastModified}'

# 3. Tail logs during test
aws logs tail /aws/lambda/AgenticMemoriesClientData --follow &
python3 test_clientdata.py

# 4. Query recent errors
aws logs filter-pattern /aws/lambda/AgenticMemoriesClientData \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000

# 5. Test endpoints manually
curl -X POST <ClientDataApiUrl> \
  -H "X-Workspace-Key: wsec_..." \
  -H "Content-Type: application/json" \
  -d '{"caller_id": "+16129782029"}' \
  -v  # Verbose output shows headers/status
```

### Performance Monitoring
```bash
# Get function metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=AgenticMemoriesClientData \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum

# Check concurrent executions
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name ConcurrentExecutions \
  --dimensions Name=FunctionName,Value=AgenticMemoriesClientData \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Maximum
```

## Additional Resources

### Internal Documentation
- **SPECIFICATION.md**: Complete technical spec (627 lines) with detailed architecture
- **CLAUDE.md**: Extended development guide (323 lines) with all commands
- **SYSTEM_FLOW.md**: Visual flow diagrams showing call lifecycle
- **ELEVENLABS_SETUP_GUIDE.md**: Step-by-step ElevenLabs integration
- **QUICK_REFERENCE.md**: Quick command reference card
- **README.md**: Comprehensive deployment + monitoring guide (721 lines)

### External References
- [Mem0 Lambda FAQ](https://docs.mem0.ai/faqs#how-do-i-configure-mem0-for-aws-lambda): Lambda-specific configuration
- [Mem0 ElevenLabs Integration](https://docs.mem0.ai/integrations/elevenlabs): Official integration docs
- [ElevenLabs Post-Call Webhooks](https://elevenlabs.io/docs/agents-platform/workflows/post-call-webhooks): Webhook payload format
- [AWS SAM Developer Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/): SAM CLI reference