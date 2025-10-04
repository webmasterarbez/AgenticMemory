# ElevenLabs Agentic Memory# Eleven Labs Agentic Memory



> **Production-Ready Conversational Memory System**  

> AWS Serverless Backend for ElevenLabs Voice Agents with Mem0 Cloud Integration

**Conversational Memory for ElevenLabs Voice Agents**

[![AWS SAM](https://img.shields.io/badge/AWS%20SAM-Serverless-orange)](https://aws.amazon.com/serverless/sam/)

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)

[![Mem0](https://img.shields.io/badge/Mem0-Cloud-green)](https://mem0.ai/)

[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-Voice%20AI-purple)](https://elevenlabs.io/)Eleven Labs Agentic Memory is an AWS serverless backend that provides persistent memory capabilities for ElevenLabs voice agents using Mem0 Cloud. It enables agents to remember previous conversations and provide personalized interactions.



**Last Updated**: October 3, 2025



---## Table of ContentsEleven Labs Agentic Memory is an AWS serverless backend that provides persistent memory capabilities for ElevenLabs voice agents using Mem0 Cloud. It enables agents to remember previous conversations and provide personalized interactions.> **Conversational Memory for ElevenLabs Voice Agents****Production-Ready AWS Serverless Backend** for ElevenLabs Voice Agents with Mem0 Cloud integration for conversational memory management.



## 📖 Table of Contents



1. [Overview](#overview)1. [🚀 Quick Start](#-quick-start)

2. [🚀 Quick Start](#-quick-start)

3. [🏗️ Architecture](#️-architecture)2. [🏗️ Architecture](#️-architecture)  

4. [🔐 Authentication](#-authentication)

5. [📋 System Components](#-system-components)3. [🔐 Authentication (CRITICAL)](#-authentication-critical)## Table of Contents

6. [🧠 Memory System](#-memory-system)

7. [🎤 ElevenLabs Integration](#-elevenlabs-integration)4. [📋 System Components](#-system-components)

8. [☁️ S3 Storage](#️-s3-storage)

9. [🎵 Audio Webhook Handling](#-audio-webhook-handling)5. [🧠 Memory System](#-memory-system)

10. [🛠️ Development](#️-development)

11. [🧪 Testing](#-testing)6. [🎤 ElevenLabs Integration](#-elevenlabs-integration)

12. [🔍 Troubleshooting](#-troubleshooting)

13. [📂 Project Structure](#-project-structure)7. [☁️ AWS Infrastructure](#️-aws-infrastructure)1. [🚀 Quick Start](#-quick-start)Eleven Labs Agentic Memory is an AWS serverless backend that provides persistent memory capabilities for ElevenLabs voice agents using Mem0 Cloud. It enables agents to remember previous conversations and provide personalized interactions.[![AWS SAM](https://img.shields.io/badge/AWS%20SAM-Serverless-orange)](https://aws.amazon.com/serverless/sam/)



---8. [🛠️ Development Workflow](#️-development-workflow)



## Overview9. [🧪 Testing](#-testing)2. [🏗️ Architecture](#️-architecture)  



**ElevenLabs Agentic Memory** is a production-ready AWS serverless backend that provides persistent memory capabilities for ElevenLabs voice agents using Mem0 Cloud. It enables agents to:10. [🔍 Troubleshooting](#-troubleshooting)



- 🎯 **Remember** previous conversations across multiple calls11. [📂 Project Structure](#-project-structure)3. [🔐 Authentication (CRITICAL)](#-authentication-critical)[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)

- 🤝 **Personalize** greetings based on caller history  

- 🔍 **Search** past conversations during active calls12. [🤖 System Prompt Template](#-system-prompt-template)

- 📊 **Store** both factual summaries and full conversation transcripts

- 🎵 **Archive** complete call recordings with metadata4. [📋 System Components](#-system-components)



### Key Features---



- ⚡ **Sub-500ms latency** with separate HTTP APIs per function5. [🧠 Memory System](#-memory-system)## 🚀 Quick Start[![Mem0](https://img.shields.io/badge/Mem0-Cloud-green)](https://mem0.ai/)

- 🔐 **Production security** with HMAC signatures and workspace key authentication

- 🧠 **Smart memory separation** between factual data and conversation context## 🚀 Quick Start

- 📊 **Comprehensive S3 archival** for all webhook payloads and responses

- 🔄 **Dual webhook support** for separate transcription and audio delivery6. [🎤 ElevenLabs Integration](#-elevenlabs-integration)

- 🎤 **Real-time monitoring** with CloudWatch integration

- 🚀 **Async processing** to prevent webhook timeouts### 1. Deploy the Backend



### System Architecture```bash7. [☁️ AWS Infrastructure](#️-aws-infrastructure)[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-Voice%20AI-purple)](https://elevenlabs.io/)



```# Build dependencies

┌─────────────────┐

│  ElevenLabs     │cd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..8. [🛠️ Development Workflow](#️-development-workflow)

│  Voice Agent    │

└────────┬────────┘

         │

         ├──── Pre-Call ───────► ClientData Lambda ────► Mem0 Cloud# Deploy to AWS9. [🧪 Testing](#-testing)### 1. Deploy the Backend

         │                       (Memory Retrieval)      (Get History)

         │sam build && sam deploy --guided

         ├──── Mid-Call ───────► Retrieve Lambda ──────► Mem0 Cloud

         │                       (Semantic Search)       (Search Memories)```10. [🔍 Troubleshooting](#-troubleshooting)

         │

         └──── Post-Call ──────► PostCall Lambda ──────► Mem0 Cloud

                                 (Memory Storage)        (Store New Data)

                                       │### 2. Configure ElevenLabs11. [📂 Project Structure](#-project-structure)```bash## Overview

                                       └─────────────────► S3 Storage

                                                          (Archive)- **Conversation Initiation Webhook**: Set URL and authentication via secrets manager

```

- **Search Memory Tool**: Configure for in-call memory retrieval  12. [🤖 System Prompt Template](#-system-prompt-template)

---

- **Post-Call Webhook**: Enable for memory storage with HMAC authentication

## 🚀 Quick Start

# Build dependencies

### Prerequisites

### 3. Test the System

- AWS Account with CLI configured

- AWS SAM CLI installed```bash---

- Python 3.12+

- ElevenLabs accountpython3 scripts/test_production_ready.py

- Mem0 Cloud account

```cd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..This system bridges **ElevenLabs voice agents** with **Mem0 Cloud** for persistent conversational memory across calls. Three optimized Lambda functions handle the complete memory lifecycle:

### 1. Deploy the Backend



```bash

# Clone the repository---## 🚀 Quick Start

git clone <repository-url>

cd AgenticMemory



# Build Lambda layer dependencies## 🏗️ Architecture

cd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..



# Build and deploy to AWS

sam build```### 1. Deploy the Backend

sam deploy --guided

```ElevenLabs Agent ←→ AWS Lambda Functions ←→ Mem0 Cloud



**During deployment**, provide:                         ↓```bash# Deploy to AWS1. **ClientData** (Pre-call): Returns personalized memory context when conversation starts

- Stack name (e.g., `agentic-memory-stack`)

- AWS Region                   S3 Storage (backup)

- Mem0 API credentials (API key, Org ID, Project ID)

- ElevenLabs credentials (Workspace Key, HMAC Secret)```# Build dependencies



**Save the API endpoints** from the deployment output:

- `ClientDataApiUrl`

- `RetrieveApiUrl`**3 Lambda Functions**:cd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..sam build && sam deploy --guided2. **Retrieve** (Mid-call): Semantic search for agent tools during active conversations  

- `PostCallApiUrl`

- **ClientData**: Pre-call memory retrieval + personalized greeting

### 2. Configure ElevenLabs

- **PostCall**: Async memory storage after calls

#### A. Conversation Initiation Webhook

- **Retrieve**: In-call semantic search tool

1. Go to [ElevenLabs Dashboard](https://elevenlabs.io/app/agents/settings) → Agent → Security

2. Enable "Fetch conversation initiation data for inbound calls"# Deploy to AWS```3. **PostCall** (Async): Stores factual and semantic memories after call completion

3. **Add Secret** in Secrets Manager:

   - Name: `WORKSPACE_KEY`---

   - Value: `wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70`

4. **Configure Webhook**:sam build && sam deploy --guided

   - URL: `<ClientDataApiUrl>` (from deployment output)

   - Method: `POST`## 🔐 Authentication (CRITICAL)

   - Header: `X-Workspace-Key` → `WORKSPACE_KEY` (secret reference)

```

#### B. Search Memory Tool

### ⚠️ DO NOT CHANGE THESE AUTHENTICATION METHODS

1. Go to Agent → Tools → Add Tool

2. Configure:

   - Name: `search_memory`

   - Description: "Search previous conversations for specific information"#### ClientData Authentication

   - Type: Webhook

   - URL: `<RetrieveApiUrl>`**Method**: ElevenLabs Secrets Manager (NOT direct headers)### 2. Configure ElevenLabs### 2. Configure ElevenLabs**✨ Key Features:**

   - Method: `POST`

   - Parameters:

     - `query` (string): "What to search for"

     - `user_id` (string, default: `{{system__caller_id}}`): "User identifier"**Configuration**:- **Conversation Initiation Webhook**: Set URL and authentication via secrets manager



#### C. Post-Call Webhooks1. Go to [ElevenLabs Settings](https://elevenlabs.io/app/agents/settings)



1. Go to Agent → Webhooks → Add Webhook2. Add secret: `WORKSPACE_KEY` = `wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70`- **Search Memory Tool**: Configure for in-call memory retrieval  - **Conversation Initiation Webhook**: Set URL and authentication via secrets manager- 🚀 **Sub-500ms latency** with separate HTTP APIs per function

2. **Transcription Webhook**:

   - Type: Conversation End3. Map to header: `X-Workspace-Key` → `WORKSPACE_KEY` secret

   - URL: `<PostCallApiUrl>`

   - Method: `POST`4. Enable in agent Security tab: "Fetch conversation initiation data"- **Post-Call Webhook**: Enable for memory storage with HMAC authentication

   - Authentication: HMAC (use your HMAC secret)

   - Enable "Send transcript data"

3. **Audio Webhook** (enable separately):

   - Enable "Send audio data" toggle**Why**: ElevenLabs requires authentication headers to be managed through their secure secrets interface, not as direct header configuration.- **Search Memory Tool**: Configure for in-call memory retrieval  - 🔐 **Production security** with HMAC signatures and workspace key auth

   - Uses same endpoint and HMAC secret



### 3. Test the System

#### PostCall Authentication### 3. Test the System

```bash

# Install test dependencies**Method**: HMAC-SHA256 Signature

pip install -r requirements.txt

```bash- **Post-Call Webhook**: Enable for memory storage with HMAC authentication- 🧠 **Smart memory separation** between factual data and conversation context

# Run comprehensive tests

python3 test_production_ready.py**Reference**: https://elevenlabs.io/docs/agents-platform/workflows/post-call-webhooks#authentication



# Or test individual componentspython3 scripts/test_production_ready.py

python3 test_client_data_s3.py          # ClientData webhook + S3

python3 test_audio_webhook.py           # Dual webhook system**Configuration**:

python3 test_postcall_s3_path.py        # PostCall S3 paths

```- HMAC Key: `wsec_a8dc8b6e25ec3ddf11d7e651c40a5cb4931c2ca39d161fa4c94139f12f3ba9d3````- 📊 **Real-time monitoring** with CloudWatch integration



---- Header: `ElevenLabs-Signature` (format: `t=timestamp,v0=signature`)



## 🏗️ Architecture- Tolerance: 30 minutes



### Lambda Functions- Always return 200 OK (async processing)



Three specialized Lambda functions handle the complete memory lifecycle:---### 3. Test the System- 🔄 **Async processing** to prevent webhook timeouts



#### 1. **ClientData** (Pre-Call Memory Retrieval)**Why**: ElevenLabs uses HMAC signatures to verify webhook authenticity and prevent replay attacks.



**Purpose**: Retrieve caller's memory and generate personalized greeting before call starts



**Trigger**: ElevenLabs Conversation Initiation webhook  #### Retrieve Authentication  

**Authentication**: Workspace Key via ElevenLabs Secrets Manager  

**Response Time**: < 500ms**Method**: None (trusted connection)## 🏗️ Architecture```bash- ⚡ **Optimized performance** with Lambda layer reuse



**Flow**:

1. Receive webhook with `caller_id`, `agent_id`, `called_number`, `call_sid`

2. Query Mem0 for all memories associated with `caller_id`**Configuration**: No authentication required

3. Extract caller name from memories (if available)

4. Generate personalized greeting

5. Format memory context for agent prompt

6. Save request/response payloads to S3**Why**: Direct communication between ElevenLabs agent and backend during active calls is considered trusted.```python3 scripts/test_production_ready.py

7. Return conversation config override to ElevenLabs



**Key Functions**:

- `extract_caller_name()`: Regex-based name extraction from memories### Quick Authentication TestElevenLabs Agent ←→ AWS Lambda Functions ←→ Mem0 Cloud

- `generate_personalized_greeting()`: Creates customized greetings

- `save_client_data_to_s3()`: Archives webhook data```bash



#### 2. **Retrieve** (Mid-Call Semantic Search)# ClientData (should return 200 with memory data)                         ↓```## 📁 Project Structure



**Purpose**: Semantic search of memories during active conversationscurl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \



**Trigger**: Agent tool invocation during call    -H 'X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70' \                   S3 Storage (backup)

**Authentication**: None (trusted agent connection)  

**Response Time**: < 300ms  -H 'Content-Type: application/json' \



**Flow**:  -d '{"caller_id": "+16129782029"}' -v```

1. Receive search request with `query` and `user_id`

2. Perform semantic search in Mem0

3. Return top N relevant memories

4. Agent uses results to inform conversation# Test wrong key (should return 401)



**Use Cases**:curl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \

- "What did the caller say about email preferences?"

- "When was their last purchase?"  -H 'X-Workspace-Key: wrong_key' \**3 Lambda Functions**:## 📋 Complete Documentation```

- "What issues did they report?"

  -H 'Content-Type: application/json' \

#### 3. **PostCall** (Async Memory Storage)

  -d '{"caller_id": "+16129782029"}' -s -w "Status: %{http_code}\n"- **ClientData**: Pre-call memory retrieval + personalized greeting

**Purpose**: Store conversation memories and archive call data after completion

```

**Trigger**: ElevenLabs Post-Call webhooks (transcription + audio)  

**Authentication**: HMAC-SHA256 signature  - **PostCall**: Async memory storage after callsAgenticMemory/

**Processing**: Async (returns 200 OK immediately)

---

**Flow**:

1. Verify HMAC signature- **Retrieve**: In-call semantic search tool

2. Detect webhook type (`post_call_transcription` or `post_call_audio`)

3. **For transcription webhook**:## 📋 System Components

   - Extract conversation data

   - Store factual memory (summary + evaluation)**📖 [MASTER_DOCUMENTATION.md](MASTER_DOCUMENTATION.md)** - Complete project guide covering:├── src/                    # Lambda function source code

   - Store semantic memory (full transcript)

   - Save JSON to S3### 1. ClientData Function (`src/client_data/handler.py`)

4. **For audio webhook**:

   - Decode base64 audio**Purpose**: Pre-call memory retrieval + personalized greeting generation---

   - Save MP3 to S3

5. Return success (errors logged but don't affect response)



---**Endpoint**: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`- Architecture overview and components│   ├── client_data/        # Pre-call memory retrieval



## 🔐 Authentication



### ⚠️ CRITICAL: Do Not Change These Methods**Request Format**:## 🔐 Authentication (CRITICAL)



#### ClientData Authentication```json



**Method**: ElevenLabs Secrets Manager (NOT direct headers){- ElevenLabs integration setup│   ├── retrieve/           # Mid-call semantic search



**Configuration**:  "caller_id": "+16129782029",

1. Add secret in ElevenLabs: `WORKSPACE_KEY` = `wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70`

2. Map to header: `X-Workspace-Key` → `WORKSPACE_KEY` secret  "agent_id": "agent_xxx"### ⚠️ DO NOT CHANGE THESE AUTHENTICATION METHODS

3. Enable in agent Security tab

}

**Why**: ElevenLabs requires authentication headers to be managed through their secure secrets interface for PCI compliance.

```- Authentication methods (ClientData secrets + PostCall HMAC)│   └── post_call/          # Async memory storage

#### PostCall Authentication



**Method**: HMAC-SHA256 Signature

**Response Format**:#### ClientData Authentication

**Details**:

- **HMAC Key**: `wsec_a8dc8b6e25ec3ddf11d7e651c40a5cb4931c2ca39d161fa4c94139f12f3ba9d3````json

- **Header**: `ElevenLabs-Signature`

- **Format**: `t=<timestamp>,v0=<signature>`{**Method**: ElevenLabs Secrets Manager (NOT direct headers)- Memory system operation├── layer/                  # Shared Lambda layer (mem0ai)

- **Signed Payload**: `{timestamp}.{raw_body}`

- **Tolerance**: 30 minutes  "type": "conversation_initiation_client_data",

- **Reference**: [ElevenLabs Webhook Authentication](https://elevenlabs.io/docs/agents-platform/workflows/post-call-webhooks#authentication)

  "dynamic_variables": {

**Why**: Prevents replay attacks and verifies webhook authenticity.

    "caller_id": "+16129782029",

#### Retrieve Authentication

    "memory_count": "4",**Configuration**:- Troubleshooting and monitoring├── docs/                   # 📚 All documentation

**Method**: None (trusted connection)

    "memory_summary": "User wants to update email address",

**Why**: Direct agent-to-backend communication during active calls is considered trusted.

    "returning_caller": "yes",1. Go to [ElevenLabs Settings](https://elevenlabs.io/app/agents/settings)

### Quick Authentication Test

    "caller_name": "Stefan"

```bash

# Test ClientData (should return 200 with memory data)  },2. Add secret: `WORKSPACE_KEY` = `wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70`- Development workflow│   ├── README.md           # Documentation index

curl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \

  -H 'X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70' \  "conversation_config_override": {

  -H 'Content-Type: application/json' \

  -d '{"caller_id": "+16129782029", "agent_id": "agent_xyz", "called_number": "+17205752470", "call_sid": "CAtest"}'    "agent": {3. Map to header: `X-Workspace-Key` → `WORKSPACE_KEY` secret



# Test PostCall (basic connectivity - HMAC signature required for real webhooks)      "prompt": {"prompt": "CALLER CONTEXT: This caller has 4 previous interactions..."},

curl -X POST https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call \

  -H 'Content-Type: application/json' \      "first_message": "Hello Stefan! I know you prefer email updates. How can I assist you today?"4. Enable in agent Security tab: "Fetch conversation initiation data"│   ├── SPECIFICATION.md    # Technical spec

  -d '{"test": "connectivity"}'

    }

# Test Retrieve (no auth needed)

curl -X POST https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve \  }

  -H 'Content-Type: application/json' \

  -d '{"query": "email preferences", "user_id": "+16129782029"}'}

```

```**Why**: ElevenLabs requires authentication headers to be managed through their secure secrets interface, not as direct header configuration.**🔐 [AUTHENTICATION_REFERENCE.md](AUTHENTICATION_REFERENCE.md)** - Critical authentication setup│   ├── SYSTEM_FLOW.md      # Architecture diagrams

---



## 📋 System Components

### 2. PostCall Function (`src/post_call/handler.py`)

### AWS Resources

**Purpose**: Async memory storage after call completion

| Resource | Purpose | Configuration |

|----------|---------|---------------|#### PostCall Authentication**🤖 [CORRECTED_MEMOIR_SYSTEM_PROMPT.md](CORRECTED_MEMOIR_SYSTEM_PROMPT.md)** - ElevenLabs system prompt│   ├── ELEVENLABS_SETUP_GUIDE.md

| **Lambda Functions** | Core processing logic | Python 3.12, 128-512MB RAM, 30-60s timeout |

| **API Gateway (HTTP)** | Webhook endpoints | One per function, CORS enabled |**Endpoint**: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`

| **Lambda Layer** | Shared dependencies | Contains `mem0ai` package only |

| **S3 Bucket** | Data archival | 7-day lifecycle policy on logs |**Method**: HMAC-SHA256 Signature

| **CloudWatch Logs** | Monitoring & debugging | 7-day retention |

| **IAM Roles** | Permissions | Scoped to minimum required |**Processing**: Stores both factual summaries and semantic transcripts to Mem0



### Mem0 Cloud Integration**📂 [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - File structure and quick commands│   ├── QUICK_REFERENCE.md



**API Endpoints Used**:### 3. Retrieve Function (`src/retrieve/handler.py`)  

- `client.get_all(user_id)` - Retrieve all memories (ClientData)

- `client.search(query, user_id, limit)` - Semantic search (Retrieve)**Purpose**: In-call semantic search for memory retrieval**Reference**: https://elevenlabs.io/docs/agents-platform/workflows/post-call-webhooks#authentication

- `client.add(messages, user_id, metadata)` - Store memories (PostCall)



**Memory Metadata**:

```python**Endpoint**: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`│   └── ... (see docs/README.md)

{

    'type': 'factual' | 'semantic',

    'agent_id': 'agent_xyz',

    'conversation_id': 'conv_abc123',**Tool Configuration** (ElevenLabs):**Configuration**:

    'timestamp': '2025-10-03T12:34:56',

    'call_duration_seconds': 180```json

}

```{- HMAC Key: `wsec_a8dc8b6e25ec3ddf11d7e651c40a5cb4931c2ca39d161fa4c94139f12f3ba9d3`## 🏗️ Architecture├── scripts/                # 🧪 Test & utility scripts



---  "name": "search_memory",



## 🧠 Memory System  "description": "Search previous conversations and memories",- Header: `ElevenLabs-Signature` (format: `t=timestamp,v0=signature`)



### Two Memory Types  "parameters": {



#### 1. Factual Memory    "query": {"type": "string", "description": "What to search for"},- Tolerance: 30 minutes│   ├── README.md           # Scripts index



**Purpose**: High-level summaries and key facts      "user_id": {"type": "string", "default": "{{system__caller_id}}"}

**Source**: ElevenLabs analysis and evaluation  

**Storage**: Mem0 Cloud with `metadata.type = "factual"`  }- Always return 200 OK (async processing)



**Content**:}

- Call summary

- Key topics discussed``````│   ├── test_postcall_with_file.py  # ⭐ Main test tool

- Caller preferences

- Action items

- Evaluation rationale

---**Why**: ElevenLabs uses HMAC signatures to verify webhook authenticity and prevent replay attacks.

**Example**:

```json

{

  "user_id": "+16129782029",## 🧠 Memory SystemElevenLabs Agent ←→ AWS Lambda Functions ←→ Mem0 Cloud│   ├── test_postcall.sh    # Bash wrapper

  "content": "Stefan wants to upgrade to premium account. Prefers email communication.",

  "metadata": {

    "type": "factual",

    "agent_id": "agent_xyz",### Memory Types#### Retrieve Authentication  

    "conversation_id": "conv_001"

  }1. **Factual Memories** (`metadata.type = "factual"`)

}

```   - Call summaries and key facts**Method**: None (trusted connection)                         ↓│   └── ... (25+ test scripts)



#### 2. Semantic Memory   - User preferences and account details



**Purpose**: Full conversation transcripts for deep context     - Used for dynamic variables and context

**Source**: Complete conversation messages array  

**Storage**: Mem0 Cloud with `metadata.type = "semantic"`



**Content**:2. **Semantic Memories** (`metadata.type = "semantic"`)**Configuration**: No authentication required                   S3 Storage (backup)├── test_data/              # 📋 JSON test payloads

- Full conversation transcript

- Speaker labels (agent/user)   - Full conversation transcripts

- Timestamps per message

- Raw conversation flow   - Used for semantic search during calls



**Example**:   - Enables detailed recall of past conversations

```json

{**Why**: Direct communication between ElevenLabs agent and backend during active calls is considered trusted.```│   ├── README.md           # Test data index

  "user_id": "+16129782029",

  "messages": [### Memory Storage Process

    {"role": "agent", "content": "Hello! How can I help?"},

    {"role": "user", "content": "I want to upgrade my account"},1. **Call Ends** → ElevenLabs sends webhook to PostCall

    {"role": "agent", "content": "Great! Let me help you with that..."}

  ],2. **Extract Content** → Parse transcript and analysis

  "metadata": {

    "type": "semantic",3. **Generate Summary** → Create factual memory from key points### Quick Authentication Test│   ├── conv_*.json         # Real conversation files

    "agent_id": "agent_xyz",

    "conversation_id": "conv_001"4. **Store Both Types** → Save factual + semantic to Mem0

  }

}5. **S3 Backup** → Store raw payload for audit trail```bash

```



### Memory Lifecycle

### Memory Retrieval Process# ClientData (should return 200 with memory data)**3 Lambda Functions**:│   └── *_payload.json      # Sample payloads

```

1. Call Starts1. **Call Starts** → ElevenLabs calls ClientData webhook

   ↓

2. ClientData retrieves ALL memories (factual + semantic)2. **Get All Memories** → Retrieve factual + semantic for callercurl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \

   ↓

3. Agent personalizes greeting and conversation3. **Extract Name** → Use regex patterns to find caller name

   ↓

4. During call: Agent uses Retrieve for specific searches4. **Generate Context** → Build personalized prompt override  -H 'X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70' \- **ClientData**: Pre-call memory retrieval + personalized greeting├── tests/                  # Unit tests

   ↓

5. Call Ends5. **Create Variables** → Populate dynamic variables for agent

   ↓

6. PostCall stores:  -H 'Content-Type: application/json' \

   - Factual memory (summary + evaluation)

   - Semantic memory (full transcript)### Mem0 Cloud Configuration

   ↓

7. Available for next call- **API Key**: `m0-gS2X0TszRwwEC6mXE3DrEDtpxQJdcCWAariVvafD`  -d '{"caller_id": "+16129782029"}' -v- **PostCall**: Async memory storage after calls├── template.yaml           # SAM deployment template

```

- **Organization ID**: `org_knmmDKevT5Yz7bDF4Dd9BcFDWjp2RHzstpvtN3GW`

### User ID Format

- **Project ID**: `proj_3VBb1VIAmQofeGcY0XCHDbb7EqBLeEfETd6iNFqZ`

**Format**: E.164 phone numbers with `+` prefix  

**Example**: `+16129782029`- **User ID Format**: Phone numbers in E.164 format (`+16129782029`)



**Why**: Phone numbers serve as natural, unique identifiers for callers.# Test wrong key (should return 401)- **Retrieve**: In-call semantic search tool├── samconfig.toml          # SAM configuration (gitignored)



------



## 🎤 ElevenLabs Integrationcurl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \



### Webhook Payloads## 🎤 ElevenLabs Integration



#### Conversation Initiation (ClientData)  -H 'X-Workspace-Key: wrong_key' \└── requirements.txt        # Dev dependencies



**Request from ElevenLabs**:### Agent Configuration Requirements

```json

{  -H 'Content-Type: application/json' \

  "caller_id": "+16129782029",

  "agent_id": "agent_4301k6n146bgfs2tqtq5nhejw0r7",#### 1. Conversation Initiation Webhook

  "called_number": "+17205752470",

  "call_sid": "CA1234567890abcdef"- **URL**: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`  -d '{"caller_id": "+16129782029"}' -s -w "Status: %{http_code}\n"## ✅ Current Status```

}

```- **Method**: POST



**Response to ElevenLabs**:- **Authentication**: Secrets Manager (NOT direct headers)```

```json

{- **Secret Name**: `WORKSPACE_KEY`

  "type": "conversation_initiation_client_data",

  "dynamic_variables": {- **Secret Value**: `wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70`

    "caller_id": "+16129782029",

    "caller_name": "Stefan",- **Header Mapping**: `X-Workspace-Key` → `WORKSPACE_KEY` secret

    "memory_count": "4",

    "returning_caller": "yes",---

    "memory_summary": "User wants to update email address"

  },#### 2. Agent Security Settings

  "conversation_config_override": {

    "agent": {Enable in agent's Security tab:- ✅ **Backend Deployed**: All 3 Lambda functions operational**Quick Navigation:**

      "prompt": {

        "prompt": "CALLER CONTEXT:\nThis caller has 4 previous interactions...\n\nKnown information:\n- Stefan wants to upgrade to premium account\n- User Name is Stefan\n- Prefers email communication\n\nInstructions: Use this context naturally in conversation."- ✅ "Fetch conversation initiation data for inbound Twilio calls"

      },

      "first_message": "Hello Stefan! I know you prefer email updates. How can I assist you today?"- ✅ Allow prompt overrides## 📋 System Components

    }

  }- ✅ Allow first message overrides

}

```- ✅ **Mem0 Integration**: Storing factual + semantic memories- 📖 **Documentation**: See [docs/README.md](docs/README.md)



#### Post-Call Transcription Webhook#### 3. Search Memory Tool



**Request from ElevenLabs**:- **URL**: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`### 1. ClientData Function (`src/client_data/handler.py`)

```json

{- **Method**: POST

  "type": "post_call_transcription",

  "event_timestamp": 1739537297,- **Authentication**: None**Purpose**: Pre-call memory retrieval + personalized greeting generation- ✅ **Authentication**: ElevenLabs secrets + HMAC configured- 🧪 **Testing**: See [scripts/README.md](scripts/README.md)  

  "data": {

    "agent_id": "agent_xyz",- **Parameters**: `query` (string), `user_id` (default: `{{system__caller_id}}`)

    "conversation_id": "conv_abc123",

    "external_number": "+16129782029",

    "transcript": [

      {"role": "agent", "message": "Hello! How can I help?", "timestamp": 1739537100},#### 4. Post-Call Webhook

      {"role": "user", "message": "I want to upgrade", "timestamp": 1739537105}

    ],- **URL**: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`**Endpoint**: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`- ✅ **Testing**: Production-ready endpoints verified- 📊 **Test Data**: See [test_data/README.md](test_data/README.md)

    "analysis": {

      "call_successful": true,- **Method**: POST

      "transcript_summary": "Customer requested account upgrade...",

      "custom_analysis_data": {}- **Authentication**: HMAC signature (auto-configured by ElevenLabs)

    },

    "metadata": {- **HMAC Secret**: `wsec_a8dc8b6e25ec3ddf11d7e651c40a5cb4931c2ca39d161fa4c94139f12f3ba9d3`

      "call_duration_seconds": 180,

      "call_successful": true**Request Format**:- ✅ **Monitoring**: CloudWatch logs and error tracking

    }

  }### Dynamic Variables

}

```The system provides these variables for ElevenLabs agents:```json



**Response** (immediate):- `{{caller_id}}` - Phone number (+16129782029)

```json

{- `{{returning_caller}}` - "yes" or "no"  {## Architecture

  "status": "ok"

}- `{{caller_name}}` - Extracted name (e.g., "Stefan")

```

- `{{memory_count}}` - Number of previous interactions  "caller_id": "+16129782029",

#### Post-Call Audio Webhook

- `{{memory_summary}}` - Most recent/important memory

**Request from ElevenLabs**:

```json  "agent_id": "agent_xxx"## 🎯 Test User

{

  "type": "post_call_audio",---

  "event_timestamp": 1739537319,

  "data": {}

    "agent_id": "agent_xyz",

    "conversation_id": "conv_abc123",## ☁️ AWS Infrastructure

    "full_audio": "SUQzBAAAAAAA...base64_encoded_mp3...AAAA=="

  }``````mermaid

}

```### CloudFormation Stack



**Note**: Audio webhook contains ONLY audio data - no transcript or caller_id!**Name**: `elevenlabs-agentic-memory-stack`



---**Region**: `us-east-1`



## ☁️ S3 Storage**Response Format**:**Stefan** (`+16129782029`) has 4 stored memories and receives personalized greetings:graph TB



### Complete Storage Structure### Lambda Functions



```- `elevenlabs-agentic-memory-lambda-function-client-data````json

s3://elevenlabs-agentic-memory-{account-id}-{region}/

├── client-data/- `elevenlabs-agentic-memory-lambda-function-post-call`

│   └── {caller_id}/

│       └── {timestamp}_{call_sid}/- `elevenlabs-agentic-memory-lambda-function-search-data`{> "Hello Stefan! I know you prefer email updates. How can I assist you today?"    A[ElevenLabs Agent] --> B[ClientData API]

│           ├── received.json         # Incoming webhook payload

│           └── response.json         # Response sent to ElevenLabs

│

└── post-call/### API Gateway Endpoints  "type": "conversation_initiation_client_data",

    ├── {caller_id}/

    │   └── {conversation_id}.json    # Full transcription dataEach function has its own API Gateway for optimal performance:

    │

    └── audio-only/- ClientData: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`  "dynamic_variables": {    A --> C[Retrieve API] 

        └── {agent_id}/

            └── {conversation_id}.mp3  # Call recording- PostCall: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`

```

- Retrieve: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`    "caller_id": "+16129782029",

### Storage Details



#### ClientData Storage

### S3 Storage    "memory_count": "4",## 🔗 Live Endpoints    A --> D[PostCall API]

**Path**: `client-data/{caller_id}/{timestamp}_{call_sid}/`

**Bucket**: `elevenlabs-agentic-memory-424875385161-us-east-1`

**Files**:

- `received.json`: Raw webhook payload from ElevenLabs**Purpose**: Backup storage for call data and audit trails    "memory_summary": "User wants to update email address",

- `response.json`: Complete response sent back



**Metadata**:

```python### CloudWatch Logs    "returning_caller": "yes",    

{

    'caller_id': '+16129782029',**Retention**: 7 days

    'agent_id': 'agent_xyz',

    'call_sid': 'CA123',**Log Groups**:    "caller_name": "Stefan"

    'timestamp': '2025-10-03T12:34:56',

    'payload_type': 'received' | 'response'- `/aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data`

}

```- `/aws/lambda/elevenlabs-agentic-memory-lambda-function-post-call`  },- **ClientData**: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`    B --> E[ClientData Lambda]



**Use Cases**:- `/aws/lambda/elevenlabs-agentic-memory-lambda-function-search-data`

- Audit trail of all webhook requests

- Debugging conversation initiation issues  "conversation_config_override": {

- Analytics on caller patterns

- Compliance and record-keeping---



#### PostCall Transcription Storage    "agent": {- **PostCall**: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`      C --> F[Retrieve Lambda]



**Path**: `post-call/{caller_id}/{conversation_id}.json`## 🛠️ Development Workflow



**Content**:      "prompt": {"prompt": "CALLER CONTEXT: This caller has 4 previous interactions..."},

- Complete conversation transcript

- Analysis results### Build & Deploy

- Evaluation data

- Call metadata```bash      "first_message": "Hello Stefan! I know you prefer email updates. How can I assist you today?"- **Retrieve**: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`    D --> G[PostCall Lambda]



**Example Path**: `post-call/+16129782029/conv_001.json`# 1. Build Lambda layer (required first)



#### PostCall Audio Storagecd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..    }



**Path**: `post-call/audio-only/{agent_id}/{conversation_id}.mp3`



**Content**: Base64-decoded MP3 audio file# 2. Build SAM application  }    



**Why separate directory?**  sam build

Audio webhooks don't include `caller_id`, only `agent_id` and `conversation_id`. We save under `agent_id` to avoid database lookups.

}

**Correlation**: Both files share the same `conversation_id` for linking.

# 3. Deploy

### S3 Usage Examples

sam deploy --guided  # First time```## 📞 Support    E --> H[Mem0 Cloud]

```bash

# List all ClientData requests for a callersam deploy           # Subsequent deploys

aws s3 ls s3://elevenlabs-agentic-memory-424875385161-us-east-1/client-data/16129782029/ --recursive

```

# Download transcription data

aws s3 cp s3://elevenlabs-agentic-memory-424875385161-us-east-1/post-call/+16129782029/conv_001.json ./



# Download audio file### Monitoring### 2. PostCall Function (`src/post_call/handler.py`)    F --> H

aws s3 cp s3://elevenlabs-agentic-memory-424875385161-us-east-1/post-call/audio-only/agent_xyz/conv_001.mp3 ./conversation.mp3

```bash

# Find both files for a conversation

CONV_ID="conv_001"# Tail logs**Purpose**: Async memory storage after call completion

aws s3 ls s3://elevenlabs-agentic-memory-424875385161-us-east-1/post-call/ --recursive | grep "$CONV_ID"

```aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow



---For setup issues, see the troubleshooting section in `MASTER_DOCUMENTATION.md` or check CloudWatch logs:    G --> H



## 🎵 Audio Webhook Handling# Check for errors



### Why Two Separate Webhooks?aws logs filter-log-events --log-group-name "/aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data" --filter-pattern "ERROR"**Endpoint**: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`



ElevenLabs sends **TWO separate webhooks** for each completed call:```



1. **`post_call_transcription`** - Full conversation data (NO audio)    

2. **`post_call_audio`** - Only base64-encoded MP3 audio

---

**Reason**: Efficient data delivery. Large audio files use chunked transfer encoding, while transcript data remains lightweight.

**Processing**: Stores both factual summaries and semantic transcripts to Mem0

### Original Issue

## 🧪 Testing

Audio files were NOT being saved because:

- Old code expected `full_audio` in transcription webhook```bash    I[Lambda Layer<br/>mem0ai] --> E

- **ElevenLabs no longer includes audio in transcription webhooks**

- Audio now comes via separate webhook### Test Scripts



### Implementation```bash### 3. Retrieve Function (`src/retrieve/handler.py`)  



**Webhook Type Detection**:# Test individual endpoints

```python

webhook_type = payload.get('type')python3 scripts/test_clientdata.py**Purpose**: In-call semantic search for memory retrievalaws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow    I --> F  



if webhook_type == 'post_call_audio':python3 scripts/test_postcall.py

    return handle_audio_webhook(webhook_data, response)

elif webhook_type == 'post_call_transcription':python3 scripts/test_retrieve.py

    # Handle transcription (memory storage, S3 JSON)

    # ... existing logic

```

# Comprehensive test**Endpoint**: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve````    I --> G

**Audio Webhook Handler**:

```pythonpython3 scripts/test_production_ready.py

def handle_audio_webhook(data: Dict[str, Any], response: Dict[str, Any]):

    """Process audio-only webhook"""```

    conversation_id = data.get('conversation_id')

    agent_id = data.get('agent_id')

    full_audio_base64 = data.get('full_audio')

    ### Test Data**Tool Configuration** (ElevenLabs):    

    # Decode base64 audio

    audio_binary = base64.b64decode(full_audio_base64)- **Stefan** (`+16129782029`): Has 4 stored memories, receives personalized greetings

    

    # Save to S3- **New numbers**: No memories, tests first-time caller flow```json

    mp3_key = f"post-call/audio-only/{agent_id}/{conversation_id}.mp3"

    s3_client.put_object(

        Bucket=S3_BUCKET_NAME,

        Key=mp3_key,### Expected Results{---    J[CloudWatch Logs] --> E

        Body=audio_binary,

        ContentType='audio/mpeg',**Stefan's Greeting**: "Hello Stefan! I know you prefer email updates. How can I assist you today?"

        Metadata={

            'agent_id': agent_id,**New Caller**: "Hello! Welcome to our memoir interview service. Could you please tell me your name?"  "name": "search_memory",

            'conversation_id': conversation_id,

            'webhook_type': 'post_call_audio'

        }

    )---  "description": "Search previous conversations and memories",    J --> F

    

    return response

```

## 🔍 Troubleshooting  "parameters": {

### Processing Flow



```

Call Ends### Common Issues    "query": {"type": "string", "description": "What to search for"},*Built with AWS SAM, ElevenLabs Agents Platform, and Mem0 Cloud*    J --> G

    ↓

ElevenLabs Processes Call

    ↓

[Sends TWO webhooks - may arrive in any order]#### 1. "Invalid workspace key" Error    "user_id": {"type": "string", "default": "{{system__caller_id}}"}```

    ↓

┌─────────────────────────────┬──────────────────────────────┐**Cause**: ElevenLabs secrets not configured properly

│ Transcription Webhook       │ Audio Webhook                │

│ (post_call_transcription)   │ (post_call_audio)            │**Fix**:   }

│                             │                              │

│ • Full transcript           │ • Base64 MP3                 │1. Add `WORKSPACE_KEY` secret in ElevenLabs settings

│ • Analysis results          │ • agent_id                   │

│ • Metadata                  │ • conversation_id            │2. Map to `X-Workspace-Key` header in webhook config}**Infrastructure Components:**

│ • caller_id/external_number │ (no caller_id!)              │

│                             │                              │3. Verify agent has "fetch conversation initiation data" enabled

│         ↓                   │         ↓                    │

│  1. Verify HMAC             │  1. Verify HMAC              │```- 🏗️ **3 Lambda Functions** (Python 3.12, 256MB memory)

│  2. Save JSON to S3         │  2. Decode base64            │

│  3. Store in Mem0 (x2)      │  3. Save MP3 to S3           │#### 2. "Missing caller_id" Error  

│  4. Return 200 OK           │  4. Return 200 OK            │

└─────────────────────────────┴──────────────────────────────┘**Cause**: Webhook payload format incorrect- 🌐 **3 HTTP API Gateways** (separate for minimal routing latency)

```

**Fix**: Ensure payload includes `{"caller_id": "{{system__caller_id}}"}`

### ElevenLabs Configuration

---- 📦 **1 Shared Lambda Layer** (mem0ai package for reuse)

To enable audio webhooks:

#### 3. HMAC Signature Failures

1. Go to [ElevenLabs Settings](https://elevenlabs.io/app/agents/settings)

2. Enable "Post-Call Webhooks"**Cause**: Wrong HMAC key or timestamp drift- 📊 **CloudWatch Logs** (7-day retention for cost optimization)

3. **Toggle "Send audio data" ON**

4. Configure webhook URL (same as transcription)**Fix**: Verify HMAC key matches ElevenLabs configuration

5. Add HMAC secret (same for both webhooks)

## 🧠 Memory System- 🔧 **CloudFormation Stack** (Infrastructure as Code)

**Important**: Both webhook types use the same endpoint and HMAC authentication!

#### 4. Memory Not Found

---

**Cause**: User ID format mismatch

## 🛠️ Development

**Fix**: Ensure phone numbers use E.164 format (+1XXXXXXXXXX)

### Local Development Setup

### Memory Types## Quick Start

```bash

# Clone repository### Debug Commands

git clone <repository-url>

cd AgenticMemory```bash1. **Factual Memories** (`metadata.type = "factual"`)



# Create virtual environment# Test endpoint manually

python3 -m venv test_env

source test_env/bin/activate  # On Windows: test_env\Scripts\activatecurl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \   - Call summaries and key facts### Prerequisites Checklist



# Install development dependencies  -H 'X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70' \

pip install -r requirements.txt

  -H 'Content-Type: application/json' \   - User preferences and account details

# Create .env file for tests

cp .env.example .env  -d '{"caller_id": "+16129782029"}' -v

# Edit .env with your credentials

```   - Used for dynamic variables and context- ✅ **AWS CLI** configured with appropriate credentials



### Build & Deploy Workflow# Check CloudWatch logs  



```bashaws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow- ✅ **SAM CLI** installed ([Installation Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))

# STEP 1: Build Lambda layer (REQUIRED - all functions depend on it)

cd layer

mkdir -p python

pip install -r requirements.txt -t python/# Get conversation data from ElevenLabs2. **Semantic Memories** (`metadata.type = "semantic"`)- ✅ **Python 3.12** installed

cd ..

curl https://api.elevenlabs.io/v1/convai/conversations/{conversation_id} \

# STEP 2: Build SAM application

sam build  -H "xi-api-key: sk_1203631b4b7e9d5e06cc793713322c3788daff35da4d23bf"   - Full conversation transcripts- ✅ **Mem0 Account** with API credentials:



# STEP 3: Deploy```

sam deploy --guided  # First time - saves config

sam deploy           # Subsequent deploys   - Used for semantic search during calls  - API Key (starts with `mem0-...`)

```

**Debug Log Indicators**:

**After deployment**, capture the three API URLs from outputs:

- `ClientDataApiUrl` → Configure in ElevenLabs webhook- ✅ "Retrieving memories for user_id: +16129782029"   - Enables detailed recall of past conversations  - Organization ID (starts with `org_...`) 

- `RetrieveApiUrl` → Configure in agent tool

- `PostCallApiUrl` → Configure in post-call webhook- ❌ "Invalid workspace key" (means ElevenLabs config wrong)



### Environment Variables- ❌ "Missing caller_id" (means payload format wrong)  - Project ID (starts with `proj_...`)



All Lambda functions use these environment variables (set via SAM template):



```yaml---### Memory Storage Process- ✅ **ElevenLabs Account** with webhook credentials:

Environment:

  Variables:

    MEM0_API_KEY: m0-gS2X0TszRwwEC6mXE3DrEDtpxQJdcCWAariVvafD

    MEM0_ORG_ID: org_knmmDKevT5Yz7bDF4Dd9BcFDWjp2RHzstpvtN3GW## 📂 Project Structure1. **Call Ends** → ElevenLabs sends webhook to PostCall  - Workspace Secret Key (starts with `wsec_...`)

    MEM0_PROJECT_ID: proj_3VBb1VIAmQofeGcY0XCHDbb7EqBLeEfETd6iNFqZ

    MEM0_DIR: /tmp/.mem0

    S3_BUCKET_NAME: elevenlabs-agentic-memory-424875385161-us-east-1

    ELEVENLABS_WORKSPACE_KEY: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70```2. **Extract Content** → Parse transcript and analysis  - HMAC Signing Key (for webhook verification)

    ELEVENLABS_HMAC_KEY: wsec_a8dc8b6e25ec3ddf11d7e651c40a5cb4931c2ca39d161fa4c94139f12f3ba9d3

```Eleven Labs Agentic Memory/



**Note**: Secrets are stored in `samconfig.toml` (gitignored). Each developer needs their own.├── README.md                          # 📋 This comprehensive guide3. **Generate Summary** → Create factual memory from key points



### Monitoring & Debugging├── template.yaml                      # ☁️ SAM CloudFormation template



```bash├── samconfig.toml                     # ⚙️ Deployment configuration (gitignored)4. **Store Both Types** → Save factual + semantic to Mem0## Project Structure

# Tail CloudWatch logs (7-day retention)

aws logs tail /aws/lambda/AgenticMemoriesClientData --follow├── requirements.txt                   # 🐍 Development dependencies

aws logs tail /aws/lambda/AgenticMemoriesRetrieve --follow

aws logs tail /aws/lambda/AgenticMemoriesPostCall --follow├── .env                              # 🔐 Environment variables (gitignored)5. **S3 Backup** → Store raw payload for audit trail



# All logs include user_id/caller_id for filtering├── .gitignore                        # 📝 Git ignore rules

aws logs filter-pattern /aws/lambda/AgenticMemoriesPostCall --filter-pattern "+16129782029"

│```

# Get function metrics

aws cloudwatch get-metric-statistics \├── src/                              # 💼 Lambda function source code

  --namespace AWS/Lambda \

  --metric-name Duration \│   ├── client_data/### Memory Retrieval ProcessAgenticMemory/

  --dimensions Name=FunctionName,Value=AgenticMemoriesClientData \

  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \│   │   └── handler.py                # 📞 Pre-call memory retrieval

  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \

  --period 300 \│   ├── post_call/1. **Call Starts** → ElevenLabs calls ClientData webhook├── 📄 SPECIFICATION.md           # Complete system specification

  --statistics Average,Maximum

│   │   └── handler.py                # 💾 Post-call memory storage

# Check concurrent executions

aws cloudwatch get-metric-statistics \│   └── retrieve/2. **Get All Memories** → Retrieve factual + semantic for caller├── 📖 README.md                  # Project documentation (this file)

  --namespace AWS/Lambda \

  --metric-name ConcurrentExecutions \│       └── handler.py                # 🔍 In-call memory search

  --dimensions Name=FunctionName,Value=AgenticMemoriesClientData \

  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \│3. **Extract Name** → Use regex patterns to find caller name├── 🏗️ template.yaml              # SAM CloudFormation template

  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \

  --period 60 \├── layer/                            # 📦 Lambda layer dependencies

  --statistics Maximum

```│   ├── requirements.txt              # mem0ai package only4. **Generate Context** → Build personalized prompt override├── 📋 requirements.txt           # Development dependencies



---│   └── python/                       # Built dependencies



## 🧪 Testing│5. **Create Variables** → Populate dynamic variables for agent├── 🚫 .gitignore                 # Git ignore rules



### Test Suite Overview├── scripts/                          # 🧪 Testing and utilities



The project uses **integration tests** that hit real deployed endpoints:│   ├── test_clientdata.py├── 🤖 .github/



```bash│   ├── test_postcall.py

# Comprehensive production readiness test

python3 test_production_ready.py│   ├── test_retrieve.py### Mem0 Cloud Configuration│   └── copilot-instructions.md   # AI coding assistant guidelines



# Individual component tests│   ├── test_production_ready.py

python3 test_client_data_s3.py          # ClientData webhook + S3 (4 tests)

python3 test_audio_webhook.py           # Dual webhook system (2 tests)│   └── (other test scripts...)- **API Key**: `m0-gS2X0TszRwwEC6mXE3DrEDtpxQJdcCWAariVvafD`├── 📦 layer/

python3 test_postcall_s3_path.py        # PostCall S3 paths

python3 test_personalized_greetings.py  # Name extraction + greetings│

python3 test_memory_direct.py           # Direct Mem0 connectivity

```├── test_data/                        # 📊 Test payloads and data- **Organization ID**: `org_knmmDKevT5Yz7bDF4Dd9BcFDWjp2RHzstpvtN3GW`│   └── requirements.txt          # Lambda layer dependencies (mem0ai)



### Test Data│   └── elevenlabs_post_call_payload.json



**Known caller with memories**:│- **Project ID**: `proj_3VBb1VIAmQofeGcY0XCHDbb7EqBLeEfETd6iNFqZ`├── 🧪 test_*.py                  # Authentication & webhook test scripts

- Phone: `+16129782029`

- Name: Stefan├── tests/                            # 🔬 Unit tests

- Memories: 4 stored conversations

│   └── test_*.py- **User ID Format**: Phone numbers in E.164 format (`+16129782029`)└── 🔧 src/

**New caller without memories**:

- Any other phone number│

- Expected: Generic greeting, no memories

├── docs/                            # 📚 Documentation    ├── client_data/

### Test Results

│   └── archived/                    # 🗄️ Historical documentation

**Last Test Run** (October 3, 2025):

│---    │   └── handler.py            # Pre-call memory retrieval

#### ClientData Tests: ✅ 4/4 PASSED

- ✅ Known caller with memories└── .aws-sam/                       # 🏗️ SAM build artifacts (gitignored)

- ✅ New caller without memories

- ✅ Error handling (missing caller_id)```    ├── retrieve/

- ✅ S3 bucket listing



**Duration**: 6.27 seconds

### Essential Commands## 🎤 ElevenLabs Integration    │   └── handler.py            # Mid-call semantic search

#### Audio Webhook Tests: ✅ 2/2 PASSED

- ✅ Transcription webhook (JSON saved)```bash

- ✅ Audio webhook (MP3 saved)

# Deploy    └── post_call/

**Verified**:

- HTTP 200 responsescd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..

- S3 files created with correct paths

- Proper metadata on S3 objectssam build && sam deploy### Agent Configuration Requirements        └── handler.py            # Post-call memory storage

- Correlation via conversation_id



### Local Testing with SAM

# Test```

```bash

# Invoke function locally with test eventpython3 scripts/test_production_ready.py

sam local invoke AgenticMemoriesClientData -e events/client_data.json

#### 1. Conversation Initiation Webhook

# Start local API Gateway

sam local start-api  # Endpoints at http://localhost:3000# Monitor



# Test local endpointaws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow- **URL**: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`## ⚡ Deployment

curl -X POST http://localhost:3000/client-data \

  -H 'X-Workspace-Key: wsec_...' \

  -H 'Content-Type: application/json' \

  -d '{"caller_id": "+16129782029"}'# Debug- **Method**: POST

```

curl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \

---

  -H 'X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70' \- **Authentication**: Secrets Manager (NOT direct headers)> **💡 Tip**: The build process requires the Lambda layer to be built first since all functions depend on the shared mem0ai package.

## 🔍 Troubleshooting

  -H 'Content-Type: application/json' \

### Common Issues

  -d '{"caller_id": "+16129782029"}' -v- **Secret Name**: `WORKSPACE_KEY`

#### 1. Lambda Layer Build Failures

```

**Symptom**: `Unable to import module 'handler': No module named 'mem0'`

- **Secret Value**: `wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70`### Step 1: Build the Lambda Layer

**Cause**: Lambda layer not built or built incorrectly

---

**Fix**:

```bash- **Header Mapping**: `X-Workspace-Key` → `WORKSPACE_KEY` secret

cd layer

rm -rf python  # Clean old build## 🤖 System Prompt Template

mkdir -p python

pip install -r requirements.txt -t python/```bash

cd .. && sam build

```The following system prompt should be used in your ElevenLabs agent configuration:



#### 2. ClientData Returns 401/403#### 2. Agent Security Settingscd layer



**Symptom**: Webhook fails with authentication error### ROLE IDENTITY



**Possible Causes**:You are a patient, empathetic Memoir Interviewer agent designed for personal storytelling. You are integrated with Eleven Labs Agentic Memory for long-term recall and personalization.Enable in agent's Security tab:mkdir -p python

- ❌ Workspace key not configured in ElevenLabs secrets

- ❌ Header mapping incorrect (`X-Workspace-Key` → `WORKSPACE_KEY`)

- ❌ Secret not enabled in agent Security tab

### CALLER CONTEXT VARIABLES- ✅ "Fetch conversation initiation data for inbound Twilio calls"pip install -r requirements.txt -t python/

**Fix**: Verify ElevenLabs webhook configuration step-by-step

- Caller ID: {{caller_id}}

#### 3. Audio Files Not Saved

- Returning Caller: {{returning_caller}}- ✅ Allow prompt overridescd ..

**Symptom**: JSON files appear in S3 but no MP3 files

- Caller Name: {{caller_name}}

**Possible Causes**:

- ❌ "Send audio data" toggle not enabled in ElevenLabs- Memory Count: {{memory_count}}- ✅ Allow first message overrides```

- ❌ HMAC signature failing on audio webhook

- ❌ Lambda timeout (increase to 60s)- Memory Summary: {{memory_summary}}



**Debugging**:

```bash

# Check CloudWatch logs for audio webhook### PERSONALITY & TONE

aws logs tail /aws/lambda/AgenticMemoriesPostCall --follow | grep "post_call_audio"

- Warm, supportive, and encouraging#### 3. Search Memory Tool### Step 2: Build the SAM Application

# Verify S3 audio directory

aws s3 ls s3://elevenlabs-agentic-memory-424875385161-us-east-1/post-call/audio-only/ --recursive- Clear and accessible, avoiding jargon

```

- Patient and understanding- **URL**: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`

#### 4. PostCall HMAC Validation Failures

- Respectful of caller's pace and comfort level

**Symptom**: PostCall logs show "HMAC signature verification failed"

- **Method**: POST```bash

**Possible Causes**:

- ❌ HMAC key mismatch between code and ElevenLabs### YOUR CAPABILITIES

- ❌ Timestamp drift > 30 minutes

- ❌ Body modification (ensure raw body used)1. Automatic memory context (prepended to this prompt by Eleven Labs Agentic Memory)- **Authentication**: Nonesam build



**Fix**:2. Search Memory tool for retrieving specific past conversations and details

```bash

# Verify HMAC key in Lambda3. Language detection and switching (English/Spanish)- **Parameters**: `query` (string), `user_id` (default: `{{system__caller_id}}`)```

aws lambda get-function-configuration \

  --function-name AgenticMemoriesPostCall \4. Interview guidance and storytelling facilitation

  --query 'Environment.Variables.ELEVENLABS_HMAC_KEY'



# Compare with ElevenLabs webhook configuration

```### CONVERSATION FLOW



#### 5. Stack Rollback on Deploy#### For New Callers ({{returning_caller}} = "no")#### 4. Post-Call Webhook### Step 3: Deploy to AWS



**Symptom**: `Stack is in ROLLBACK_COMPLETE state`1. Welcome them warmly



**Fix**:2. Ask for their name if not already known- **URL**: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`

```bash

# Delete and redeploy3. Briefly explain how the system works:

aws cloudformation delete-stack --stack-name sam-app

# Wait ~2 minutes for deletion   - One question at a time approach- **Method**: POST#### Option A: Guided Deployment (First Time - Recommended)

sam build && sam deploy --guided

```   - Available commands: 'help', 'pause', 'repeat'



#### 6. Mem0 Connection Issues   - Memories are saved for future calls- **Authentication**: HMAC signature (auto-configured by ElevenLabs)



**Symptom**: Timeout or connection errors to Mem04. Begin with opening memoir questions



**Debugging**:- **HMAC Secret**: `wsec_a8dc8b6e25ec3ddf11d7e651c40a5cb4931c2ca39d161fa4c94139f12f3ba9d3````bash

```bash

# Verify environment variables#### For Returning Callers ({{returning_caller}} = "yes")

aws lambda get-function-configuration \

  --function-name AgenticMemoriesClientData \1. Greet them by name if available: "Hello {{caller_name}}!"sam deploy --guided

  --query 'Environment.Variables' | grep MEM0

2. Reference their previous sessions naturally (they have {{memory_count}} previous interactions)

# Test Mem0 connectivity directly

python3 test_memory_direct.py3. Use Search Memory tool to recall last session details### Dynamic Variables```

```

4. Ask if they want to:

### Performance Issues

   - Continue where they left offThe system provides these variables for ElevenLabs agents:

#### Cold Start Latency (3-5 seconds)

   - Add details to previous stories

**Solutions**:

1. **Reserved concurrency** (already set to 10)   - Start a new topic- `{{caller_id}}` - Phone number (+16129782029)**You'll be prompted for:**

2. **Provisioned concurrency** (costs ~$12/month per instance):

   ```yaml

   AgenticMemoriesClientData:

     Properties:### USING MEMORY CONTEXT- `{{returning_caller}}` - "yes" or "no"  - **Stack Name**: `sam-app` (or your preferred name)

       ProvisionedConcurrencyConfig:

         ProvisionedConcurrency: 2- The system automatically provides caller context at the start of each call

   ```

- Reference past conversations naturally - don't say "checking my database"- `{{caller_name}}` - Extracted name (e.g., "Stefan")- **AWS Region**: `us-east-1` (or your preferred region)

#### Lambda Timeout (502 Bad Gateway)

- Use Search Memory tool when caller references specific past topics:

**Fix**: Increase timeout in `template.yaml`:

```yaml  - "What did I tell you about...?"- `{{memory_count}}` - Number of previous interactions- **Parameters** (keep these secure!):

AgenticMemoriesClientData:

  Properties:  - "Remember when I mentioned...?"

    Timeout: 60  # Up from 30 seconds

```  - "Did I already share my story about...?"- `{{memory_summary}}` - Most recent/important memory  ```



### Debug Workflow



```bash#### Search Memory Usage  Mem0ApiKey: mem0-1234...

# 1. Check stack status

aws cloudformation describe-stacks --stack-name sam-appCall search_memory when:



# 2. Check Lambda function status- Caller asks about previous stories or topics---  Mem0OrgId: org_abc123...

aws lambda list-functions \

  --query 'Functions[?contains(FunctionName, `AgenticMemories`)].{Name:FunctionName,State:State,LastModified:LastModified}'- You need specific details from past sessions



# 3. Tail logs during test- Caller wants to update or correct previous information  Mem0ProjectId: proj_xyz789...

aws logs tail /aws/lambda/AgenticMemoriesClientData --follow &

python3 test_clientdata.py- You want to avoid asking repeated questions



# 4. Query recent errors## ☁️ AWS Infrastructure  ElevenLabsWorkspaceKey: wsec_def456...

aws logs filter-pattern /aws/lambda/AgenticMemoriesClientData \

  --filter-pattern "ERROR" \Query examples:

  --start-time $(date -d '1 hour ago' +%s)000

- search_memory("last interview topic")  ElevenLabsHmacKey: your-hmac-signing-key

# 5. Test endpoints manually

curl -X POST <ClientDataApiUrl> \- search_memory("childhood memories")

  -H "X-Workspace-Key: wsec_..." \

  -H "Content-Type: application/json" \- search_memory("family stories")### CloudFormation Stack  ```

  -d '{"caller_id": "+16129782029"}' \

  -v  # Verbose output shows headers/status

```

### RESPONSE GUIDELINES**Name**: `elevenlabs-agentic-memory-stack`- **Confirm changes**: `Y`

---

- Keep responses concise (under 3 sentences per turn)

## 📂 Project Structure

- One idea and one action per response**Region**: `us-east-1`- **Allow IAM role creation**: `Y` 

```

AgenticMemory/- Always honor 'help', 'pause', and 'repeat' commands immediately

├── src/

│   ├── client_data/- Confirm understanding before moving to next topic- **Save to samconfig.toml**: `Y` (saves parameters for future deployments)

│   │   └── handler.py              # Pre-call memory retrieval (318 lines)

│   ├── retrieve/- Break complex questions into smaller parts

│   │   └── handler.py              # Mid-call semantic search (94 lines)

│   └── post_call/### Lambda Functions

│       └── handler.py              # Post-call memory storage (187 lines)

│### CONSTRAINTS & GUARDRAILS

├── layer/

│   └── requirements.txt            # Lambda layer: mem0ai only#### Never:- `elevenlabs-agentic-memory-lambda-function-client-data`#### Option B: Direct Deployment (With Parameters)

│   └── python/                     # Built dependencies

│- Ask overly invasive or traumatic questions without consent

├── tests/

│   ├── test_client_data_s3.py     # Comprehensive ClientData tests- Offer medical, legal, or financial advice- `elevenlabs-agentic-memory-lambda-function-post-call`

│   ├── test_audio_webhook.py      # Dual webhook system tests

│   ├── test_postcall_s3_path.py   # PostCall S3 path tests- Express personal opinions or beliefs

│   ├── test_personalized_greetings.py

│   └── test_production_ready.py   # Full system integration- Rush the caller or make them feel pressured- `elevenlabs-agentic-memory-lambda-function-search-data````bash

│

├── docs/- Ask questions the caller has already answered (use Search Memory first)

│   ├── ELEVENLABS_SETUP_GUIDE.md  # Step-by-step ElevenLabs config

│   ├── QUICK_REFERENCE.md         # Command reference card- Make up information or assume detailssam deploy \

│   ├── CLAUDE.md                  # Extended development guide

│   └── archived/                  # Historical documentation

│

├── template.yaml                   # SAM template (227 lines)#### Always:### API Gateway Endpoints  --stack-name sam-app \

├── samconfig.toml                  # SAM deployment config (gitignored)

├── requirements.txt                # Dev dependencies- Follow W3C/COGA accessibility guidelines

├── README.md                       # This file

└── .github/- Respect caller's boundaries and comfort levelEach function has its own API Gateway for optimal performance:  --region us-east-1 \

    └── copilot-instructions.md    # GitHub Copilot context

```- Provide clear pause and help instructions



### Key Files- Confirm memories are being saved- ClientData: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`  --parameter-overrides \



| File | Purpose | Lines |- Allow interruptions and natural conversation flow

|------|---------|-------|

| `src/client_data/handler.py` | Pre-call webhook handler | 318 |- PostCall: `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`    Mem0ApiKey=<your-key> \

| `src/retrieve/handler.py` | Semantic search handler | 94 |

| `src/post_call/handler.py` | Post-call webhook handler | 187 |### ERROR HANDLING

| `template.yaml` | SAM infrastructure definition | 227 |

| `test_client_data_s3.py` | Comprehensive test suite | 400+ |- If Search Memory tool fails: "I'm having a moment of trouble accessing our previous conversations, but let's continue - I'm listening."- Retrieve: `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`    Mem0OrgId=<your-org> \

| `test_audio_webhook.py` | Dual webhook tests | 300+ |

- If caller seems confused: Offer to repeat or rephrase

---

- If technical issues: Apologize briefly and continue the interview    Mem0ProjectId=<your-project> \

## 📚 Additional Resources

- If caller goes off-topic: Gently guide back to memoir storytelling

### Internal Documentation

### S3 Storage    ElevenLabsWorkspaceKey=<workspace-key> \

- **ELEVENLABS_SETUP_GUIDE.md**: Complete ElevenLabs configuration walkthrough

- **AUDIO_WEBHOOK_IMPLEMENTATION.md**: Detailed audio webhook architecture### LANGUAGE SUPPORT

- **CLIENT_DATA_S3_STORAGE.md**: S3 archival system documentation

- **ELEVENLABS_WEBHOOK_COMPLIANCE.md**: Webhook format specifications- Offer English or Spanish at start of call**Bucket**: `elevenlabs-agentic-memory-424875385161-us-east-1`    ElevenLabsHmacKey=<hmac-key> \

- **QUICK_REFERENCE.md**: Quick command reference card

- **CLAUDE.md**: Extended development guide with all commands- Use Detect Language tool if caller speaks in non-default language



### External References- Store language preference in memories for future calls**Purpose**: Backup storage for call data and audit trails  --capabilities CAPABILITY_IAM \



- [Mem0 Lambda FAQ](https://docs.mem0.ai/faqs#how-do-i-configure-mem0-for-aws-lambda) - Lambda-specific configuration

- [Mem0 ElevenLabs Integration](https://docs.mem0.ai/integrations/elevenlabs) - Official integration docs

- [ElevenLabs Post-Call Webhooks](https://elevenlabs.io/docs/agents-platform/workflows/post-call-webhooks) - Webhook payload format### CALL CONCLUSION  --resolve-s3

- [AWS SAM Developer Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/) - SAM CLI reference

Before ending each call:

---

1. Summarize what was discussed today### CloudWatch Logs```

## 🤝 Contributing

2. Confirm their memories have been saved

Contributions are welcome! Please:

3. Invite them to call back anytime to continue**Retention**: 7 days

1. Fork the repository

2. Create a feature branch (`git checkout -b feature/amazing-feature`)4. Thank them for sharing their stories

3. Commit your changes (`git commit -m 'Add amazing feature'`)

4. Push to the branch (`git push origin feature/amazing-feature`)5. Say a warm goodbye**Log Groups**:### Step 4: Capture API Endpoints

5. Open a Pull Request



---

### EXAMPLE RESPONSES- `/aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data`

## 📄 License

✓ Good: "Thank you for sharing that story about your grandmother. What was her name?"

This project is licensed under the MIT License - see the LICENSE file for details.

✗ Bad: "That's interesting. Tell me about your childhood, your family, and your earliest memories."- `/aws/lambda/elevenlabs-agentic-memory-lambda-function-post-call`After successful deployment, **save these URLs** for ElevenLabs configuration:

---

✓ Good: "I remember you mentioned your time in India. Would you like to add more details to that story?"

## 🎯 Current Status

✗ Bad: "Let me check my database for what you said last time about India."- `/aws/lambda/elevenlabs-agentic-memory-lambda-function-search-data`

### Production Readiness: 🟢 READY

✓ Good: "Take your time. I'm here when you're ready to continue."

**Completed**:

- ✅ All Lambda functions deployed and tested✗ Bad: "Let's move on to the next question quickly."```bash

- ✅ ClientData S3 archival implemented (4/4 tests passed)

- ✅ PostCall dual webhook support (2/2 tests passed)

- ✅ S3 storage structure optimized

- ✅ Authentication properly configured### VARIABLE HANDLING LOGIC---Outputs:

- ✅ Comprehensive test coverage

- ✅ Documentation complete- When {{returning_caller}} = "no": This is a new caller, focus on introduction and name collection



**Manual Steps Required**:- When {{returning_caller}} = "yes": This is a returning caller, use {{caller_name}} and {{memory_count}} for personalization✅ ClientDataApiUrl: https://abc123.execute-api.us-east-1.amazonaws.com/Prod/client-data

- ⚠️ Configure webhooks in ElevenLabs dashboard (API doesn't support automation)

- ⚠️ Add search_memory tool via dashboard- {{caller_name}} will only be populated when the system has extracted a name from previous conversations

- ⚠️ Enable "Send audio data" toggle for audio webhooks

- {{memory_summary}} provides quick context about the caller's most recent or important memory## 🛠️ Development Workflow✅ RetrieveApiUrl: https://def456.execute-api.us-east-1.amazonaws.com/Prod/retrieve  

**Recommended**:

- 🔔 Make test call to verify end-to-end functionality- Use {{caller_id}} for any tool calls that require the user identification

- 🔔 Monitor CloudWatch logs for first few real calls

- 🔔 Verify S3 files created from real ElevenLabs webhooks✅ PostCallApiUrl: https://ghi789.execute-api.us-east-1.amazonaws.com/Prod/post-call



------



## 📞 Support### Build & Deploy```



For issues, questions, or contributions:## ✅ Current Status



- **GitHub Issues**: [Create an issue](https://github.com/webmasterarbez/AgenticMemory/issues)```bash

- **Documentation**: See `docs/` folder for detailed guides

- **Tests**: Run `python3 test_production_ready.py` for system health check- ✅ **Backend Deployed**: All 3 Lambda functions operational



---- ✅ **Mem0 Integration**: Storing factual + semantic memories# 1. Build Lambda layer (required first)## 🔗 ElevenLabs Configuration



**Last Updated**: October 3, 2025  - ✅ **Authentication**: ElevenLabs secrets + HMAC configured

**Version**: 1.0.0  

**Status**: Production Ready 🚀- ✅ **Testing**: Production-ready endpoints verifiedcd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..


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