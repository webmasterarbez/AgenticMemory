# AgenticMemory Project Structure

```
AgenticMemory/
├── MASTER_DOCUMENTATION.md           # 📋 Complete project guide
├── CORRECTED_MEMOIR_SYSTEM_PROMPT.md # 🤖 ElevenLabs agent system prompt
├── template.yaml                     # ☁️ SAM CloudFormation template
├── samconfig.toml                    # ⚙️ Deployment configuration (gitignored)
├── requirements.txt                  # 🐍 Development dependencies
├── .env                             # 🔐 Environment variables (gitignored)
├── .gitignore                       # 📝 Git ignore rules
│
├── src/                             # 💼 Lambda function source code
│   ├── client_data/
│   │   └── handler.py               # 📞 Pre-call memory retrieval
│   ├── post_call/
│   │   └── handler.py               # 💾 Post-call memory storage
│   └── retrieve/
│       └── handler.py               # 🔍 In-call memory search
│
├── layer/                           # 📦 Lambda layer dependencies
│   ├── requirements.txt             # mem0ai package only
│   └── python/                      # Built dependencies
│
├── scripts/                         # 🧪 Testing and utilities
│   ├── test_clientdata.py
│   ├── test_postcall.py
│   ├── test_retrieve.py
│   ├── test_production_ready.py
│   └── (other test scripts...)
│
├── test_data/                       # 📊 Test payloads and data
│   └── elevenlabs_post_call_payload.json
│
├── tests/                           # 🔬 Unit tests
│   └── test_*.py
│
├── docs/                           # 📚 Documentation
│   └── archived/                   # 🗄️ Historical documentation
│       ├── README.md
│       ├── SPECIFICATION.md
│       ├── CLAUDE.md
│       └── (other archived docs...)
│
└── .aws-sam/                      # 🏗️ SAM build artifacts (gitignored)
```

## Key Files

### Essential Documents
- **`MASTER_DOCUMENTATION.md`** - Single source of truth for the entire project
- **`CORRECTED_MEMOIR_SYSTEM_PROMPT.md`** - ElevenLabs agent configuration

### Core Infrastructure  
- **`template.yaml`** - AWS SAM template defining all resources
- **`src/`** - Lambda function code (3 functions)
- **`layer/`** - Shared dependencies (mem0ai package)

### Development Tools
- **`scripts/`** - Testing utilities and debug tools
- **`.env`** - Local environment configuration
- **`samconfig.toml`** - Deployment settings

## Quick Commands

### Deploy
```bash
cd layer && mkdir -p python && pip install -r requirements.txt -t python/ && cd ..
sam build && sam deploy
```

### Test
```bash
python3 scripts/test_production_ready.py
```

### Monitor
```bash
aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow
```

### Debug
```bash
curl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \
  -H 'X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70' \
  -H 'Content-Type: application/json' \
  -d '{"caller_id": "+16129782029"}' -v
```

---
*See `MASTER_DOCUMENTATION.md` for complete details*