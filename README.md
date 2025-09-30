# AgenticMemories

AWS Serverless backend for ElevenLabs Agents with Mem0 Cloud integration for long-term memory management.

## Overview

This system provides three webhook endpoints for ElevenLabs agents:

1. **ClientData**: Returns personalized memory data when a call is initiated
2. **Retrieve**: Semantic search for memories during active calls
3. **PostCall**: Stores conversation memories after call completion

**Performance**: Optimized for <500ms latency with 10 concurrent calls.

## Architecture

- **3 Lambda Functions** (Python 3.12, 256MB)
- **3 HTTP API Gateways** (separate for minimal latency)
- **1 Lambda Layer** (mem0ai package)
- **CloudWatch Logs** (7-day retention)

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **SAM CLI** installed ([Installation Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))
3. **Python 3.12** installed
4. **Mem0 Account** with:
   - API Key
   - Organization ID
   - Project ID
5. **ElevenLabs Account** with:
   - Workspace Secret Key
   - HMAC Signing Key

## Project Structure

```
AgenticMemory/
├── SPECIFICATION.md           # Complete system specification
├── README.md                  # This file
├── template.yaml              # SAM CloudFormation template
├── requirements.txt           # Development dependencies
├── .gitignore                 # Git ignore rules
├── layer/
│   └── requirements.txt       # Lambda layer dependencies (mem0ai)
└── src/
    ├── client_data/
    │   └── handler.py         # ClientData Lambda
    ├── retrieve/
    │   └── handler.py         # Retrieve Lambda
    └── post_call/
        └── handler.py         # PostCall Lambda
```

## Deployment

### Step 1: Build the Lambda Layer

```bash
cd layer
mkdir -p python
pip install -r requirements.txt -t python/
cd ..
```

### Step 2: Build the SAM Application

```bash
sam build
```

### Step 3: Deploy to AWS

#### Option A: Guided Deployment (First Time)

```bash
sam deploy --guided
```

You'll be prompted for:
- Stack Name: `AgenticMemoriesStack`
- AWS Region: `us-east-1`
- Parameters:
  - Mem0ApiKey: `<your-mem0-api-key>`
  - Mem0OrgId: `<your-mem0-org-id>`
  - Mem0ProjectId: `<your-mem0-project-id>`
  - ElevenLabsWorkspaceKey: `<your-workspace-secret>`
  - ElevenLabsHmacKey: `<your-hmac-signing-key>`
- Confirm changes before deploy: `Y`
- Allow SAM CLI IAM role creation: `Y`
- Save arguments to configuration file: `Y`

#### Option B: Direct Deployment (With Parameters)

```bash
sam deploy \
  --stack-name AgenticMemoriesStack \
  --region us-east-1 \
  --parameter-overrides \
    Mem0ApiKey=<your-key> \
    Mem0OrgId=<your-org> \
    Mem0ProjectId=<your-project> \
    ElevenLabsWorkspaceKey=<workspace-key> \
    ElevenLabsHmacKey=<hmac-key> \
  --capabilities CAPABILITY_NAMED_IAM \
  --resolve-s3
```

### Step 4: Get API Endpoints

After deployment, SAM outputs three URLs:

```
Outputs:
  ClientDataApiUrl: https://xxx.execute-api.us-east-1.amazonaws.com/Prod/client-data
  RetrieveApiUrl: https://xxx.execute-api.us-east-1.amazonaws.com/Prod/retrieve
  PostCallApiUrl: https://xxx.execute-api.us-east-1.amazonaws.com/Prod/post-call
```

## ElevenLabs Configuration

### 1. Conversation Initiation Webhook

Configure in ElevenLabs Agent settings:
- **URL**: `ClientDataApiUrl` from deployment outputs
- **Header**: `X-Workspace-Key: <your-workspace-key>`

### 2. Agent Tool (In-Call Retrieval)

Add as a custom tool in ElevenLabs:
- **URL**: `RetrieveApiUrl` from deployment outputs
- **Method**: POST
- **Request Body**:
  ```json
  {
    "query": "{{query}}",
    "user_id": "{{caller_id}}"
  }
  ```

### 3. Post-Call Webhook

Configure in ElevenLabs:
- **URL**: `PostCallApiUrl` from deployment outputs
- **Authentication**: HMAC signature (automatically handled by ElevenLabs)

## Testing

### Test ClientData Endpoint

```bash
curl -X POST <ClientDataApiUrl> \
  -H "Content-Type: application/json" \
  -H "X-Workspace-Key: <your-workspace-key>" \
  -d '{
    "caller_id": "+16129782029",
    "agent_id": "test-agent",
    "called_number": "+18005551234",
    "call_sid": "test-call-123"
  }'
```

### Test Retrieve Endpoint

```bash
curl -X POST <RetrieveApiUrl> \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the user preferences?",
    "user_id": "+16129782029"
  }'
```

### Test PostCall Endpoint

```bash
curl -X POST <PostCallApiUrl> \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv-123",
    "agent_id": "agent-123",
    "call_duration": 120,
    "transcript": [
      {"role": "user", "content": "Hello"},
      {"role": "assistant", "content": "Hi there"}
    ],
    "analysis": {
      "summary": "Customer greeted the agent"
    },
    "metadata": {
      "caller_id": "+16129782029"
    }
  }'
```

## Monitoring

### CloudWatch Logs

View logs for each Lambda:

```bash
# ClientData logs
aws logs tail /aws/lambda/AgenticMemoriesClientData --follow

# Retrieve logs
aws logs tail /aws/lambda/AgenticMemoriesRetrieve --follow

# PostCall logs
aws logs tail /aws/lambda/AgenticMemoriesPostCall --follow
```

### CloudWatch Metrics

Monitor in AWS Console:
- Lambda invocations, errors, duration
- API Gateway 4xx/5xx errors, latency

## Updating the Stack

After making code changes:

```bash
sam build
sam deploy
```

## Deleting the Stack

To remove all resources:

```bash
aws cloudformation delete-stack --stack-name AgenticMemoriesStack
```

## Environment Variables

All Lambdas use these environment variables (configured in template.yaml):

| Variable | Description | Default |
|----------|-------------|---------|
| `MEM0_API_KEY` | Mem0 API key | Required |
| `MEM0_ORG_ID` | Mem0 organization ID | Required |
| `MEM0_PROJECT_ID` | Mem0 project ID | Required |
| `MEM0_DIR` | Directory for Mem0 cache | `/tmp/.mem0` |
| `MEM0_SEARCH_LIMIT` | Max results for semantic search | `3` |
| `MEM0_TIMEOUT` | Timeout in seconds | `5` |
| `ELEVENLABS_WORKSPACE_KEY` | Workspace secret for auth | Required |
| `ELEVENLABS_HMAC_KEY` | HMAC signing key | Required |

## Cost Estimate

For 10 concurrent calls, ~10k invocations/month:

- Lambda: ~$5-10
- HTTP API: ~$1-2
- CloudWatch Logs: ~$1

**Total**: ~$7-13/month

## Troubleshooting

### Lambda Timeout

If requests timeout, increase timeout in `template.yaml`:
```yaml
Timeout: 30  # Increase to 45 or 60
```

### Mem0 Connection Issues

Verify environment variables are set correctly:
```bash
aws lambda get-function-configuration --function-name AgenticMemoriesClientData
```

### HMAC Validation Failing

Ensure `ELEVENLABS_HMAC_KEY` matches the signing key in ElevenLabs settings.

### Cold Start Latency

For production, consider adding Provisioned Concurrency in `template.yaml`.

## Development

### Local Testing with SAM

```bash
# Invoke locally
sam local invoke AgenticMemoriesClientData -e events/client_data.json

# Start API locally
sam local start-api
```

### Running Tests

```bash
pip install -r requirements.txt
pytest tests/
```

## Security Notes

1. **Secrets**: All sensitive values are marked `NoEcho: true` in template
2. **HTTPS**: All API endpoints enforce HTTPS
3. **Authentication**:
   - ClientData uses workspace key validation
   - PostCall uses HMAC signature verification
4. **IAM**: Lambda role has minimal permissions (CloudWatch Logs only)

## Next Steps (Phase 2)

- Add provisioned concurrency for sub-100ms cold starts
- Implement DLQ for PostCall processing
- Add API keys for Retrieve endpoint
- Set up CloudWatch alarms
- Add X-Ray tracing for debugging
- Implement memory versioning/TTL

## References

- [Complete Specification](./SPECIFICATION.md)
- [Mem0 Documentation](https://docs.mem0.ai/)
- [ElevenLabs Agent Docs](https://elevenlabs.io/docs/agents-platform)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)

## License

MIT

## Support

For issues or questions, please refer to the [SPECIFICATION.md](./SPECIFICATION.md) document.