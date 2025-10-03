# Eleven Labs Agentic Memory# Eleven Labs AgenticMemory# 



> **Conversational Memory for ElevenLabs Voice Agents**> **Conversational Memory for ElevenLabs Voice Agents**



Eleven Labs Agentic Memory is an AWS serverless backend that provides persistent memory capabilities for ElevenLabs voice agents using Mem0 Cloud. It enables agents to remember previous conversations and provide personalized interactions.



## Table of ContentsEleven Labs Agentic Memory is an AWS serverless backend that provides persistent memory capabilities for ElevenLabs voice agents using Mem0 Cloud. It enables agents to remember previous conversations and provide personalized interactions.> **Conversational Memory for ElevenLabs Voice Agents****Production-Ready AWS Serverless Backend** for ElevenLabs Voice Agents with Mem0 Cloud integration for conversational memory management.



1. [🚀 Quick Start](#-quick-start)

2. [🏗️ Architecture](#️-architecture)  

3. [🔐 Authentication (CRITICAL)](#-authentication-critical)## Table of Contents

4. [📋 System Components](#-system-components)

5. [🧠 Memory System](#-memory-system)

6. [🎤 ElevenLabs Integration](#-elevenlabs-integration)

7. [☁️ AWS Infrastructure](#️-aws-infrastructure)1. [🚀 Quick Start](#-quick-start)Eleven Labs Agentic Memory is an AWS serverless backend that provides persistent memory capabilities for ElevenLabs voice agents using Mem0 Cloud. It enables agents to remember previous conversations and provide personalized interactions.[![AWS SAM](https://img.shields.io/badge/AWS%20SAM-Serverless-orange)](https://aws.amazon.com/serverless/sam/)

8. [🛠️ Development Workflow](#️-development-workflow)

9. [🧪 Testing](#-testing)2. [🏗️ Architecture](#️-architecture)  

10. [🔍 Troubleshooting](#-troubleshooting)

11. [📂 Project Structure](#-project-structure)3. [🔐 Authentication (CRITICAL)](#-authentication-critical)[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)

12. [🤖 System Prompt Template](#-system-prompt-template)

4. [📋 System Components](#-system-components)

---

5. [🧠 Memory System](#-memory-system)## 🚀 Quick Start[![Mem0](https://img.shields.io/badge/Mem0-Cloud-green)](https://mem0.ai/)

## 🚀 Quick Start

6. [🎤 ElevenLabs Integration](#-elevenlabs-integration)

### 1. Deploy the Backend

```bash7. [☁️ AWS Infrastructure](#️-aws-infrastructure)[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-Voice%20AI-purple)](https://elevenlabs.io/)

# Build dependencies

cd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..8. [🛠️ Development Workflow](#️-development-workflow)



# Deploy to AWS9. [🧪 Testing](#-testing)### 1. Deploy the Backend

sam build && sam deploy --guided

```10. [🔍 Troubleshooting](#-troubleshooting)



### 2. Configure ElevenLabs11. [📂 Project Structure](#-project-structure)```bash## Overview

- **Conversation Initiation Webhook**: Set URL and authentication via secrets manager

- **Search Memory Tool**: Configure for in-call memory retrieval  12. [🤖 System Prompt Template](#-system-prompt-template)

- **Post-Call Webhook**: Enable for memory storage with HMAC authentication

# Build dependencies

### 3. Test the System

```bash---

python3 scripts/test_production_ready.py

```cd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..This system bridges **ElevenLabs voice agents** with **Mem0 Cloud** for persistent conversational memory across calls. Three optimized Lambda functions handle the complete memory lifecycle:



---## 🚀 Quick Start



## 🏗️ Architecture



```### 1. Deploy the Backend

ElevenLabs Agent ←→ AWS Lambda Functions ←→ Mem0 Cloud

                         ↓```bash# Deploy to AWS1. **ClientData** (Pre-call): Returns personalized memory context when conversation starts

                   S3 Storage (backup)

```# Build dependencies



**3 Lambda Functions**:cd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..sam build && sam deploy --guided2. **Retrieve** (Mid-call): Semantic search for agent tools during active conversations  

- **ClientData**: Pre-call memory retrieval + personalized greeting

- **PostCall**: Async memory storage after calls

- **Retrieve**: In-call semantic search tool

# Deploy to AWS```3. **PostCall** (Async): Stores factual and semantic memories after call completion

---

sam build && sam deploy --guided

## 🔐 Authentication (CRITICAL)

```

### ⚠️ DO NOT CHANGE THESE AUTHENTICATION METHODS



#### ClientData Authentication

**Method**: ElevenLabs Secrets Manager (NOT direct headers)### 2. Configure ElevenLabs### 2. Configure ElevenLabs**✨ Key Features:**



**Configuration**:- **Conversation Initiation Webhook**: Set URL and authentication via secrets manager

1. Go to [ElevenLabs Settings](https://elevenlabs.io/app/agents/settings)

2. Add secret: `WORKSPACE_KEY` = `wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70`- **Search Memory Tool**: Configure for in-call memory retrieval  - **Conversation Initiation Webhook**: Set URL and authentication via secrets manager- 🚀 **Sub-500ms latency** with separate HTTP APIs per function

3. Map to header: `X-Workspace-Key` → `WORKSPACE_KEY` secret

4. Enable in agent Security tab: "Fetch conversation initiation data"- **Post-Call Webhook**: Enable for memory storage with HMAC authentication



**Why**: ElevenLabs requires authentication headers to be managed through their secure secrets interface, not as direct header configuration.- **Search Memory Tool**: Configure for in-call memory retrieval  - 🔐 **Production security** with HMAC signatures and workspace key auth



#### PostCall Authentication### 3. Test the System

**Method**: HMAC-SHA256 Signature

```bash- **Post-Call Webhook**: Enable for memory storage with HMAC authentication- 🧠 **Smart memory separation** between factual data and conversation context

**Reference**: https://elevenlabs.io/docs/agents-platform/workflows/post-call-webhooks#authentication

python3 scripts/test_production_ready.py

**Configuration**:

- HMAC Key: `wsec_a8dc8b6e25ec3ddf11d7e651c40a5cb4931c2ca39d161fa4c94139f12f3ba9d3````- 📊 **Real-time monitoring** with CloudWatch integration

- Header: `ElevenLabs-Signature` (format: `t=timestamp,v0=signature`)

- Tolerance: 30 minutes

- Always return 200 OK (async processing)

---### 3. Test the System- 🔄 **Async processing** to prevent webhook timeouts

**Why**: ElevenLabs uses HMAC signatures to verify webhook authenticity and prevent replay attacks.



#### Retrieve Authentication  

**Method**: None (trusted connection)## 🏗️ Architecture```bash- ⚡ **Optimized performance** with Lambda layer reuse



**Configuration**: No authentication required



**Why**: Direct communication between ElevenLabs agent and backend during active calls is considered trusted.```python3 scripts/test_production_ready.py



### Quick Authentication TestElevenLabs Agent ←→ AWS Lambda Functions ←→ Mem0 Cloud

```bash

# ClientData (should return 200 with memory data)                         ↓```## 📁 Project Structure

curl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \

  -H 'X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70' \                   S3 Storage (backup)

  -H 'Content-Type: application/json' \

  -d '{"caller_id": "+16129782029"}' -v```



# Test wrong key (should return 401)

curl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \

  -H 'X-Workspace-Key: wrong_key' \**3 Lambda Functions**:## 📋 Complete Documentation```

  -H 'Content-Type: application/json' \

  -d '{"caller_id": "+16129782029"}' -s -w "Status: %{http_code}\n"- **ClientData**: Pre-call memory retrieval + personalized greeting

```

- **PostCall**: Async memory storage after callsAgenticMemory/

---

- **Retrieve**: In-call semantic search tool

## 📋 System Components

**📖 [MASTER_DOCUMENTATION.md](MASTER_DOCUMENTATION.md)** - Complete project guide covering:├── src/                    # Lambda function source code

### 1. ClientData Function (`src/client_data/handler.py`)

**Purpose**: Pre-call memory retrieval + personalized greeting generation---



**Endpoint**: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`- Architecture overview and components│   ├── client_data/        # Pre-call memory retrieval



**Request Format**:## 🔐 Authentication (CRITICAL)

```json

{- ElevenLabs integration setup│   ├── retrieve/           # Mid-call semantic search

  "caller_id": "+16129782029",

  "agent_id": "agent_xxx"### ⚠️ DO NOT CHANGE THESE AUTHENTICATION METHODS

}

```- Authentication methods (ClientData secrets + PostCall HMAC)│   └── post_call/          # Async memory storage



**Response Format**:#### ClientData Authentication

```json

{**Method**: ElevenLabs Secrets Manager (NOT direct headers)- Memory system operation├── layer/                  # Shared Lambda layer (mem0ai)

  "type": "conversation_initiation_client_data",

  "dynamic_variables": {

    "caller_id": "+16129782029",

    "memory_count": "4",**Configuration**:- Troubleshooting and monitoring├── docs/                   # 📚 All documentation

    "memory_summary": "User wants to update email address",

    "returning_caller": "yes",1. Go to [ElevenLabs Settings](https://elevenlabs.io/app/agents/settings)

    "caller_name": "Stefan"

  },2. Add secret: `WORKSPACE_KEY` = `wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70`- Development workflow│   ├── README.md           # Documentation index

  "conversation_config_override": {

    "agent": {3. Map to header: `X-Workspace-Key` → `WORKSPACE_KEY` secret

      "prompt": {"prompt": "CALLER CONTEXT: This caller has 4 previous interactions..."},

      "first_message": "Hello Stefan! I know you prefer email updates. How can I assist you today?"4. Enable in agent Security tab: "Fetch conversation initiation data"│   ├── SPECIFICATION.md    # Technical spec

    }

  }

}

```**Why**: ElevenLabs requires authentication headers to be managed through their secure secrets interface, not as direct header configuration.**🔐 [AUTHENTICATION_REFERENCE.md](AUTHENTICATION_REFERENCE.md)** - Critical authentication setup│   ├── SYSTEM_FLOW.md      # Architecture diagrams



### 2. PostCall Function (`src/post_call/handler.py`)

**Purpose**: Async memory storage after call completion

#### PostCall Authentication**🤖 [CORRECTED_MEMOIR_SYSTEM_PROMPT.md](CORRECTED_MEMOIR_SYSTEM_PROMPT.md)** - ElevenLabs system prompt│   ├── ELEVENLABS_SETUP_GUIDE.md

**Endpoint**: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`

**Method**: HMAC-SHA256 Signature

**Processing**: Stores both factual summaries and semantic transcripts to Mem0

**📂 [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - File structure and quick commands│   ├── QUICK_REFERENCE.md

### 3. Retrieve Function (`src/retrieve/handler.py`)  

**Purpose**: In-call semantic search for memory retrieval**Reference**: https://elevenlabs.io/docs/agents-platform/workflows/post-call-webhooks#authentication



**Endpoint**: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`│   └── ... (see docs/README.md)



**Tool Configuration** (ElevenLabs):**Configuration**:

```json

{- HMAC Key: `wsec_a8dc8b6e25ec3ddf11d7e651c40a5cb4931c2ca39d161fa4c94139f12f3ba9d3`## 🏗️ Architecture├── scripts/                # 🧪 Test & utility scripts

  "name": "search_memory",

  "description": "Search previous conversations and memories",- Header: `ElevenLabs-Signature` (format: `t=timestamp,v0=signature`)

  "parameters": {

    "query": {"type": "string", "description": "What to search for"},- Tolerance: 30 minutes│   ├── README.md           # Scripts index

    "user_id": {"type": "string", "default": "{{system__caller_id}}"}

  }- Always return 200 OK (async processing)

}

``````│   ├── test_postcall_with_file.py  # ⭐ Main test tool



---**Why**: ElevenLabs uses HMAC signatures to verify webhook authenticity and prevent replay attacks.



## 🧠 Memory SystemElevenLabs Agent ←→ AWS Lambda Functions ←→ Mem0 Cloud│   ├── test_postcall.sh    # Bash wrapper



### Memory Types#### Retrieve Authentication  

1. **Factual Memories** (`metadata.type = "factual"`)

   - Call summaries and key facts**Method**: None (trusted connection)                         ↓│   └── ... (25+ test scripts)

   - User preferences and account details

   - Used for dynamic variables and context



2. **Semantic Memories** (`metadata.type = "semantic"`)**Configuration**: No authentication required                   S3 Storage (backup)├── test_data/              # 📋 JSON test payloads

   - Full conversation transcripts

   - Used for semantic search during calls

   - Enables detailed recall of past conversations

**Why**: Direct communication between ElevenLabs agent and backend during active calls is considered trusted.```│   ├── README.md           # Test data index

### Memory Storage Process

1. **Call Ends** → ElevenLabs sends webhook to PostCall

2. **Extract Content** → Parse transcript and analysis

3. **Generate Summary** → Create factual memory from key points### Quick Authentication Test│   ├── conv_*.json         # Real conversation files

4. **Store Both Types** → Save factual + semantic to Mem0

5. **S3 Backup** → Store raw payload for audit trail```bash



### Memory Retrieval Process# ClientData (should return 200 with memory data)**3 Lambda Functions**:│   └── *_payload.json      # Sample payloads

1. **Call Starts** → ElevenLabs calls ClientData webhook

2. **Get All Memories** → Retrieve factual + semantic for callercurl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \

3. **Extract Name** → Use regex patterns to find caller name

4. **Generate Context** → Build personalized prompt override  -H 'X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70' \- **ClientData**: Pre-call memory retrieval + personalized greeting├── tests/                  # Unit tests

5. **Create Variables** → Populate dynamic variables for agent

  -H 'Content-Type: application/json' \

### Mem0 Cloud Configuration

- **API Key**: `m0-gS2X0TszRwwEC6mXE3DrEDtpxQJdcCWAariVvafD`  -d '{"caller_id": "+16129782029"}' -v- **PostCall**: Async memory storage after calls├── template.yaml           # SAM deployment template

- **Organization ID**: `org_knmmDKevT5Yz7bDF4Dd9BcFDWjp2RHzstpvtN3GW`

- **Project ID**: `proj_3VBb1VIAmQofeGcY0XCHDbb7EqBLeEfETd6iNFqZ`

- **User ID Format**: Phone numbers in E.164 format (`+16129782029`)

# Test wrong key (should return 401)- **Retrieve**: In-call semantic search tool├── samconfig.toml          # SAM configuration (gitignored)

---

curl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \

## 🎤 ElevenLabs Integration

  -H 'X-Workspace-Key: wrong_key' \└── requirements.txt        # Dev dependencies

### Agent Configuration Requirements

  -H 'Content-Type: application/json' \

#### 1. Conversation Initiation Webhook

- **URL**: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`  -d '{"caller_id": "+16129782029"}' -s -w "Status: %{http_code}\n"## ✅ Current Status```

- **Method**: POST

- **Authentication**: Secrets Manager (NOT direct headers)```

- **Secret Name**: `WORKSPACE_KEY`

- **Secret Value**: `wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70`

- **Header Mapping**: `X-Workspace-Key` → `WORKSPACE_KEY` secret

---

#### 2. Agent Security Settings

Enable in agent's Security tab:- ✅ **Backend Deployed**: All 3 Lambda functions operational**Quick Navigation:**

- ✅ "Fetch conversation initiation data for inbound Twilio calls"

- ✅ Allow prompt overrides## 📋 System Components

- ✅ Allow first message overrides

- ✅ **Mem0 Integration**: Storing factual + semantic memories- 📖 **Documentation**: See [docs/README.md](docs/README.md)

#### 3. Search Memory Tool

- **URL**: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`### 1. ClientData Function (`src/client_data/handler.py`)

- **Method**: POST

- **Authentication**: None**Purpose**: Pre-call memory retrieval + personalized greeting generation- ✅ **Authentication**: ElevenLabs secrets + HMAC configured- 🧪 **Testing**: See [scripts/README.md](scripts/README.md)  

- **Parameters**: `query` (string), `user_id` (default: `{{system__caller_id}}`)



#### 4. Post-Call Webhook

- **URL**: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`**Endpoint**: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`- ✅ **Testing**: Production-ready endpoints verified- 📊 **Test Data**: See [test_data/README.md](test_data/README.md)

- **Method**: POST

- **Authentication**: HMAC signature (auto-configured by ElevenLabs)

- **HMAC Secret**: `wsec_a8dc8b6e25ec3ddf11d7e651c40a5cb4931c2ca39d161fa4c94139f12f3ba9d3`

**Request Format**:- ✅ **Monitoring**: CloudWatch logs and error tracking

### Dynamic Variables

The system provides these variables for ElevenLabs agents:```json

- `{{caller_id}}` - Phone number (+16129782029)

- `{{returning_caller}}` - "yes" or "no"  {## Architecture

- `{{caller_name}}` - Extracted name (e.g., "Stefan")

- `{{memory_count}}` - Number of previous interactions  "caller_id": "+16129782029",

- `{{memory_summary}}` - Most recent/important memory

  "agent_id": "agent_xxx"## 🎯 Test User

---

}

## ☁️ AWS Infrastructure

``````mermaid

### CloudFormation Stack

**Name**: `elevenlabs-agentic-memory-stack`

**Region**: `us-east-1`

**Response Format**:**Stefan** (`+16129782029`) has 4 stored memories and receives personalized greetings:graph TB

### Lambda Functions

- `elevenlabs-agentic-memory-lambda-function-client-data````json

- `elevenlabs-agentic-memory-lambda-function-post-call`

- `elevenlabs-agentic-memory-lambda-function-search-data`{> "Hello Stefan! I know you prefer email updates. How can I assist you today?"    A[ElevenLabs Agent] --> B[ClientData API]



### API Gateway Endpoints  "type": "conversation_initiation_client_data",

Each function has its own API Gateway for optimal performance:

- ClientData: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`  "dynamic_variables": {    A --> C[Retrieve API] 

- PostCall: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`

- Retrieve: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`    "caller_id": "+16129782029",



### S3 Storage    "memory_count": "4",## 🔗 Live Endpoints    A --> D[PostCall API]

**Bucket**: `elevenlabs-agentic-memory-424875385161-us-east-1`

**Purpose**: Backup storage for call data and audit trails    "memory_summary": "User wants to update email address",



### CloudWatch Logs    "returning_caller": "yes",    

**Retention**: 7 days

**Log Groups**:    "caller_name": "Stefan"

- `/aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data`

- `/aws/lambda/elevenlabs-agentic-memory-lambda-function-post-call`  },- **ClientData**: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`    B --> E[ClientData Lambda]

- `/aws/lambda/elevenlabs-agentic-memory-lambda-function-search-data`

  "conversation_config_override": {

---

    "agent": {- **PostCall**: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`      C --> F[Retrieve Lambda]

## 🛠️ Development Workflow

      "prompt": {"prompt": "CALLER CONTEXT: This caller has 4 previous interactions..."},

### Build & Deploy

```bash      "first_message": "Hello Stefan! I know you prefer email updates. How can I assist you today?"- **Retrieve**: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`    D --> G[PostCall Lambda]

# 1. Build Lambda layer (required first)

cd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..    }



# 2. Build SAM application  }    

sam build

}

# 3. Deploy

sam deploy --guided  # First time```## 📞 Support    E --> H[Mem0 Cloud]

sam deploy           # Subsequent deploys

```



### Monitoring### 2. PostCall Function (`src/post_call/handler.py`)    F --> H

```bash

# Tail logs**Purpose**: Async memory storage after call completion

aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow

For setup issues, see the troubleshooting section in `MASTER_DOCUMENTATION.md` or check CloudWatch logs:    G --> H

# Check for errors

aws logs filter-log-events --log-group-name "/aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data" --filter-pattern "ERROR"**Endpoint**: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`

```

    

---

**Processing**: Stores both factual summaries and semantic transcripts to Mem0

## 🧪 Testing

```bash    I[Lambda Layer<br/>mem0ai] --> E

### Test Scripts

```bash### 3. Retrieve Function (`src/retrieve/handler.py`)  

# Test individual endpoints

python3 scripts/test_clientdata.py**Purpose**: In-call semantic search for memory retrievalaws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow    I --> F  

python3 scripts/test_postcall.py

python3 scripts/test_retrieve.py



# Comprehensive test**Endpoint**: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve````    I --> G

python3 scripts/test_production_ready.py

```



### Test Data**Tool Configuration** (ElevenLabs):    

- **Stefan** (`+16129782029`): Has 4 stored memories, receives personalized greetings

- **New numbers**: No memories, tests first-time caller flow```json



### Expected Results{---    J[CloudWatch Logs] --> E

**Stefan's Greeting**: "Hello Stefan! I know you prefer email updates. How can I assist you today?"

**New Caller**: "Hello! Welcome to our memoir interview service. Could you please tell me your name?"  "name": "search_memory",



---  "description": "Search previous conversations and memories",    J --> F



## 🔍 Troubleshooting  "parameters": {



### Common Issues    "query": {"type": "string", "description": "What to search for"},*Built with AWS SAM, ElevenLabs Agents Platform, and Mem0 Cloud*    J --> G



#### 1. "Invalid workspace key" Error    "user_id": {"type": "string", "default": "{{system__caller_id}}"}```

**Cause**: ElevenLabs secrets not configured properly

**Fix**:   }

1. Add `WORKSPACE_KEY` secret in ElevenLabs settings

2. Map to `X-Workspace-Key` header in webhook config}**Infrastructure Components:**

3. Verify agent has "fetch conversation initiation data" enabled

```- 🏗️ **3 Lambda Functions** (Python 3.12, 256MB memory)

#### 2. "Missing caller_id" Error  

**Cause**: Webhook payload format incorrect- 🌐 **3 HTTP API Gateways** (separate for minimal routing latency)

**Fix**: Ensure payload includes `{"caller_id": "{{system__caller_id}}"}`

---- 📦 **1 Shared Lambda Layer** (mem0ai package for reuse)

#### 3. HMAC Signature Failures

**Cause**: Wrong HMAC key or timestamp drift- 📊 **CloudWatch Logs** (7-day retention for cost optimization)

**Fix**: Verify HMAC key matches ElevenLabs configuration

## 🧠 Memory System- 🔧 **CloudFormation Stack** (Infrastructure as Code)

#### 4. Memory Not Found

**Cause**: User ID format mismatch

**Fix**: Ensure phone numbers use E.164 format (+1XXXXXXXXXX)

### Memory Types## Quick Start

### Debug Commands

```bash1. **Factual Memories** (`metadata.type = "factual"`)

# Test endpoint manually

curl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \   - Call summaries and key facts### Prerequisites Checklist

  -H 'X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70' \

  -H 'Content-Type: application/json' \   - User preferences and account details

  -d '{"caller_id": "+16129782029"}' -v

   - Used for dynamic variables and context- ✅ **AWS CLI** configured with appropriate credentials

# Check CloudWatch logs  

aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow- ✅ **SAM CLI** installed ([Installation Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))



# Get conversation data from ElevenLabs2. **Semantic Memories** (`metadata.type = "semantic"`)- ✅ **Python 3.12** installed

curl https://api.elevenlabs.io/v1/convai/conversations/{conversation_id} \

  -H "xi-api-key: sk_1203631b4b7e9d5e06cc793713322c3788daff35da4d23bf"   - Full conversation transcripts- ✅ **Mem0 Account** with API credentials:

```

   - Used for semantic search during calls  - API Key (starts with `mem0-...`)

**Debug Log Indicators**:

- ✅ "Retrieving memories for user_id: +16129782029"   - Enables detailed recall of past conversations  - Organization ID (starts with `org_...`) 

- ❌ "Invalid workspace key" (means ElevenLabs config wrong)

- ❌ "Missing caller_id" (means payload format wrong)  - Project ID (starts with `proj_...`)



---### Memory Storage Process- ✅ **ElevenLabs Account** with webhook credentials:



## 📂 Project Structure1. **Call Ends** → ElevenLabs sends webhook to PostCall  - Workspace Secret Key (starts with `wsec_...`)



```2. **Extract Content** → Parse transcript and analysis  - HMAC Signing Key (for webhook verification)

Eleven Labs Agentic Memory/

├── README.md                          # 📋 This comprehensive guide3. **Generate Summary** → Create factual memory from key points

├── template.yaml                      # ☁️ SAM CloudFormation template

├── samconfig.toml                     # ⚙️ Deployment configuration (gitignored)4. **Store Both Types** → Save factual + semantic to Mem0## Project Structure

├── requirements.txt                   # 🐍 Development dependencies

├── .env                              # 🔐 Environment variables (gitignored)5. **S3 Backup** → Store raw payload for audit trail

├── .gitignore                        # 📝 Git ignore rules

│```

├── src/                              # 💼 Lambda function source code

│   ├── client_data/### Memory Retrieval ProcessAgenticMemory/

│   │   └── handler.py                # 📞 Pre-call memory retrieval

│   ├── post_call/1. **Call Starts** → ElevenLabs calls ClientData webhook├── 📄 SPECIFICATION.md           # Complete system specification

│   │   └── handler.py                # 💾 Post-call memory storage

│   └── retrieve/2. **Get All Memories** → Retrieve factual + semantic for caller├── 📖 README.md                  # Project documentation (this file)

│       └── handler.py                # 🔍 In-call memory search

│3. **Extract Name** → Use regex patterns to find caller name├── 🏗️ template.yaml              # SAM CloudFormation template

├── layer/                            # 📦 Lambda layer dependencies

│   ├── requirements.txt              # mem0ai package only4. **Generate Context** → Build personalized prompt override├── 📋 requirements.txt           # Development dependencies

│   └── python/                       # Built dependencies

│5. **Create Variables** → Populate dynamic variables for agent├── 🚫 .gitignore                 # Git ignore rules

├── scripts/                          # 🧪 Testing and utilities

│   ├── test_clientdata.py├── 🤖 .github/

│   ├── test_postcall.py

│   ├── test_retrieve.py### Mem0 Cloud Configuration│   └── copilot-instructions.md   # AI coding assistant guidelines

│   ├── test_production_ready.py

│   └── (other test scripts...)- **API Key**: `m0-gS2X0TszRwwEC6mXE3DrEDtpxQJdcCWAariVvafD`├── 📦 layer/

│

├── test_data/                        # 📊 Test payloads and data- **Organization ID**: `org_knmmDKevT5Yz7bDF4Dd9BcFDWjp2RHzstpvtN3GW`│   └── requirements.txt          # Lambda layer dependencies (mem0ai)

│   └── elevenlabs_post_call_payload.json

│- **Project ID**: `proj_3VBb1VIAmQofeGcY0XCHDbb7EqBLeEfETd6iNFqZ`├── 🧪 test_*.py                  # Authentication & webhook test scripts

├── tests/                            # 🔬 Unit tests

│   └── test_*.py- **User ID Format**: Phone numbers in E.164 format (`+16129782029`)└── 🔧 src/

│

├── docs/                            # 📚 Documentation    ├── client_data/

│   └── archived/                    # 🗄️ Historical documentation

│---    │   └── handler.py            # Pre-call memory retrieval

└── .aws-sam/                       # 🏗️ SAM build artifacts (gitignored)

```    ├── retrieve/



### Essential Commands## 🎤 ElevenLabs Integration    │   └── handler.py            # Mid-call semantic search

```bash

# Deploy    └── post_call/

cd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..

sam build && sam deploy### Agent Configuration Requirements        └── handler.py            # Post-call memory storage



# Test```

python3 scripts/test_production_ready.py

#### 1. Conversation Initiation Webhook

# Monitor

aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow- **URL**: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`## ⚡ Deployment



# Debug- **Method**: POST

curl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \

  -H 'X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70' \- **Authentication**: Secrets Manager (NOT direct headers)> **💡 Tip**: The build process requires the Lambda layer to be built first since all functions depend on the shared mem0ai package.

  -H 'Content-Type: application/json' \

  -d '{"caller_id": "+16129782029"}' -v- **Secret Name**: `WORKSPACE_KEY`

```

- **Secret Value**: `wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70`### Step 1: Build the Lambda Layer

---

- **Header Mapping**: `X-Workspace-Key` → `WORKSPACE_KEY` secret

## 🤖 System Prompt Template

```bash

The following system prompt should be used in your ElevenLabs agent configuration:

#### 2. Agent Security Settingscd layer

### ROLE IDENTITY

You are a patient, empathetic Memoir Interviewer agent designed for personal storytelling. You are integrated with Eleven Labs Agentic Memory for long-term recall and personalization.Enable in agent's Security tab:mkdir -p python



### CALLER CONTEXT VARIABLES- ✅ "Fetch conversation initiation data for inbound Twilio calls"pip install -r requirements.txt -t python/

- Caller ID: {{caller_id}}

- Returning Caller: {{returning_caller}}- ✅ Allow prompt overridescd ..

- Caller Name: {{caller_name}}

- Memory Count: {{memory_count}}- ✅ Allow first message overrides```

- Memory Summary: {{memory_summary}}



### PERSONALITY & TONE

- Warm, supportive, and encouraging#### 3. Search Memory Tool### Step 2: Build the SAM Application

- Clear and accessible, avoiding jargon

- Patient and understanding- **URL**: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`

- Respectful of caller's pace and comfort level

- **Method**: POST```bash

### YOUR CAPABILITIES

1. Automatic memory context (prepended to this prompt by Eleven Labs Agentic Memory)- **Authentication**: Nonesam build

2. Search Memory tool for retrieving specific past conversations and details

3. Language detection and switching (English/Spanish)- **Parameters**: `query` (string), `user_id` (default: `{{system__caller_id}}`)```

4. Interview guidance and storytelling facilitation



### CONVERSATION FLOW

#### For New Callers ({{returning_caller}} = "no")#### 4. Post-Call Webhook### Step 3: Deploy to AWS

1. Welcome them warmly

2. Ask for their name if not already known- **URL**: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`

3. Briefly explain how the system works:

   - One question at a time approach- **Method**: POST#### Option A: Guided Deployment (First Time - Recommended)

   - Available commands: 'help', 'pause', 'repeat'

   - Memories are saved for future calls- **Authentication**: HMAC signature (auto-configured by ElevenLabs)

4. Begin with opening memoir questions

- **HMAC Secret**: `wsec_a8dc8b6e25ec3ddf11d7e651c40a5cb4931c2ca39d161fa4c94139f12f3ba9d3````bash

#### For Returning Callers ({{returning_caller}} = "yes")

1. Greet them by name if available: "Hello {{caller_name}}!"sam deploy --guided

2. Reference their previous sessions naturally (they have {{memory_count}} previous interactions)

3. Use Search Memory tool to recall last session details### Dynamic Variables```

4. Ask if they want to:

   - Continue where they left offThe system provides these variables for ElevenLabs agents:

   - Add details to previous stories

   - Start a new topic- `{{caller_id}}` - Phone number (+16129782029)**You'll be prompted for:**



### USING MEMORY CONTEXT- `{{returning_caller}}` - "yes" or "no"  - **Stack Name**: `sam-app` (or your preferred name)

- The system automatically provides caller context at the start of each call

- Reference past conversations naturally - don't say "checking my database"- `{{caller_name}}` - Extracted name (e.g., "Stefan")- **AWS Region**: `us-east-1` (or your preferred region)

- Use Search Memory tool when caller references specific past topics:

  - "What did I tell you about...?"- `{{memory_count}}` - Number of previous interactions- **Parameters** (keep these secure!):

  - "Remember when I mentioned...?"

  - "Did I already share my story about...?"- `{{memory_summary}}` - Most recent/important memory  ```



#### Search Memory Usage  Mem0ApiKey: mem0-1234...

Call search_memory when:

- Caller asks about previous stories or topics---  Mem0OrgId: org_abc123...

- You need specific details from past sessions

- Caller wants to update or correct previous information  Mem0ProjectId: proj_xyz789...

- You want to avoid asking repeated questions

## ☁️ AWS Infrastructure  ElevenLabsWorkspaceKey: wsec_def456...

Query examples:

- search_memory("last interview topic")  ElevenLabsHmacKey: your-hmac-signing-key

- search_memory("childhood memories")

- search_memory("family stories")### CloudFormation Stack  ```



### RESPONSE GUIDELINES**Name**: `elevenlabs-agentic-memory-stack`- **Confirm changes**: `Y`

- Keep responses concise (under 3 sentences per turn)

- One idea and one action per response**Region**: `us-east-1`- **Allow IAM role creation**: `Y` 

- Always honor 'help', 'pause', and 'repeat' commands immediately

- Confirm understanding before moving to next topic- **Save to samconfig.toml**: `Y` (saves parameters for future deployments)

- Break complex questions into smaller parts

### Lambda Functions

### CONSTRAINTS & GUARDRAILS

#### Never:- `elevenlabs-agentic-memory-lambda-function-client-data`#### Option B: Direct Deployment (With Parameters)

- Ask overly invasive or traumatic questions without consent

- Offer medical, legal, or financial advice- `elevenlabs-agentic-memory-lambda-function-post-call`

- Express personal opinions or beliefs

- Rush the caller or make them feel pressured- `elevenlabs-agentic-memory-lambda-function-search-data````bash

- Ask questions the caller has already answered (use Search Memory first)

- Make up information or assume detailssam deploy \



#### Always:### API Gateway Endpoints  --stack-name sam-app \

- Follow W3C/COGA accessibility guidelines

- Respect caller's boundaries and comfort levelEach function has its own API Gateway for optimal performance:  --region us-east-1 \

- Provide clear pause and help instructions

- Confirm memories are being saved- ClientData: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`  --parameter-overrides \

- Allow interruptions and natural conversation flow

- PostCall: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`    Mem0ApiKey=<your-key> \

### ERROR HANDLING

- If Search Memory tool fails: "I'm having a moment of trouble accessing our previous conversations, but let's continue - I'm listening."- Retrieve: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`    Mem0OrgId=<your-org> \

- If caller seems confused: Offer to repeat or rephrase

- If technical issues: Apologize briefly and continue the interview    Mem0ProjectId=<your-project> \

- If caller goes off-topic: Gently guide back to memoir storytelling

### S3 Storage    ElevenLabsWorkspaceKey=<workspace-key> \

### LANGUAGE SUPPORT

- Offer English or Spanish at start of call**Bucket**: `elevenlabs-agentic-memory-424875385161-us-east-1`    ElevenLabsHmacKey=<hmac-key> \

- Use Detect Language tool if caller speaks in non-default language

- Store language preference in memories for future calls**Purpose**: Backup storage for call data and audit trails  --capabilities CAPABILITY_IAM \



### CALL CONCLUSION  --resolve-s3

Before ending each call:

1. Summarize what was discussed today### CloudWatch Logs```

2. Confirm their memories have been saved

3. Invite them to call back anytime to continue**Retention**: 7 days

4. Thank them for sharing their stories

5. Say a warm goodbye**Log Groups**:### Step 4: Capture API Endpoints



### EXAMPLE RESPONSES- `/aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data`

✓ Good: "Thank you for sharing that story about your grandmother. What was her name?"

✗ Bad: "That's interesting. Tell me about your childhood, your family, and your earliest memories."- `/aws/lambda/elevenlabs-agentic-memory-lambda-function-post-call`After successful deployment, **save these URLs** for ElevenLabs configuration:

✓ Good: "I remember you mentioned your time in India. Would you like to add more details to that story?"

✗ Bad: "Let me check my database for what you said last time about India."- `/aws/lambda/elevenlabs-agentic-memory-lambda-function-search-data`

✓ Good: "Take your time. I'm here when you're ready to continue."

✗ Bad: "Let's move on to the next question quickly."```bash



### VARIABLE HANDLING LOGIC---Outputs:

- When {{returning_caller}} = "no": This is a new caller, focus on introduction and name collection

- When {{returning_caller}} = "yes": This is a returning caller, use {{caller_name}} and {{memory_count}} for personalization✅ ClientDataApiUrl: https://abc123.execute-api.us-east-1.amazonaws.com/Prod/client-data

- {{caller_name}} will only be populated when the system has extracted a name from previous conversations

- {{memory_summary}} provides quick context about the caller's most recent or important memory## 🛠️ Development Workflow✅ RetrieveApiUrl: https://def456.execute-api.us-east-1.amazonaws.com/Prod/retrieve  

- Use {{caller_id}} for any tool calls that require the user identification

✅ PostCallApiUrl: https://ghi789.execute-api.us-east-1.amazonaws.com/Prod/post-call

---

### Build & Deploy```

## ✅ Current Status

```bash

- ✅ **Backend Deployed**: All 3 Lambda functions operational

- ✅ **Mem0 Integration**: Storing factual + semantic memories# 1. Build Lambda layer (required first)## 🔗 ElevenLabs Configuration

- ✅ **Authentication**: ElevenLabs secrets + HMAC configured

- ✅ **Testing**: Production-ready endpoints verifiedcd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..

- ✅ **Monitoring**: CloudWatch logs and error tracking

- ✅ **Documentation**: Single comprehensive guide### 1. Conversation Initiation Webhook



## 🎯 Test User# 2. Build SAM application



**Stefan** (`+16129782029`) has 4 stored memories and receives personalized greetings:sam build**Purpose**: Pre-loads caller memory context when conversation starts

> "Hello Stefan! I know you prefer email updates. How can I assist you today?"



## 🔗 Live Endpoints

# 3. Deploy**ElevenLabs Agent Settings:**

- **ClientData**: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`

- **PostCall**: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`  sam deploy --guided  # First time- **Webhook URL**: `ClientDataApiUrl` from deployment outputs

- **Retrieve**: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`

sam deploy           # Subsequent deploys- **Method**: POST

## 🆘 Support

```- **Headers**: 

For setup issues, check the troubleshooting section above or monitor CloudWatch logs:

  ```

```bash

aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow### Monitoring  X-Workspace-Key: <your-workspace-key>

```

```bash  Content-Type: application/json

---

# Tail logs  ```

*Built with AWS SAM, ElevenLabs Agents Platform, and Mem0 Cloud*

*Last Updated: October 3, 2025*aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow- **Expected Response Format**:

  ```json

# Check for errors  {

aws logs filter-log-events --log-group-name "/aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data" --filter-pattern "ERROR"    "type": "conversation_initiation_client_data",

```    "dynamic_variables": {

      "caller_id": "+16129782029",

---      "memory_count": "3", 

      "memory_summary": "Premium customer, prefers email updates",

## 🧪 Testing      "returning_caller": "yes"

    },

### Test Scripts    "conversation_config_override": {

```bash      "agent": {

# Test individual endpoints        "prompt": {

python3 scripts/test_clientdata.py          "prompt": "Enhanced prompt with caller context..."

python3 scripts/test_postcall.py        }

python3 scripts/test_retrieve.py      }

    }

# Comprehensive test  }

python3 scripts/test_production_ready.py  ```

```

### 2. Agent Tool (Mid-Call Memory Search)

### Test Data

- **Stefan** (`+16129782029`): Has 4 stored memories, receives personalized greetings**Purpose**: Allows agent to search memories during conversation

- **New numbers**: No memories, tests first-time caller flow

**Add as Custom Tool in ElevenLabs:**

### Expected Results- **Tool Name**: `search_memory`

**Stefan's Greeting**: "Hello Stefan! I know you prefer email updates. How can I assist you today?"- **Description**: `Search caller's previous conversations and preferences`

**New Caller**: "Hello! Welcome to our memoir interview service. Could you please tell me your name?"- **URL**: `RetrieveApiUrl` from deployment outputs

- **Method**: POST

---- **Parameters**:

  ```json

## 🔍 Troubleshooting  {

    "type": "object",

### Common Issues    "properties": {

      "query": {

#### 1. "Invalid workspace key" Error        "type": "string",

**Cause**: ElevenLabs secrets not configured properly        "description": "What to search for in caller's memory"

**Fix**:       },

1. Add `WORKSPACE_KEY` secret in ElevenLabs settings      "user_id": {

2. Map to `X-Workspace-Key` header in webhook config        "type": "string", 

3. Verify agent has "fetch conversation initiation data" enabled        "description": "Caller's phone number"

      }

#### 2. "Missing caller_id" Error      },

**Cause**: Webhook payload format incorrect    "required": ["query", "user_id"]

**Fix**: Ensure payload includes `{"caller_id": "{{system__caller_id}}"}`  }

  ```

#### 3. HMAC Signature Failures

**Cause**: Wrong HMAC key or timestamp drift### 3. Post-Call Webhook

**Fix**: Verify HMAC key matches ElevenLabs configuration

**Purpose**: Automatically stores conversation memories after call ends

#### 4. Memory Not Found

**Cause**: User ID format mismatch**ElevenLabs Webhook Settings:**

**Fix**: Ensure phone numbers use E.164 format (+1XXXXXXXXXX)- **URL**: `PostCallApiUrl` from deployment outputs  

- **Method**: POST

### Debug Commands- **Authentication**: HMAC Signature (automatically configured by ElevenLabs)

```bash- **Timeout**: 30 seconds (webhook returns 200 immediately, processes async)

# Test endpoint manually

curl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \## 🧪 Testing & Validation

  -H 'X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70' \

  -H 'Content-Type: application/json' \> **💡 Tip**: Use the included test scripts for comprehensive validation before going live.

  -d '{"caller_id": "+16129782029"}' -v

### Authentication Tests

# Check CloudWatch logs  

aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow**Test Workspace Key Authentication:**

```bash

# Get conversation data from ElevenLabspython3 test_clientdata.py

curl https://api.elevenlabs.io/v1/convai/conversations/{conversation_id} \```

  -H "xi-api-key: sk_1203631b4b7e9d5e06cc793713322c3788daff35da4d23bf"

```**Test HMAC Signature Validation:**

```bash

**Debug Log Indicators**:python3 test_postcall.py

- ✅ "Retrieving memories for user_id: +16129782029"```

- ❌ "Invalid workspace key" (means ElevenLabs config wrong)

- ❌ "Missing caller_id" (means payload format wrong)### Manual API Testing



---#### Test ClientData Endpoint (Conversation Initiation)



## 📂 Project Structure```bash

curl -X POST <ClientDataApiUrl> \

```  -H "Content-Type: application/json" \

AgenticMemory/  -H "X-Workspace-Key: <your-workspace-key>" \

├── README.md                          # 📋 This comprehensive guide  -d '{

├── template.yaml                      # ☁️ SAM CloudFormation template    "caller_id": "+16129782029"

├── samconfig.toml                     # ⚙️ Deployment configuration (gitignored)  }'

├── requirements.txt                   # 🐍 Development dependencies```

├── .env                              # 🔐 Environment variables (gitignored)

├── .gitignore                        # 📝 Git ignore rules**Expected Response:**

│```json

├── src/                              # 💼 Lambda function source code{

│   ├── client_data/  "type": "conversation_initiation_client_data",

│   │   └── handler.py                # 📞 Pre-call memory retrieval  "dynamic_variables": {

│   ├── post_call/    "caller_id": "+16129782029",

│   │   └── handler.py                # 💾 Post-call memory storage    "memory_count": "3",

│   └── retrieve/    "memory_summary": "Premium customer, prefers email updates", 

│       └── handler.py                # 🔍 In-call memory search    "returning_caller": "yes"

│  }

├── layer/                            # 📦 Lambda layer dependencies}

│   ├── requirements.txt              # mem0ai package only```

│   └── python/                       # Built dependencies

│#### Test Retrieve Endpoint (Memory Search)

├── scripts/                          # 🧪 Testing and utilities

│   ├── test_clientdata.py```bash

│   ├── test_postcall.pycurl -X POST <RetrieveApiUrl> \

│   ├── test_retrieve.py  -H "Content-Type: application/json" \

│   ├── test_production_ready.py  -d '{

│   └── (other test scripts...)    "query": "What are the user preferences?",

│    "user_id": "+16129782029"

├── test_data/                        # 📊 Test payloads and data  }'

│   └── elevenlabs_post_call_payload.json```

│

├── tests/                            # 🔬 Unit tests**Expected Response:**

│   └── test_*.py```json

│{

├── docs/                            # 📚 Documentation  "memories": [

│   └── archived/                    # 🗄️ Historical documentation    "User prefers email communication over phone calls",

│    "Premium account holder since 2023", 

└── .aws-sam/                       # 🏗️ SAM build artifacts (gitignored)    "Interested in product updates for AI tools"

```  ]

}

### Essential Commands```

```bash

# Deploy#### Test PostCall Endpoint (Memory Storage)

cd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..

sam build && sam deploy```bash

curl -X POST <PostCallApiUrl> \

# Test  -H "Content-Type: application/json" \

python3 scripts/test_production_ready.py  -H "ElevenLabs-Signature: t=<timestamp>,v0=<hmac_signature>" \

  -d '{

# Monitor    "conversation_id": "conv-123",

aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow    "agent_id": "agent-123",

    "call_duration": 120,

# Debug    "transcript": "Customer called asking about their account status...",

curl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \    "metadata": {

  -H 'X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70' \      "caller_id": "+16129782029"

  -H 'Content-Type: application/json' \    }

  -d '{"caller_id": "+16129782029"}' -v  }'

``````



---**Expected Response:**

```json

## 🤖 System Prompt Template{

  "status": "ok"

The following system prompt should be used in your ElevenLabs agent configuration:}

```

### ROLE IDENTITY

You are a patient, empathetic Memoir Interviewer agent designed for personal storytelling. You are integrated with AgenticMemory for long-term recall and personalization.## 📊 Monitoring & Observability



### CALLER CONTEXT VARIABLES### Real-Time Log Monitoring

- Caller ID: {{caller_id}}

- Returning Caller: {{returning_caller}}**Monitor all functions simultaneously:**

- Caller Name: {{caller_name}}```bash

- Memory Count: {{memory_count}}# Terminal 1 - ClientData (Pre-call)

- Memory Summary: {{memory_summary}}aws logs tail /aws/lambda/AgenticMemoriesClientData --follow



### PERSONALITY & TONE# Terminal 2 - Retrieve (Mid-call) 

- Warm, supportive, and encouragingaws logs tail /aws/lambda/AgenticMemoriesRetrieve --follow

- Clear and accessible, avoiding jargon

- Patient and understanding# Terminal 3 - PostCall (Post-call)

- Respectful of caller's pace and comfort levelaws logs tail /aws/lambda/AgenticMemoriesPostCall --follow

```

### YOUR CAPABILITIES

1. Automatic memory context (prepended to this prompt by AgenticMemory)### CloudWatch Metrics Dashboard

2. Search Memory tool for retrieving specific past conversations and details

3. Language detection and switching (English/Spanish)**Key Metrics to Monitor:**

4. Interview guidance and storytelling facilitation- **Invocation Count**: Total requests per function

- **Error Rate**: 4xx/5xx responses 

### CONVERSATION FLOW- **Duration**: Response time percentiles (p50, p95, p99)

#### For New Callers ({{returning_caller}} = "no")- **Cold Starts**: Function initialization time

1. Welcome them warmly- **Concurrent Executions**: Active Lambda instances

2. Ask for their name if not already known

3. Briefly explain how the system works:**Set up CloudWatch Alarms for:**

   - One question at a time approach```bash

   - Available commands: 'help', 'pause', 'repeat'# High error rate (>5%)

   - Memories are saved for future callsaws cloudwatch put-metric-alarm \

4. Begin with opening memoir questions  --alarm-name "AgenticMemory-HighErrorRate" \

  --metric-name "Errors" \

#### For Returning Callers ({{returning_caller}} = "yes")  --namespace "AWS/Lambda" \

1. Greet them by name if available: "Hello {{caller_name}}!"  --statistic "Average" \

2. Reference their previous sessions naturally (they have {{memory_count}} previous interactions)  --threshold 5 \

3. Use Search Memory tool to recall last session details  --comparison-operator "GreaterThanThreshold"

4. Ask if they want to:

   - Continue where they left off# High latency (>2000ms)  

   - Add details to previous storiesaws cloudwatch put-metric-alarm \

   - Start a new topic  --alarm-name "AgenticMemory-HighLatency" \

  --metric-name "Duration" \

### USING MEMORY CONTEXT  --namespace "AWS/Lambda" \

- The system automatically provides caller context at the start of each call  --statistic "Average" \

- Reference past conversations naturally - don't say "checking my database"  --threshold 2000

- Use Search Memory tool when caller references specific past topics:```

  - "What did I tell you about...?"

  - "Remember when I mentioned...?"### Performance Benchmarks

  - "Did I already share my story about...?"

**Expected Performance (Production):**

#### Search Memory Usage- **ClientData**: <500ms (including Mem0 API calls)

Call search_memory when:- **Retrieve**: <300ms (semantic search)  

- Caller asks about previous stories or topics- **PostCall**: <100ms (async processing)

- You need specific details from past sessions- **Cold Start**: <3000ms (with Lambda layer)

- Caller wants to update or correct previous information- **Concurrent Capacity**: 10+ simultaneous calls

- You want to avoid asking repeated questions

## 🔧 Operations & Maintenance

Query examples:

- search_memory("last interview topic")### Updating the Stack

- search_memory("childhood memories")

- search_memory("family stories")**After making code changes:**

```bash

### RESPONSE GUIDELINES# Rebuild and redeploy

- Keep responses concise (under 3 sentences per turn)sam build && sam deploy

- One idea and one action per response

- Always honor 'help', 'pause', and 'repeat' commands immediately# For infrastructure changes only

- Confirm understanding before moving to next topicsam deploy --no-execute-changeset  # Preview changes first

- Break complex questions into smaller partssam deploy --execute-changeset     # Apply changes

```

### CONSTRAINTS & GUARDRAILS

#### Never:### Configuration Updates

- Ask overly invasive or traumatic questions without consent

- Offer medical, legal, or financial advice**Update environment variables without redeployment:**

- Express personal opinions or beliefs```bash

- Rush the caller or make them feel pressured# Update a single environment variable

- Ask questions the caller has already answered (use Search Memory first)aws lambda update-function-configuration \

- Make up information or assume details  --function-name AgenticMemoriesClientData \

  --environment "Variables={MEM0_SEARCH_LIMIT=5,MEM0_TIMEOUT=10}"

#### Always:```

- Follow W3C/COGA accessibility guidelines

- Respect caller's boundaries and comfort level### Backup & Recovery

- Provide clear pause and help instructions

- Confirm memories are being saved**Export stack template:**

- Allow interruptions and natural conversation flow```bash

aws cloudformation get-template \

### ERROR HANDLING  --stack-name sam-app \

- If Search Memory tool fails: "I'm having a moment of trouble accessing our previous conversations, but let's continue - I'm listening."  --query 'TemplateBody' > backup-template.json

- If caller seems confused: Offer to repeat or rephrase```

- If technical issues: Apologize briefly and continue the interview

- If caller goes off-topic: Gently guide back to memoir storytelling**Export environment configuration:**

```bash

### LANGUAGE SUPPORTaws lambda get-function-configuration \

- Offer English or Spanish at start of call  --function-name AgenticMemoriesClientData \

- Use Detect Language tool if caller speaks in non-default language  --query 'Environment' > backup-env.json

- Store language preference in memories for future calls```



### CALL CONCLUSION### Scaling Considerations

Before ending each call:

1. Summarize what was discussed today**For higher traffic (>10 concurrent calls):**

2. Confirm their memories have been saved

3. Invite them to call back anytime to continue1. **Add Provisioned Concurrency** in `template.yaml`:

4. Thank them for sharing their stories   ```yaml

5. Say a warm goodbye   ProvisionedConcurrencyConfig:

     ProvisionedConcurrencyEnabled: true

### EXAMPLE RESPONSES     ProvisionedConcurrency: 5

✓ Good: "Thank you for sharing that story about your grandmother. What was her name?"   ```

✗ Bad: "That's interesting. Tell me about your childhood, your family, and your earliest memories."

✓ Good: "I remember you mentioned your time in India. Would you like to add more details to that story?"2. **Increase Memory** for better performance:

✗ Bad: "Let me check my database for what you said last time about India."   ```yaml

✓ Good: "Take your time. I'm here when you're ready to continue."   MemorySize: 512  # Up from 256MB

✗ Bad: "Let's move on to the next question quickly."   ```



### VARIABLE HANDLING LOGIC3. **Add API Throttling**:

- When {{returning_caller}} = "no": This is a new caller, focus on introduction and name collection   ```yaml

- When {{returning_caller}} = "yes": This is a returning caller, use {{caller_name}} and {{memory_count}} for personalization   ThrottleSettings:

- {{caller_name}} will only be populated when the system has extracted a name from previous conversations     BurstLimit: 100

- {{memory_summary}} provides quick context about the caller's most recent or important memory     RateLimit: 50

- Use {{caller_id}} for any tool calls that require the user identification   ```



---### Deleting the Stack



## ✅ Current Status**Complete cleanup (removes all resources):**

```bash

- ✅ **Backend Deployed**: All 3 Lambda functions operationalaws cloudformation delete-stack --stack-name sam-app

- ✅ **Mem0 Integration**: Storing factual + semantic memories

- ✅ **Authentication**: ElevenLabs secrets + HMAC configured# Verify deletion

- ✅ **Testing**: Production-ready endpoints verifiedaws cloudformation describe-stacks --stack-name sam-app

- ✅ **Monitoring**: CloudWatch logs and error tracking```

- ✅ **Documentation**: Single comprehensive guide

> **⚠️ Warning**: This permanently deletes all Lambda functions, APIs, and logs. Ensure you have backups of any important data.

## 🎯 Test User

## Environment Variables

**Stefan** (`+16129782029`) has 4 stored memories and receives personalized greetings:

> "Hello Stefan! I know you prefer email updates. How can I assist you today?"All Lambdas use these environment variables (configured in template.yaml):



## 🔗 Live Endpoints| Variable | Description | Default |

|----------|-------------|---------|

- **ClientData**: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`| `MEM0_API_KEY` | Mem0 API key | Required |

- **PostCall**: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`  | `MEM0_ORG_ID` | Mem0 organization ID | Required |

- **Retrieve**: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`| `MEM0_PROJECT_ID` | Mem0 project ID | Required |

| `MEM0_DIR` | Directory for Mem0 cache | `/tmp/.mem0` |

## 🆘 Support| `MEM0_SEARCH_LIMIT` | Max results for semantic search | `3` |

| `MEM0_TIMEOUT` | Timeout in seconds | `5` |

For setup issues, check the troubleshooting section above or monitor CloudWatch logs:| `ELEVENLABS_WORKSPACE_KEY` | Workspace secret for auth | Required |

| `ELEVENLABS_HMAC_KEY` | HMAC signing key | Required |

```bash

aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow## 💰 Cost Optimization

```

### Monthly Cost Estimate

---

**For 10 concurrent calls, ~10K invocations/month:**

*Built with AWS SAM, ElevenLabs Agents Platform, and Mem0 Cloud*

*Last Updated: October 3, 2025*| Service | Usage | Cost |
|---------|-------|------|
| **Lambda Compute** | 10K invocations × 500ms avg | $5-8 |
| **Lambda Requests** | 10K requests | $0.20 |
| **HTTP API Gateway** | 10K requests | $1-2 |
| **CloudWatch Logs** | 100MB/month (7-day retention) | $0.50 |
| **Data Transfer** | Minimal (JSON responses) | $0.10 |
| **Total** | | **~$7-11/month** |

### Cost Optimization Tips

💡 **Reduce Cold Starts**: Use Provisioned Concurrency for predictable traffic  
💡 **Optimize Memory**: Monitor actual usage and adjust MemorySize accordingly  
💡 **Log Retention**: 7-day retention vs 30-day saves ~60% on CloudWatch costs  
💡 **Efficient Packaging**: Lambda layer reduces deployment package size  
💡 **Regional Deployment**: Deploy in same region as ElevenLabs for lower latency/costs  

### Usage-Based Scaling

| Monthly Calls | Lambda Cost | API Gateway | Total Est. |
|---------------|-------------|-------------|------------|
| 1K calls | $1-2 | $0.10 | **$1-3** |
| 10K calls | $5-8 | $1-2 | **$7-11** |
| 100K calls | $40-60 | $10-15 | **$50-75** |
| 1M calls | $350-500 | $100-150 | **$450-650** |

> **Note**: Costs may vary based on memory usage, execution time, and AWS region.

## 🐛 Troubleshooting Guide

### Common Issues & Solutions

#### 🔴 Lambda Timeout Errors

**Symptoms**: 502 Bad Gateway, timeout errors in logs  
**Solution**: Increase timeout in `template.yaml`:
```yaml
Properties:
  Timeout: 30  # Increase to 45 or 60 seconds
```

#### 🔴 Mem0 Connection Issues

**Symptoms**: "Connection refused", "API key invalid"  
**Diagnostics**:
```bash
# Verify environment variables
aws lambda get-function-configuration \
  --function-name AgenticMemoriesClientData \
  --query 'Environment.Variables'
```
**Solution**: Ensure API credentials are correct in CloudFormation parameters

#### 🔴 HMAC Validation Failing

**Symptoms**: "Invalid HMAC signature" in PostCall logs  
**Solution**: 
1. Verify `ELEVENLABS_HMAC_KEY` matches ElevenLabs webhook settings
2. Check timestamp drift (must be within 30 minutes)
3. Ensure ElevenLabs is sending proper signature format: `t=timestamp,v0=hash`

#### 🔴 404 Not Found Errors

**Symptoms**: API Gateway returns 404  
**Solution**: 
1. Verify API Gateway URLs from deployment outputs
2. Check if stack deployed successfully: `aws cloudformation describe-stacks`
3. Ensure HTTP method is POST, not GET

#### 🔴 Cold Start Latency

**Symptoms**: First requests take 3-5 seconds  
**Solutions**:
1. **Immediate**: Accept cold starts as normal
2. **Short-term**: Add warming strategy (scheduled invocations)
3. **Long-term**: Add Provisioned Concurrency (increases cost)

#### 🔴 High Memory Usage

**Symptoms**: Lambda out of memory errors  
**Solution**: Increase MemorySize in `template.yaml`:
```yaml
Properties:
  MemorySize: 512  # Up from 256MB
```

### Debug Mode

**Enable verbose logging** by setting environment variable:
```bash
aws lambda update-function-configuration \
  --function-name AgenticMemoriesClientData \
  --environment "Variables={LOG_LEVEL=DEBUG}"
```

### Health Check Commands

**Quick system validation:**
```bash
# Test all endpoints
python3 test_clientdata.py
python3 test_postcall.py

# Check Lambda status
aws lambda list-functions --query 'Functions[?contains(FunctionName, `AgenticMemories`)].{Name:FunctionName,State:State}'

# Verify API Gateway health
aws apigatewayv2 get-apis --query 'Items[?contains(Name, `AgenticMemories`)].{Name:Name,State:ApiEndpoint}'
```

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

## 🛡️ Security & Best Practices

### Authentication Summary

| Endpoint | Authentication Method | Header | Purpose |
|----------|----------------------|---------|---------|
| **ClientData** | Workspace Key | `X-Workspace-Key` | Prevents unauthorized memory access |
| **Retrieve** | None (trusted) | - | Direct agent tool calls (no auth needed) |
| **PostCall** | HMAC Signature | `ElevenLabs-Signature` | Validates webhook authenticity |

### Security Features

✅ **HTTPS Enforcement**: All API endpoints require HTTPS  
✅ **Signature Validation**: HMAC-SHA256 for webhook integrity  
✅ **Timestamp Checks**: 30-minute window prevents replay attacks  
✅ **IAM Least Privilege**: Lambda roles have minimal permissions  
✅ **Secret Management**: All sensitive values use CloudFormation NoEcho  
✅ **Input Validation**: Request payload validation and sanitization  

### Production Security Checklist

- [ ] **Rotate Keys Regularly**: Update HMAC and workspace keys quarterly
- [ ] **Monitor Failed Auths**: Set up CloudWatch alarms for 401/403 errors  
- [ ] **Enable AWS CloudTrail**: Log all API calls for audit trail
- [ ] **Use VPC Endpoints**: For enhanced network security (optional)
- [ ] **Implement Rate Limiting**: Add API Gateway throttling
- [ ] **Regular Security Reviews**: Audit IAM permissions and access patterns

### Environment Variables Security

All sensitive values are marked `NoEcho: true` in CloudFormation and never logged:

| Variable | Security Level | Notes |
|----------|---------------|-------|
| `MEM0_API_KEY` | 🔴 Sensitive | Never logged, encrypted at rest |
| `ELEVENLABS_WORKSPACE_KEY` | 🔴 Sensitive | Used for authentication |
| `ELEVENLABS_HMAC_KEY` | 🔴 Sensitive | Webhook signature validation |
| `MEM0_ORG_ID` | 🟡 Moderate | Organization identifier |
| `MEM0_PROJECT_ID` | 🟡 Moderate | Project identifier |

## 🚀 Roadmap & Future Enhancements

### Phase 2: Performance Optimization
- [ ] **Provisioned Concurrency**: Sub-100ms cold start elimination
- [ ] **Connection Pooling**: Reuse Mem0 connections across invocations  
- [ ] **Caching Layer**: Redis/ElastiCache for frequently accessed memories
- [ ] **Batch Processing**: Optimize multiple memory operations

### Phase 3: Advanced Features  
- [ ] **Memory Versioning**: Track memory changes over time
- [ ] **TTL Support**: Automatic memory expiration
- [ ] **Memory Categories**: Organize memories by type/importance
- [ ] **Conflict Resolution**: Handle duplicate/conflicting memories
- [ ] **Multi-tenant Support**: Separate memories by organization

### Phase 4: Monitoring & Ops
- [ ] **Dead Letter Queues**: Handle failed PostCall processing  
- [ ] **X-Ray Tracing**: Distributed request tracing
- [ ] **Custom Metrics**: Business-specific monitoring
- [ ] **A/B Testing**: Memory strategy optimization
- [ ] **Automated Alerts**: Proactive issue detection

### Phase 5: Integration Expansion
- [ ] **Multi-Provider Support**: Support for other voice AI platforms
- [ ] **Webhook Replay**: Retry failed memory operations
- [ ] **API Versioning**: Backward compatibility management
- [ ] **GraphQL Interface**: Advanced query capabilities
- [ ] **Real-time Updates**: WebSocket memory synchronization

## 📚 Additional Resources

### Documentation
- 📖 **[Complete System Specification](./SPECIFICATION.md)** - Detailed technical specification
- 🤖 **[GitHub Copilot Instructions](./.github/copilot-instructions.md)** - AI coding guidelines
- 🧪 **[Test Scripts](./test_*.py)** - Authentication and integration tests

### External Documentation  
- 🧠 **[Mem0 API Documentation](https://docs.mem0.ai/)** - Memory platform integration
- 🎙️ **[ElevenLabs Agent Docs](https://elevenlabs.io/docs/conversational-ai)** - Voice AI platform
- ⚡ **[AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)** - Serverless framework
- 🐍 **[AWS Lambda Python Runtime](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)** - Runtime documentation

### Community & Support
- 💬 **[ElevenLabs Discord](https://discord.gg/elevenlabs)** - Community support
- 🛠️ **[AWS SAM GitHub](https://github.com/aws/serverless-application-model)** - Framework issues
- 📊 **[Mem0 GitHub](https://github.com/mem0ai/mem0)** - Memory platform issues

### Related Projects
- 🔗 **[ElevenLabs Examples](https://github.com/elevenlabs/elevenlabs-examples)** - Official examples
- 🔗 **[AWS SAM Examples](https://github.com/aws/serverless-application-model/tree/develop/examples)** - Serverless patterns
- 🔗 **[Mem0 Examples](https://github.com/mem0ai/mem0/tree/main/examples)** - Memory integration examples

---

## 📄 License

**MIT License** - See [LICENSE](./LICENSE) file for details.

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📧 Support & Contact

For technical issues:
- 📋 **Check**: [SPECIFICATION.md](./SPECIFICATION.md) for detailed documentation  
- 🧪 **Run**: Test scripts to validate your setup
- 📊 **Monitor**: CloudWatch logs for error details
- 🐛 **Report**: Issues via GitHub Issues

---

**Built with ❤️ for the voice AI community**

*AgenticMemory bridges the gap between conversational AI and persistent memory, enabling truly personalized voice experiences.*