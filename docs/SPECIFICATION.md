# AgenticMemories System Specification

## Project Overview
AWS Serverless backend for ElevenLabs Agents with Mem0 Cloud integration for long-term memory management. Optimized for <500ms latency supporting 10 concurrent calls.

**Stack Name**: `AgenticMemoriesStack`
**Region**: `us-east-1`
**Framework**: AWS SAM
**Runtime**: Python 3.12

---

## Architecture

```
ElevenLabs Agent
    |
    ├─> [Conversation Initiation] -> AgenticMemoriesClientDataHttpApi -> AgenticMemoriesClientData (sync)
    |                                                                      └─> Mem0 Cloud (get all memories)
    |
    ├─> [In-Call Tool]           -> AgenticMemoriesRetrieveHttpApi     -> AgenticMemoriesRetrieve (sync)
    |                                                                      └─> Mem0 Cloud (semantic search)
    |
    └─> [Post-Call Webhook]      -> AgenticMemoriesPostCallHttpApi     -> AgenticMemoriesPostCall (async)
                                                                           └─> Mem0 Cloud (store memories)
```

---

## Components

### 1. Lambda Functions

#### Common Configuration
- **Runtime**: Python 3.12
- **Memory**: 256MB
- **Timeout**: 30 seconds (ClientData & Retrieve), 60 seconds (PostCall)
- **Architecture**: x86_64
- **Layer**: AgenticMemoriesLambdaLayer (contains mem0ai package)

#### AgenticMemoriesClientData (Synchronous)
**Purpose**: Return personalized data for call initiation

**Trigger**: HTTP API POST request from ElevenLabs Conversation Initiation webhook

**Authentication**: Header validation using `ELEVENLABS_WORKSPACE_KEY`

**Input**:
```json
{
  "caller_id": "+16129782029",
  "agent_id": "...",
  "called_number": "...",
  "call_sid": "..."
}
```

**Process**:
1. Validate `ELEVENLABS_WORKSPACE_KEY` in request headers
2. Extract `caller_id` from payload
3. Use `caller_id` as Mem0 `user_id`
4. Retrieve ALL memories for user: `client.get_all(user_id=caller_id)`
5. Return memories to ElevenLabs

**Output**:
```json
{
  "user_id": "+16129782029",
  "memories": [
    {
      "id": "mem-uuid",
      "memory": "User prefers morning calls",
      "metadata": {...}
    }
  ]
}
```

**Error Handling**: Log errors, return 500 with error message

---

#### AgenticMemoriesRetrieve (Synchronous)
**Purpose**: Semantic search during active call

**Trigger**: HTTP API POST from ElevenLabs agent tool

**Authentication**: None (agent-to-backend trusted connection)

**Input**:
```json
{
  "query": "What are the user's payment preferences?",
  "user_id": "+16129782029"
}
```

**Process**:
1. Extract `query` and `user_id`
2. Semantic search: `client.search(query, user_id=user_id, limit=MEM0_SEARCH_LIMIT)`
3. Set timeout: `MEM0_TIMEOUT` seconds
4. Return top N relevant memories

**Output**:
```json
{
  "memories": [
    {
      "id": "mem-uuid",
      "memory": "User prefers credit card payments",
      "score": 0.95
    }
  ]
}
```

**Error Handling**: Log errors, return 500 with error message

---

#### AgenticMemoriesPostCall (Asynchronous)
**Purpose**: Store conversation memories after call completion

**Trigger**: HTTP API POST from ElevenLabs Post-Call webhook

**Authentication**: HMAC signature validation using `ELEVENLABS_HMAC_KEY`

**Input** (example payload from ElevenLabs):
```json
{
  "conversation_id": "...",
  "agent_id": "...",
  "call_duration": 120,
  "transcript": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "analysis": {
    "summary": "Customer inquired about pricing...",
    "evaluation": {...}
  },
  "metadata": {
    "caller_id": "+16129782029"
  }
}
```

**Process**:
1. Return `200 OK` immediately
2. Validate HMAC signature
3. Extract: `caller_id`, `transcript`, `analysis`, metadata
4. Store **Factual Memory**:
   ```python
   client.add(
       messages=[{"role": "assistant", "content": analysis['summary'] + evaluation_rationale}],
       user_id=caller_id,
       metadata={
           "type": "factual",
           "agent_id": agent_id,
           "conversation_id": conversation_id,
           "call_duration": call_duration,
           "timestamp": ...
       }
   )
   ```
5. Store **Semantic Memory**:
   ```python
   client.add(
       messages=transcript,  # Full chat messages
       user_id=caller_id,
       metadata={
           "type": "semantic",
           "agent_id": agent_id,
           "conversation_id": conversation_id,
           "call_duration": call_duration,
           "timestamp": ...
       }
   )
   ```

**Output**:
```json
{"status": "ok"}
```

**Error Handling**: Log all errors, do not throw exceptions

---

### 2. HTTP API Gateways

#### AgenticMemoriesClientDataHttpApi
- **Type**: HTTP API (not REST API)
- **Route**: `POST /client-data`
- **Integration**: Lambda Proxy
- **CORS**: Enabled
- **Throttling**: Default AWS limits

#### AgenticMemoriesRetrieveHttpApi
- **Type**: HTTP API
- **Route**: `POST /retrieve`
- **Integration**: Lambda Proxy
- **CORS**: Enabled
- **Throttling**: Default AWS limits

#### AgenticMemoriesPostCallHttpApi
- **Type**: HTTP API
- **Route**: `POST /post-call`
- **Integration**: Lambda Proxy
- **CORS**: Enabled
- **Throttling**: Default AWS limits

---

### 3. Lambda Layer

#### AgenticMemoriesLambdaLayer
**Contents**:
- `mem0ai` Python package (installed via pip)
- Compatible with Python 3.12

**Build Process**:
```bash
mkdir -p layer/python
pip install mem0ai -t layer/python/
cd layer && zip -r layer.zip python/
```

---

### 4. IAM Role

#### AgenticMemoriesLambdaRole
**Permissions**:
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`

**Trust Policy**: Lambda service

---

### 5. CloudWatch Log Groups
- `/aws/lambda/AgenticMemoriesClientData` (7-day retention)
- `/aws/lambda/AgenticMemoriesRetrieve` (7-day retention)
- `/aws/lambda/AgenticMemoriesPostCall` (7-day retention)

---

## Environment Variables

All Lambda functions share these environment variables:

```bash
# Mem0 Configuration (required)
MEM0_API_KEY=<your-mem0-api-key>
MEM0_ORG_ID=<your-mem0-org-id>
MEM0_PROJECT_ID=<your-mem0-project-id>
MEM0_DIR=/tmp/.mem0

# Performance Tuning
MEM0_SEARCH_LIMIT=3        # Number of results for semantic search
MEM0_TIMEOUT=5             # Seconds before timeout

# ElevenLabs Authentication
ELEVENLABS_WORKSPACE_KEY=<workspace-secret>   # For ClientData webhook
ELEVENLABS_HMAC_KEY=<signing-key>             # For PostCall webhook HMAC
```

---

## Mem0 Integration Details

### Client Initialization (Lambda Best Practice)
Per [Mem0 Lambda FAQ](https://docs.mem0.ai/faqs#how-do-i-configure-mem0-for-aws-lambda):

```python
from mem0 import MemoryClient
import os

# Initialize OUTSIDE handler for reuse across invocations
client = MemoryClient(
    api_key=os.environ['MEM0_API_KEY'],
    org_id=os.environ['MEM0_ORG_ID'],
    project_id=os.environ['MEM0_PROJECT_ID']
)

def lambda_handler(event, context):
    # Use client here
    memories = client.get_all(user_id="...")
```

### User ID Strategy
- **user_id**: Phone number (e.g., `+16129782029`)
- Auto-creates new Mem0 user on first interaction
- All memories linked to phone number

### Memory Types
1. **Factual Memory**: Stored knowledge, preferences, domain info
2. **Semantic Memory**: Full conversation context for relationship understanding

---

## API Contracts

### ClientData Endpoint
**URL**: `https://<api-id>.execute-api.us-east-1.amazonaws.com/client-data`

**Request**:
```http
POST /client-data
Content-Type: application/json
X-Workspace-Key: <ELEVENLABS_WORKSPACE_KEY>

{
  "caller_id": "+16129782029",
  "agent_id": "agent-123",
  "called_number": "+18005551234",
  "call_sid": "call-abc"
}
```

**Response** (200 OK):
```json
{
  "user_id": "+16129782029",
  "memories": [...]
}
```

---

### Retrieve Endpoint
**URL**: `https://<api-id>.execute-api.us-east-1.amazonaws.com/retrieve`

**Request**:
```http
POST /retrieve
Content-Type: application/json

{
  "query": "payment preferences",
  "user_id": "+16129782029"
}
```

**Response** (200 OK):
```json
{
  "memories": [
    {
      "id": "...",
      "memory": "...",
      "score": 0.95
    }
  ]
}
```

---

### PostCall Endpoint
**URL**: `https://<api-id>.execute-api.us-east-1.amazonaws.com/post-call`

**Request**:
```http
POST /post-call
Content-Type: application/json
X-ElevenLabs-Signature: <hmac-signature>

{
  "conversation_id": "...",
  "transcript": [...],
  "analysis": {...},
  "metadata": {"caller_id": "+16129782029"}
}
```

**Response** (200 OK - immediate):
```json
{"status": "ok"}
```

---

## Security

### Authentication Methods

1. **ClientData Webhook**: Header-based authentication
   - Validate `X-Workspace-Key` header matches `ELEVENLABS_WORKSPACE_KEY`

2. **Retrieve Tool**: None (trusted agent-backend connection)
   - Consider adding API key in production phase

3. **PostCall Webhook**: HMAC signature validation
   - Validate `X-ElevenLabs-Signature` using `ELEVENLABS_HMAC_KEY`
   - Follow [ElevenLabs HMAC documentation](https://elevenlabs.io/docs/agents-platform/workflows/post-call-webhooks#authentication)

### HTTPS Only
All API Gateway endpoints enforce HTTPS

---

## Cost Optimization Strategy

1. **HTTP API** (vs REST API): ~70% cheaper
2. **256MB memory**: Balanced cost/performance
3. **Lambda Layer**: Reduces deployment package size
4. **7-day log retention**: Minimizes CloudWatch storage costs
5. **No provisioned concurrency**: Pay only for actual invocations
6. **No DLQ/SQS**: Simplified error handling for prototype
7. **Raw JSON responses**: No compression overhead

**Estimated Monthly Cost** (100 concurrent calls, 10k invocations/month):
- Lambda: ~$5-10
- HTTP API: ~$1-2
- CloudWatch Logs: ~$1
- **Total**: ~$7-13/month

---

## Performance Optimization Strategy

1. **Separate HTTP APIs**: Eliminates routing overhead
2. **Mem0 client outside handler**: Reused across invocations
3. **`/tmp/.mem0` directory**: SDK cache for faster operations
4. **Configurable search limits**: Trade-off between context and latency
5. **Timeout protection**: Fail-fast if Mem0 is slow
6. **256MB memory**: Sufficient CPU for network-bound operations
7. **Async PostCall processing**: No blocking on storage operations

**Expected Latencies**:
- ClientData: 200-500ms (get_all + network)
- Retrieve: 150-400ms (semantic search + network)
- PostCall: <50ms (immediate return)

---

## Deployment

### Prerequisites
1. AWS CLI configured with credentials
2. SAM CLI installed
3. Mem0 account with API key, org_id, project_id
4. ElevenLabs workspace key and HMAC signing key

### Build Lambda Layer
```bash
mkdir -p layer/python
pip install mem0ai -t layer/python/
```

### Deploy Stack
```bash
sam build
sam deploy \
  --stack-name AgenticMemoriesStack \
  --region us-east-1 \
  --parameter-overrides \
    Mem0ApiKey=<key> \
    Mem0OrgId=<org> \
    Mem0ProjectId=<project> \
    ElevenLabsWorkspaceKey=<workspace-key> \
    ElevenLabsHmacKey=<hmac-key> \
  --capabilities CAPABILITY_IAM
```

### Outputs
After deployment, SAM will output:
- `ClientDataApiUrl`: Configure in ElevenLabs Conversation Initiation webhook
- `RetrieveApiUrl`: Configure as ElevenLabs agent tool endpoint
- `PostCallApiUrl`: Configure in ElevenLabs Post-Call webhook

---

## Testing

### Unit Tests
```bash
pytest tests/unit/
```

### Integration Tests
```bash
# Test ClientData
curl -X POST <ClientDataApiUrl> \
  -H "Content-Type: application/json" \
  -H "X-Workspace-Key: <key>" \
  -d '{"caller_id": "+16129782029"}'

# Test Retrieve
curl -X POST <RetrieveApiUrl> \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "user_id": "+16129782029"}'

# Test PostCall
curl -X POST <PostCallApiUrl> \
  -H "Content-Type: application/json" \
  -d '{"metadata": {"caller_id": "+16129782029"}, "transcript": []}'
```

### Load Testing
```bash
# Use artillery or locust to simulate 100 concurrent calls
artillery quick --count 100 --num 10 <RetrieveApiUrl>
```

---

## Error Handling

### ClientData & Retrieve (Synchronous)
- Log error with full context
- Return 500 with error message
- ElevenLabs will see the error

### PostCall (Asynchronous)
- Return 200 OK immediately
- Log all processing errors
- Continue execution (don't throw)
- No retry mechanism (ElevenLabs may retry on their side)

### Common Error Scenarios
1. **Mem0 timeout**: Log and return error after `MEM0_TIMEOUT` seconds
2. **Invalid authentication**: Log and return 401
3. **Missing required fields**: Log and return 400
4. **Mem0 API error**: Log and return 502

---

## Monitoring

### CloudWatch Metrics
- Lambda invocations
- Lambda errors
- Lambda duration
- API Gateway 4xx/5xx errors
- API Gateway latency

### CloudWatch Logs
All errors logged with structured format:
```json
{
  "level": "ERROR",
  "function": "AgenticMemoriesRetrieve",
  "error": "Mem0 timeout",
  "user_id": "+16129782029",
  "duration_ms": 5000
}
```

### Alarms (Future Phase)
- Lambda error rate > 5%
- API Gateway latency > 500ms (p99)
- Lambda concurrent executions > 80

---

## Future Enhancements (Phase 2+)

1. **Performance**:
   - Provisioned concurrency for sub-100ms cold starts
   - Response caching (ElastiCache/DAX)
   - Connection pooling

2. **Reliability**:
   - DLQ for PostCall processing
   - Retry logic with exponential backoff
   - Circuit breakers

3. **Security**:
   - API keys for Retrieve endpoint
   - Rate limiting per user_id
   - Secrets Manager for credentials

4. **Observability**:
   - X-Ray tracing
   - Custom CloudWatch metrics
   - Real-time dashboards

5. **Features**:
   - Memory versioning
   - Memory expiration/TTL
   - Multi-agent support
   - Memory analytics

---

## File Structure

```
AgenticMemory/
├── SPECIFICATION.md           # This file
├── template.yaml              # SAM template
├── requirements.txt           # Python dependencies
├── layer/
│   └── python/                # Lambda layer contents
│       └── mem0ai/
├── src/
│   ├── client_data/
│   │   └── handler.py         # AgenticMemoriesClientData
│   ├── retrieve/
│   │   └── handler.py         # AgenticMemoriesRetrieve
│   └── post_call/
│       └── handler.py         # AgenticMemoriesPostCall
├── tests/
│   ├── unit/
│   └── integration/
└── README.md                  # Deployment instructions
```

---

## References

- [Mem0 Lambda Configuration](https://docs.mem0.ai/faqs#how-do-i-configure-mem0-for-aws-lambda)
- [Mem0 ElevenLabs Integration](https://docs.mem0.ai/integrations/elevenlabs)
- [Mem0 API Reference](https://docs.mem0.ai/api-reference/memory/add-memories)
- [ElevenLabs Post-Call Webhooks](https://elevenlabs.io/docs/agents-platform/workflows/post-call-webhooks)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)

---

**Document Version**: 1.0
**Last Updated**: 2025-09-30
**Status**: Ready for Implementation