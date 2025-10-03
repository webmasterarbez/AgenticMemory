# AgenticMemory Product Documentation

**Version:** 1.0  
**Last Updated:** October 3, 2025  
**Status:** Production Ready

---

## Executive Summary

**AgenticMemory** is a serverless AWS backend that bridges ElevenLabs voice agents with Mem0 Cloud to provide conversational memory capabilities. It enables voice agents to remember caller information across conversations, retrieve context during calls, and store new memories after each interaction.

### Key Capabilities
- 🧠 **Persistent Memory** - Remember caller preferences, history, and context across calls
- 👤 **Caller Identification** - Automatic recognition and personalization using phone numbers
- 🔍 **Semantic Search** - Real-time memory search during conversations
- 💾 **Dual Storage** - Memories in Mem0 Cloud + transcripts/audio in S3
- 🔐 **Enterprise Security** - Workspace key + HMAC-SHA256 authentication

---

## Table of Contents

1. [Product Overview](#product-overview)
2. [Architecture](#architecture)
3. [Core Features](#core-features)
4. [API Endpoints](#api-endpoints)
5. [Memory System](#memory-system)
6. [Authentication & Security](#authentication--security)
7. [Integration Guide](#integration-guide)
8. [Use Cases](#use-cases)
9. [Technical Specifications](#technical-specifications)
10. [Deployment](#deployment)

---

## Product Overview

### What It Does

AgenticMemory acts as a memory layer for voice agents, enabling them to:

1. **Pre-Call**: Retrieve caller history and generate personalized greetings
2. **During Call**: Search past conversations and preferences in real-time
3. **Post-Call**: Store conversation summaries, transcripts, and evaluations

### How It Works

```
┌─────────────────┐
│  ElevenLabs     │
│  Voice Agent    │
└────────┬────────┘
         │
         ├─────────── Pre-Call ────────► ClientData Endpoint
         │                               (Get memories + greeting)
         │
         ├─────────── During Call ──────► Retrieve Endpoint
         │                               (Semantic search)
         │
         └─────────── Post-Call ────────► PostCall Endpoint
                                         (Store new memories)
                                         
┌─────────────────────────────────────────────────────────┐
│                    AgenticMemory Backend                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  ClientData  │  │   Retrieve   │  │   PostCall   │ │
│  │   Lambda     │  │    Lambda    │  │    Lambda    │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          ▼                  ▼                  ▼
    ┌─────────────────────────────────────────────┐
    │            Mem0 Cloud (Memory Store)        │
    └─────────────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   AWS S3 Bucket │
                    │  (Transcripts)  │
                    └─────────────────┘
```

### Target Users

- **Contact Centers** - Customer service with personalized interactions
- **Sales Teams** - Relationship building with memory of past conversations
- **Healthcare** - Patient interaction history and preferences
- **Hospitality** - Guest preference tracking and personalized service
- **Any Business** using ElevenLabs voice agents requiring conversation memory

---

## Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | AWS Lambda (Python 3.12) | Serverless compute |
| **API Gateway** | AWS API Gateway v2 (HTTP) | REST endpoints |
| **Memory Store** | Mem0 Cloud | AI-powered memory management |
| **File Storage** | AWS S3 | Transcripts and audio files |
| **Infrastructure** | AWS SAM (CloudFormation) | Infrastructure as Code |
| **Logging** | CloudWatch Logs | Monitoring and debugging |
| **Authentication** | Workspace Keys + HMAC-SHA256 | Security |

### AWS Resources

All resources follow the `elevenlabs-agentic-memory-*` naming convention:

```
elevenlabs-agentic-memory-stack (CloudFormation Stack)
├── elevenlabs-agentic-memory-role (IAM Role)
├── elevenlabs-agentic-memory-lambda-function-client-data
├── elevenlabs-agentic-memory-lambda-function-search-data
├── elevenlabs-agentic-memory-lambda-function-post-call
├── elevenlabs-agentic-memory-api-gateway-client-data
├── elevenlabs-agentic-memory-api-gateway-search-data
├── elevenlabs-agentic-memory-api-gateway-post-call
├── /aws/lambda/elevenlabs-agentic-memory-log-client-data
├── /aws/lambda/elevenlabs-agentic-memory-log-search-data
├── /aws/lambda/elevenlabs-agentic-memory-log-post-call
└── elevenlabs-agentic-memory-{AccountId}-{Region} (S3 Bucket)
```

### Deployment Architecture

- **Region**: us-east-1 (configurable)
- **Availability**: Multi-AZ (Lambda + API Gateway)
- **Concurrency**: 10 reserved concurrent executions per function
- **Timeout**: 30s (ClientData/Retrieve), 60s (PostCall)
- **Memory**: 128MB per function

---

## Core Features

### 1. Pre-Call Memory Retrieval (ClientData)

**Purpose**: Load caller history before conversation starts

**Capabilities**:
- ✅ Retrieve all memories for caller (phone number as ID)
- ✅ Extract caller name from memory using AI patterns
- ✅ Generate personalized greeting based on context
- ✅ Separate factual vs semantic memories
- ✅ Build contextual prompt for agent
- ✅ Return dynamic variables for ElevenLabs

**Input**: Caller phone number  
**Output**: Memories, personalized greeting, dynamic variables

**Dynamic Variables Provided**:
- `caller_id` - Phone number
- `memory_count` - Total memories
- `memory_summary` - Key information
- `returning_caller` - "yes" or "no"
- `caller_name` - Extracted name (if found)

**Example Use**:
```
New Caller → "Hello! How may I help you today?"
Returning Caller → "Hello Stefan! Welcome back. How can I assist you today?"
```

---

### 2. In-Call Semantic Search (Retrieve)

**Purpose**: Search memories during active conversation

**Capabilities**:
- ✅ Semantic search across all caller memories
- ✅ Natural language query processing
- ✅ Relevance-ranked results
- ✅ Search both factual and semantic memories
- ✅ Configurable result limit (default: 10)
- ✅ No authentication required (trusted agent)

**Input**: Search query + caller phone number  
**Output**: Ranked list of relevant memories

**Example Queries**:
- "What are the user's preferences?"
- "Tell me about their last issue"
- "What product did they inquire about?"

**Response Format**:
```json
{
  "memories": [
    {
      "id": "uuid",
      "memory": "User prefers email communication",
      "score": 0.89,
      "metadata": {
        "type": "factual",
        "timestamp": "2025-10-02T01:26:13.749007"
      }
    }
  ]
}
```

---

### 3. Post-Call Memory Storage (PostCall)

**Purpose**: Store conversation data after call ends

**Capabilities**:
- ✅ HMAC-SHA256 signature verification
- ✅ Dual memory storage (factual + semantic)
- ✅ S3 transcript storage
- ✅ S3 audio file storage (if provided)
- ✅ Async processing (returns 200 immediately)
- ✅ Comprehensive error logging

**Two Memory Types Stored**:

1. **Factual Memory**:
   - Summary + evaluation rationale
   - Extracted facts and preferences
   - Metadata: `type: "factual"`

2. **Semantic Memory**:
   - Full conversation transcript
   - Preserves context and flow
   - Metadata: `type: "semantic"`

**S3 Storage Structure**:
```
s3://elevenlabs-agentic-memory-{AccountId}-{Region}/
├── transcripts/
│   └── {caller_id}/
│       └── {conversation_id}_{timestamp}.json
└── audio/
    └── {caller_id}/
        └── {conversation_id}_{timestamp}.mp3
```

**Input**: ElevenLabs post-call webhook payload  
**Output**: 200 OK (async processing)

---

## API Endpoints

### Current Production URLs

| Endpoint | URL | Method | Auth |
|----------|-----|--------|------|
| ClientData | `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data` | POST | Workspace Key |
| Retrieve | `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve` | POST | None |
| PostCall | `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call` | POST | HMAC |

---

### ClientData Endpoint

**URL**: `/Prod/client-data`  
**Method**: POST  
**Authentication**: `X-Workspace-Key` header

**Request**:
```json
{
  "caller_id": "+16129782029"
}
```

**Response**:
```json
{
  "type": "conversation_initiation_client_data",
  "dynamic_variables": {
    "caller_id": "+16129782029",
    "memory_count": "15",
    "memory_summary": "User sympathizes with people of color",
    "returning_caller": "yes",
    "caller_name": "Stefan"
  },
  "conversation_config_override": {
    "agent": {
      "prompt": {
        "prompt": "CALLER CONTEXT:\nThis caller has 15 previous interactions..."
      },
      "first_message": "Hello Stefan! How can I assist you today?"
    }
  }
}
```

**Status Codes**:
- `200` - Success
- `400` - Missing caller_id
- `401` - Invalid/missing workspace key
- `500` - Server error

---

### Retrieve Endpoint

**URL**: `/Prod/retrieve`  
**Method**: POST  
**Authentication**: None (trusted agent connection)

**Request**:
```json
{
  "query": "What are the user's preferences?",
  "user_id": "+16129782029",
  "limit": 10
}
```

**Response**:
```json
{
  "memories": [
    {
      "id": "uuid",
      "memory": "User prefers email communication",
      "user_id": "+16129782029",
      "metadata": {
        "type": "factual",
        "agent_id": "agent_id",
        "timestamp": "2025-10-02T01:26:13.749007"
      },
      "score": 0.89
    }
  ]
}
```

**Parameters**:
- `query` (required) - Natural language search query
- `user_id` (required) - Caller phone number
- `limit` (optional) - Max results (default: 10)

**Status Codes**:
- `200` - Success (even if 0 results)
- `400` - Missing required parameters
- `500` - Server error

---

### PostCall Endpoint

**URL**: `/Prod/post-call`  
**Method**: POST  
**Authentication**: HMAC-SHA256 signature in `ElevenLabs-Signature` header

**Request** (ElevenLabs format):
```json
{
  "conversation_id": "conv_123",
  "agent_id": "agent_456",
  "call_duration": 120,
  "transcript": [
    {
      "role": "user",
      "content": "Hello, I need help"
    },
    {
      "role": "assistant",
      "content": "I'd be happy to help"
    }
  ],
  "analysis": {
    "summary": "Customer requested help",
    "evaluation": {
      "rationale": "Customer was polite"
    }
  },
  "metadata": {
    "phone_call": {
      "external_number": "+16129782029"
    }
  },
  "recording_url": "https://..."
}
```

**Response**:
```json
{
  "status": "ok"
}
```

**HMAC Signature Format**:
```
Header: ElevenLabs-Signature
Value: t=1234567890,v0=abc123def456...

Payload to sign: {timestamp}.{request_body}
Algorithm: HMAC-SHA256
Key: Your HMAC secret key
```

**Status Codes**:
- `200` - Always returns 200 (async processing)
- Errors logged to CloudWatch

---

## Memory System

### Memory Storage Architecture

```
Phone Number (E.164)
        │
        └─── User ID in Mem0
                │
                ├─── Factual Memories
                │    ├── Summary statements
                │    ├── Preferences
                │    ├── Account info
                │    └── Extracted facts
                │
                └─── Semantic Memories
                     ├── Full transcripts
                     ├── Conversation flow
                     └── Contextual details
```

### Memory Types

#### Factual Memories
- **Content**: Extracted facts, summaries, evaluations
- **Format**: Concise statements
- **Metadata**: `type: "factual"`
- **Example**: "User prefers email communication"
- **Use**: Quick facts, preferences, status

#### Semantic Memories
- **Content**: Full conversation transcripts
- **Format**: Complete message arrays
- **Metadata**: `type: "semantic"`
- **Example**: Full back-and-forth conversation
- **Use**: Context, conversation flow, detailed history

### Memory Metadata

Each memory includes:
```json
{
  "type": "factual" | "semantic",
  "agent_id": "agent_123",
  "timestamp": "2025-10-02T01:26:13.749007",
  "call_duration": 120,
  "conversation_id": "conv_123"
}
```

### User Identification

- **Primary Key**: Phone number in E.164 format
- **Format**: `+[country][area][number]`
- **Example**: `+16129782029`
- **Consistency**: Same format across all endpoints
- **Isolation**: Memories completely isolated per phone number

---

## Authentication & Security

### Security Model

```
┌─────────────────────────────────────────────────────────┐
│                    Security Layers                       │
├─────────────────────────────────────────────────────────┤
│  ClientData    │  X-Workspace-Key header validation    │
│  (Pre-call)    │  wsec_* key format                     │
├─────────────────────────────────────────────────────────┤
│  Retrieve      │  No authentication                     │
│  (In-call)     │  Trusted agent connection              │
├─────────────────────────────────────────────────────────┤
│  PostCall      │  HMAC-SHA256 signature                │
│  (Post-call)   │  30-minute timestamp tolerance         │
└─────────────────────────────────────────────────────────┘
```

### 1. Workspace Key Authentication (ClientData)

**Method**: Header-based validation

```http
X-Workspace-Key: wsec_955d3f63879a0daf23483809cbc8b135eb851bcecfab6eb6767bc23d11b762ed
```

**Validation**:
- Case-insensitive header lookup
- Exact match required
- Returns 401 if invalid/missing

**Use Case**: Webhook called by ElevenLabs before call starts

---

### 2. No Authentication (Retrieve)

**Method**: None

**Rationale**: 
- Called during active conversation
- Trusted connection between agent and backend
- Low latency requirement (no auth overhead)
- Agent already authenticated with ElevenLabs

**Security Notes**:
- Not publicly exposed
- Used only within secure ElevenLabs agent context
- No sensitive data in responses (only caller's own memories)

---

### 3. HMAC-SHA256 Signature (PostCall)

**Method**: Cryptographic signature verification

**Header Format**:
```
ElevenLabs-Signature: t=1234567890,v0=abc123...
```

**Verification Process**:
```python
# 1. Extract timestamp and signature from header
timestamp, signature = parse_header(header)

# 2. Check timestamp tolerance (30 minutes)
if abs(time.now() - timestamp) > 1800:
    return invalid

# 3. Build payload to verify
payload = f"{timestamp}.{request_body}"

# 4. Compute expected signature
expected = hmac.sha256(secret_key, payload)

# 5. Compare signatures (constant-time)
if signature == expected:
    return valid
```

**Security Features**:
- Prevents replay attacks (timestamp validation)
- Prevents tampering (signature verification)
- Constant-time comparison (prevents timing attacks)

**Tolerance**: 30 minutes (1800 seconds)

---

### Data Security

**In Transit**:
- ✅ HTTPS/TLS 1.2+ for all endpoints
- ✅ API Gateway encryption

**At Rest**:
- ✅ S3 server-side encryption (AES-256)
- ✅ Mem0 Cloud encryption

**Access Control**:
- ✅ IAM role with least-privilege permissions
- ✅ S3 bucket policies
- ✅ CloudWatch log encryption

**Compliance**:
- ✅ GDPR-ready (user data isolation)
- ✅ HIPAA-compatible architecture
- ✅ SOC 2 controls (CloudWatch auditing)

---

## Integration Guide

### ElevenLabs Integration

#### Step 1: Configure Conversation Initiation Webhook

**In ElevenLabs Dashboard**:
1. Go to Agent Settings → Webhooks
2. Add Conversation Initiation webhook:
   - **URL**: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`
   - **Method**: POST
   - **Headers**: 
     ```
     X-Workspace-Key: wsec_955d3f63879a0daf23483809cbc8b135eb851bcecfab6eb6767bc23d11b762ed
     ```

**What It Does**:
- Called before each conversation starts
- Provides caller history and personalized greeting
- Agent receives dynamic variables and memory context

---

#### Step 2: Add Memory Search Tool

**In ElevenLabs Dashboard**:
1. Go to Agent Settings → Tools
2. Add custom tool:
   - **Name**: "Search Memory"
   - **Description**: "Search caller's conversation history"
   - **URL**: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`
   - **Method**: POST
   - **Parameters**:
     - `query` (string, required) - Search query
     - `user_id` (string, required) - Use `{{caller_phone}}` variable
     - `limit` (integer, optional) - Default: 10

**What It Does**:
- Agent can search memories during conversation
- Use natural language queries
- Returns relevant past interactions

**Example Agent Usage**:
```
Agent: Let me check your previous interactions...
[Calls Search Memory tool with query="last issue"]
Agent: I see you contacted us about email access last week.
```

---

#### Step 3: Configure Post-Call Webhook

**In ElevenLabs Dashboard**:
1. Go to Agent Settings → Webhooks
2. Add Post-Call webhook:
   - **URL**: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`
   - **Method**: POST
   - **HMAC Key**: `wsec_955d3f63879a0daf23483809cbc8b135eb851bcecfab6eb6767bc23d11b762ed`
   - **Signature Header**: `ElevenLabs-Signature`

**What It Does**:
- Called automatically after conversation ends
- Stores summary, transcript, and evaluation
- Saves audio recording to S3
- Creates searchable memories for next interaction

---

### Integration Checklist

- [ ] Configure Mem0 Cloud account (API key, Org ID, Project ID)
- [ ] Deploy AWS infrastructure with SAM
- [ ] Capture API Gateway URLs from deployment
- [ ] Configure ClientData webhook in ElevenLabs
- [ ] Add Memory Search tool in ElevenLabs
- [ ] Configure PostCall webhook with HMAC key
- [ ] Test with sample call
- [ ] Verify memories stored in Mem0
- [ ] Check CloudWatch logs
- [ ] Confirm S3 transcript storage

---

## Use Cases

### 1. Customer Service

**Scenario**: Returning customer calls support

**Flow**:
1. Customer calls → ClientData retrieves history
2. Agent greets: "Hello Sarah! I see you called about your order last week."
3. During call, agent searches: "What was Sarah's last order?"
4. After call, summary stored: "Customer requested refund for order #12345"

**Benefits**:
- No repeated questions
- Faster resolution
- Personalized service
- Context awareness

---

### 2. Sales Follow-Up

**Scenario**: Sales rep follows up with prospect

**Flow**:
1. Prospect calls → System loads: "Interested in Enterprise plan"
2. Agent: "Hi John! Following up on the Enterprise plan discussion."
3. During call: Search "pricing concerns" → Shows previous objections
4. After call: Store "Agreed to 30-day trial, follow up on 10/15"

**Benefits**:
- Relationship continuity
- No lost context
- Informed conversations
- Better conversion rates

---

### 3. Healthcare

**Scenario**: Patient calls medical office

**Flow**:
1. Patient calls → Load: "Prefers morning appointments"
2. Receptionist: "Hello Maria! I have a morning slot available."
3. Store after call: "Scheduled follow-up, reminded about medication"

**Benefits**:
- Patient preference awareness
- Continuity of care
- Personalized scheduling
- Compliance tracking

---

### 4. Hospitality

**Scenario**: Guest calls hotel concierge

**Flow**:
1. Guest calls → Load: "Stayed in June, vegetarian, likes spa"
2. Concierge: "Welcome back! Would you like to book the spa again?"
3. Store: "Requested dinner reservation at vegetarian restaurant"

**Benefits**:
- VIP treatment for all
- Preference memory
- Personalized recommendations
- Guest satisfaction

---

## Technical Specifications

### Performance

| Metric | Target | Actual |
|--------|--------|--------|
| ClientData Response Time | < 2s | ~800ms |
| Retrieve Response Time | < 1s | ~400ms |
| PostCall Acknowledgment | < 200ms | ~50ms |
| Cold Start Time | < 3s | ~2.5s |
| Concurrent Users | 100+ | 100 (reserved) |

### Limits

| Resource | Limit | Configurable |
|----------|-------|--------------|
| Lambda Timeout | 30s (sync), 60s (async) | Yes |
| Lambda Memory | 128MB | Yes |
| API Gateway Timeout | 30s | No |
| Memory Search Results | 10 (default) | Yes |
| Concurrent Executions | 10 (reserved) | Yes |
| S3 Object Size | 5GB | No |

### Scalability

- **Auto-scaling**: Lambda scales automatically to demand
- **Rate Limiting**: API Gateway default limits apply
- **Mem0 Cloud**: Scales with usage
- **S3 Storage**: Virtually unlimited
- **Cost**: Pay-per-use (no minimum)

### Reliability

- **Availability**: 99.9% (Lambda + API Gateway SLA)
- **Durability**: 99.999999999% (S3)
- **Redundancy**: Multi-AZ deployment
- **Monitoring**: CloudWatch alarms on errors
- **Logging**: 7-day retention (configurable)

---

## Deployment

### Prerequisites

- AWS Account with admin access
- AWS CLI configured
- SAM CLI installed
- Mem0 Cloud account
- ElevenLabs account
- Python 3.12+

### Quick Deploy

```bash
# 1. Clone repository
git clone https://github.com/webmasterarbez/AgenticMemory.git
cd AgenticMemory

# 2. Build Lambda layer
cd layer && mkdir -p python
pip install -r requirements.txt -t python/
cd ..

# 3. Build SAM application
sam build

# 4. Deploy with guided setup
sam deploy --guided \
  --stack-name elevenlabs-agentic-memory-stack \
  --capabilities CAPABILITY_NAMED_IAM

# 5. Capture output URLs
aws cloudformation describe-stacks \
  --stack-name elevenlabs-agentic-memory-stack \
  --query 'Stacks[0].Outputs'
```

### Configuration

**Required Environment Variables** (set during deployment):

```bash
MEM0_API_KEY=m0-...
MEM0_ORG_ID=org_...
MEM0_PROJECT_ID=proj_...
ELEVENLABS_WORKSPACE_KEY=wsec_...
ELEVENLABS_HMAC_KEY=wsec_...
```

### Post-Deployment

1. **Update .env file** with new API URLs
2. **Configure ElevenLabs** webhooks with URLs
3. **Run tests** to verify functionality:
   ```bash
   python scripts/test_production_ready.py
   ```
4. **Monitor logs** in CloudWatch
5. **Make test call** through ElevenLabs

---

## Monitoring & Operations

### CloudWatch Logs

**Log Groups**:
```
/aws/lambda/elevenlabs-agentic-memory-log-client-data
/aws/lambda/elevenlabs-agentic-memory-log-search-data
/aws/lambda/elevenlabs-agentic-memory-log-post-call
```

**Log Retention**: 7 days (configurable in template.yaml)

**Viewing Logs**:
```bash
# Tail logs in real-time
aws logs tail /aws/lambda/elevenlabs-agentic-memory-log-client-data --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/elevenlabs-agentic-memory-log-post-call \
  --filter-pattern "ERROR"
```

### Metrics

**Key Metrics to Monitor**:
- Lambda invocations (count)
- Lambda duration (milliseconds)
- Lambda errors (count)
- Lambda throttles (count)
- API Gateway 4XX errors
- API Gateway 5XX errors
- S3 PUT requests
- Mem0 API calls

### Alerts

**Recommended CloudWatch Alarms**:
```yaml
- Lambda error rate > 1%
- Lambda duration > 25s
- API Gateway 5XX errors > 5
- Lambda throttles > 0
```

### Cost Monitoring

**Monthly Cost Estimate** (1000 calls):
- Lambda executions: ~$0.20
- API Gateway requests: ~$0.01
- S3 storage (1GB): ~$0.02
- Mem0 Cloud: Variable (see Mem0 pricing)
- CloudWatch Logs: ~$0.50

**Total**: < $1/month + Mem0 costs

---

## Testing

### Test Suite

All tests use `.env` configuration (no manual input required):

```bash
# Validate configuration
python scripts/validate_env.py

# Comprehensive test
python scripts/test_production_ready.py

# Individual endpoint tests
python scripts/test_clientdata.py
python scripts/test_retrieve.py
python scripts/test_postcall.py

# Feature tests
python scripts/test_personalized_greetings.py
python scripts/test_hmac_auth.py
```

### Test Data

**Default Test User**: `+16129782029` (has memories)  
**New User**: `+19995551234` (no memories)

### CI/CD Integration

```bash
#!/bin/bash
# Validate environment
python scripts/validate_env.py || exit 1

# Run tests
python scripts/test_production_ready.py
exit $?
```

---

## Support & Resources

### Documentation

- **Product Docs**: `PRODUCT_DOCUMENTATION.md` (this file)
- **API Reference**: `CLIENTDATA_DYNAMIC_VARIABLES.md`
- **Deployment Guide**: `README.md`
- **Integration Guide**: `ELEVENLABS_SETUP_GUIDE.md`
- **Quick Reference**: `QUICK_REFERENCE.md`
- **Test Guide**: `QUICK_TEST_GUIDE.md`

### External Resources

- [Mem0 Documentation](https://docs.mem0.ai/)
- [ElevenLabs API Docs](https://elevenlabs.io/docs)
- [AWS Lambda Guide](https://docs.aws.amazon.com/lambda/)
- [AWS SAM Reference](https://docs.aws.amazon.com/serverless-application-model/)

### Common Issues

#### Issue: "Invalid workspace key"
**Solution**: Check `X-Workspace-Key` header matches deployed value

#### Issue: "HMAC signature verification failed"
**Solution**: Verify HMAC key in ElevenLabs matches deployed value

#### Issue: "Mem0 API timeout"
**Solution**: Check Mem0 Cloud status, verify credentials

#### Issue: "No memories returned"
**Solution**: Verify caller_id format is E.164 (`+16129782029`)

---

## Roadmap

### Planned Features

- [ ] Multi-language support
- [ ] Custom memory retention policies
- [ ] Memory export/import functionality
- [ ] Advanced search filters
- [ ] Real-time memory updates
- [ ] Analytics dashboard
- [ ] Memory versioning
- [ ] Bulk operations API

---

## Appendix

### API Response Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Continue normally |
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Verify authentication |
| 500 | Server Error | Check logs, retry |

### Phone Number Format

**Valid Formats**:
- ✅ `+16129782029` (E.164)
- ✅ `+441234567890` (UK)
- ✅ `+33123456789` (France)

**Invalid Formats**:
- ❌ `6129782029` (missing +1)
- ❌ `1-612-978-2029` (dashes)
- ❌ `(612) 978-2029` (parentheses)

### Memory Best Practices

**Do**:
- ✅ Use consistent phone number format
- ✅ Store factual summaries (concise)
- ✅ Include timestamps in metadata
- ✅ Separate facts from conversations

**Don't**:
- ❌ Store PII unnecessarily
- ❌ Duplicate information
- ❌ Store raw audio in Mem0
- ❌ Mix memory types

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Oct 3, 2025 | Initial production release |
| 0.9 | Oct 2, 2025 | Test configuration updates |
| 0.8 | Oct 1, 2025 | Naming convention standardization |
| 0.7 | Sep 30, 2025 | S3 storage implementation |
| 0.6 | Sep 29, 2025 | Personalized greeting generation |
| 0.5 | Sep 28, 2025 | Initial memory storage |

---

**End of Product Documentation**

For technical support or feature requests, please contact the development team or open an issue in the GitHub repository.
