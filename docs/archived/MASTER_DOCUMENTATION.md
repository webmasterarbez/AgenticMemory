# AgenticMemory - Complete Project Documentation

## Project Overview

**AgenticMemory** is an AWS SAM serverless backend that bridges ElevenLabs voice agents with Mem0 Cloud for conversational memory. The system enables voice agents to remember previous conversations and provide personalized interactions.

### Architecture
- **3 Lambda Functions** with separate API Gateways for optimal performance
- **Mem0 Cloud Integration** for memory storage and retrieval  
- **ElevenLabs Integration** via webhooks and tools
- **S3 Storage** for backup and extended storage
- **CloudWatch Logging** for monitoring and debugging

---

## System Components

### 1. ClientData Function (`src/client_data/handler.py`)
**Purpose**: Pre-call memory retrieval + personalized greeting generation

**Authentication**: ElevenLabs Secrets Manager
- Configure secrets in [ElevenLabs Settings](https://elevenlabs.io/app/agents/settings)
- Add `WORKSPACE_KEY` secret with value: `wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70`
- Map secret to header: `X-Workspace-Key`
- **⚠️ CRITICAL**: Must use ElevenLabs secrets manager - direct headers don't work

**Endpoint**: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`

**Request Format**:
```json
{
  "caller_id": "+16129782029",
  "agent_id": "agent_xxx"
}
```

**Response Format**:
```json
{
  "type": "conversation_initiation_client_data",
  "dynamic_variables": {
    "caller_id": "+16129782029",
    "memory_count": "4",
    "memory_summary": "User wants to update email address",
    "returning_caller": "yes",
    "caller_name": "Stefan"
  },
  "conversation_config_override": {
    "agent": {
      "prompt": {"prompt": "CALLER CONTEXT: This caller has 4 previous interactions..."},
      "first_message": "Hello Stefan! I know you prefer email updates. How can I assist you today?"
    }
  }
}
```

### 2. PostCall Function (`src/post_call/handler.py`)
**Purpose**: Async memory storage after call completion

**Authentication**: HMAC-SHA256 Signature
- **Reference**: https://elevenlabs.io/docs/agents-platform/workflows/post-call-webhooks#authentication
- **HMAC Key**: `wsec_a8dc8b6e25ec3ddf11d7e651c40a5cb4931c2ca39d161fa4c94139f12f3ba9d3`
- **Header**: `ElevenLabs-Signature` with format `t=timestamp,v0=signature`
- **Signed Payload**: `{timestamp}.{raw_body}`
- **Tolerance**: 30 minutes
- **⚠️ CRITICAL**: Always returns 200 OK (async processing pattern)

**Endpoint**: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`

**Processing**: Stores both factual summaries and semantic transcripts to Mem0

### 3. Retrieve Function (`src/retrieve/handler.py`)  
**Purpose**: In-call semantic search for memory retrieval

**Authentication**: None (trusted agent connection)

**Endpoint**: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`

**Tool Configuration** (ElevenLabs):
```json
{
  "name": "search_memory",
  "description": "Search previous conversations and memories",
  "parameters": {
    "query": {"type": "string", "description": "What to search for"},
    "user_id": {"type": "string", "default": "{{system__caller_id}}"}
  }
}
```

---

## Memory System

### Memory Types
1. **Factual Memories** (`metadata.type = "factual"`)
   - Call summaries and key facts
   - User preferences and account details
   - Used for dynamic variables and context

2. **Semantic Memories** (`metadata.type = "semantic"`)
   - Full conversation transcripts
   - Used for semantic search during calls
   - Enables detailed recall of past conversations

### Memory Storage Process
1. **Call Ends** → ElevenLabs sends webhook to PostCall
2. **Extract Content** → Parse transcript and analysis
3. **Generate Summary** → Create factual memory from key points
4. **Store Both Types** → Save factual + semantic to Mem0
5. **S3 Backup** → Store raw payload for audit trail

### Memory Retrieval Process
1. **Call Starts** → ElevenLabs calls ClientData webhook
2. **Get All Memories** → Retrieve factual + semantic for caller
3. **Extract Name** → Use regex patterns to find caller name
4. **Generate Context** → Build personalized prompt override
5. **Create Variables** → Populate dynamic variables for agent

---

## ElevenLabs Integration

### Agent Configuration Requirements

#### 1. Conversation Initiation Webhook
- **URL**: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`
- **Method**: POST
- **Authentication**: Secrets Manager (NOT direct headers)
- **Secret Name**: `WORKSPACE_KEY`
- **Secret Value**: `wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70`
- **Header Mapping**: `X-Workspace-Key` → `WORKSPACE_KEY` secret

#### 2. Agent Security Settings
Enable in agent's Security tab:
- ✅ "Fetch conversation initiation data for inbound Twilio calls"
- ✅ Allow prompt overrides
- ✅ Allow first message overrides

#### 3. Search Memory Tool
- **URL**: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`
- **Method**: POST
- **Authentication**: None
- **Parameters**: `query` (string), `user_id` (default: `{{system__caller_id}}`)

#### 4. Post-Call Webhook
- **URL**: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`
- **Method**: POST
- **Authentication**: HMAC signature (auto-configured by ElevenLabs)
- **HMAC Secret**: `wsec_a8dc8b6e25ec3ddf11d7e651c40a5cb4931c2ca39d161fa4c94139f12f3ba9d3`

### Dynamic Variables
The system provides these variables for ElevenLabs agents:
- `{{caller_id}}` - Phone number (+16129782029)
- `{{returning_caller}}` - "yes" or "no"  
- `{{caller_name}}` - Extracted name (e.g., "Stefan")
- `{{memory_count}}` - Number of previous interactions
- `{{memory_summary}}` - Most recent/important memory

### System Prompt Template
Use the corrected system prompt from `CORRECTED_MEMOIR_SYSTEM_PROMPT.md` with proper `{{variable_name}}` syntax (double braces).

---

## Mem0 Cloud Configuration

### Current Project Details
- **API Key**: `m0-gS2X0TszRwwEC6mXE3DrEDtpxQJdcCWAariVvafD`
- **Organization ID**: `org_knmmDKevT5Yz7bDF4Dd9BcFDWjp2RHzstpvtN3GW`
- **Project ID**: `proj_3VBb1VIAmQofeGcY0XCHDbb7EqBLeEfETd6iNFqZ`

### User ID Format
Phone numbers in E.164 format: `+16129782029`

### Memory Metadata Schema
```json
{
  "type": "factual|semantic",
  "agent_id": "agent_xxx",
  "timestamp": "2025-10-03T18:52:00Z",
  "call_duration": 120,
  "phone_number": "+16129782029"
}
```

---

## AWS Infrastructure

### CloudFormation Stack
**Name**: `elevenlabs-agentic-memory-stack`
**Region**: `us-east-1`

### Lambda Functions
- `elevenlabs-agentic-memory-lambda-function-client-data`
- `elevenlabs-agentic-memory-lambda-function-post-call`
- `elevenlabs-agentic-memory-lambda-function-search-data`

### API Gateway Endpoints
Each function has its own API Gateway for optimal performance:
- ClientData: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`
- PostCall: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`
- Retrieve: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`

### S3 Storage
**Bucket**: `elevenlabs-agentic-memory-424875385161-us-east-1`
**Purpose**: Backup storage for call data and audit trails

### CloudWatch Logs
**Retention**: 7 days
**Log Groups**:
- `/aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data`
- `/aws/lambda/elevenlabs-agentic-memory-lambda-function-post-call`
- `/aws/lambda/elevenlabs-agentic-memory-lambda-function-search-data`

---

## Development Workflow

### Build & Deploy
```bash
# 1. Build Lambda layer (required first)
cd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..

# 2. Build SAM application
sam build

# 3. Deploy
sam deploy --guided  # First time
sam deploy           # Subsequent deploys
```

### Testing
```bash
# Test individual endpoints
python3 scripts/test_clientdata.py
python3 scripts/test_postcall.py
python3 scripts/test_retrieve.py

# Comprehensive test
python3 scripts/test_production_ready.py
```

### Monitoring
```bash
# Tail logs
aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow

# Check for errors
aws logs filter-log-events --log-group-name "/aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data" --filter-pattern "ERROR"
```

---

## Authentication Reference

### ⚠️ CRITICAL: Authentication Methods (DO NOT CHANGE)

#### ClientData Authentication
**Method**: ElevenLabs Secrets Manager
- Must use ElevenLabs secrets interface
- Cannot use direct headers in webhook configuration
- Secret name: `WORKSPACE_KEY`
- Header mapping: `X-Workspace-Key` → `WORKSPACE_KEY` secret

#### PostCall Authentication  
**Method**: HMAC-SHA256 Signature
- **Reference**: https://elevenlabs.io/docs/agents-platform/workflows/post-call-webhooks#authentication
- Automatic signature verification
- 30-minute timestamp tolerance
- Always return 200 OK (async pattern)

#### Retrieve Authentication
**Method**: None (trusted connection)
- No authentication required
- Direct agent-to-backend communication

---

## Troubleshooting Guide

### Common Issues

#### 1. "Invalid workspace key" Error
**Cause**: ElevenLabs secrets not configured properly
**Fix**: 
1. Add `WORKSPACE_KEY` secret in ElevenLabs settings
2. Map to `X-Workspace-Key` header in webhook config
3. Verify agent has "fetch conversation initiation data" enabled

#### 2. "Missing caller_id" Error  
**Cause**: Webhook payload format incorrect
**Fix**: Ensure payload includes `{"caller_id": "{{system__caller_id}}"}`

#### 3. HMAC Signature Failures
**Cause**: Wrong HMAC key or timestamp drift
**Fix**: Verify HMAC key matches ElevenLabs configuration

#### 4. Memory Not Found
**Cause**: User ID format mismatch
**Fix**: Ensure phone numbers use E.164 format (+1XXXXXXXXXX)

### Debug Commands
```bash
# Test endpoint manually
curl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \
  -H 'X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70' \
  -H 'Content-Type: application/json' \
  -d '{"caller_id": "+16129782029"}' -v

# Check CloudWatch logs  
aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow

# Get conversation data from ElevenLabs
curl https://api.elevenlabs.io/v1/convai/conversations/{conversation_id} \
  -H "xi-api-key: sk_1203631b4b7e9d5e06cc793713322c3788daff35da4d23bf"
```

---

## Test Data

### Stefan (Returning User)
- **Phone**: `+16129782029`
- **Memories**: 4 stored interactions
- **Context**: Premium account, prefers email updates
- **Expected Greeting**: "Hello Stefan! I know you prefer email updates. How can I assist you today?"

### New Users
- **Any new phone number**
- **Memories**: 0 interactions
- **Expected Greeting**: "Hello! Welcome to our memoir interview service. Could you please tell me your name?"

---

## File Organization

### Core Files
- `template.yaml` - SAM CloudFormation template
- `samconfig.toml` - Deployment configuration (gitignored)
- `.env` - Environment variables for testing (gitignored)

### Source Code
- `src/client_data/handler.py` - Pre-call memory retrieval
- `src/post_call/handler.py` - Post-call memory storage  
- `src/retrieve/handler.py` - In-call memory search
- `layer/requirements.txt` - Lambda layer dependencies

### Documentation
- `MASTER_DOCUMENTATION.md` - This comprehensive guide
- `CORRECTED_MEMOIR_SYSTEM_PROMPT.md` - ElevenLabs system prompt template

### Scripts
- `scripts/test_*.py` - Testing utilities
- `scripts/debug_*.py` - Debugging tools

### Archived Documentation
The following files contain historical information but are superseded by this master document:
- `README.md`, `SPECIFICATION.md`, `CLAUDE.md` - Original documentation
- `ELEVENLABS_*` - Setup guides and configuration docs
- `*_COMPLETE.md` - Status and completion reports

---

## Security Considerations

### Secrets Management
- **Never commit** API keys, HMAC secrets, or workspace keys to git
- **Use environment variables** for local development
- **Use SAM parameters** for deployment configuration
- **Use ElevenLabs secrets manager** for webhook authentication

### Network Security
- **HTTPS only** for all webhook endpoints
- **API Gateway** provides DDoS protection and throttling
- **Lambda functions** run in isolated environments
- **CloudWatch** logs exclude sensitive data

### Data Privacy
- **Phone numbers** used as user IDs (no PII collection beyond conversation content)
- **Mem0 Cloud** handles data encryption and compliance
- **S3 storage** uses server-side encryption
- **7-day log retention** minimizes data exposure

---

## Support and Resources

### External Documentation
- [Mem0 Cloud Documentation](https://docs.mem0.ai/)
- [ElevenLabs Agents Platform](https://elevenlabs.io/docs/agents-platform)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)

### Internal Resources
- CloudWatch Dashboards: Monitor function performance
- S3 Bucket: Access stored call data
- Mem0 Dashboard: View and manage memories

### Emergency Contacts
- **Stack Name**: `elevenlabs-agentic-memory-stack`
- **Region**: `us-east-1`
- **Primary Test User**: Stefan (+16129782029)

---

*Last Updated: October 3, 2025*
*Version: 1.0 - Master Documentation*