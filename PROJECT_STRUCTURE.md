# AgenticMemory Project Structure

Complete guide to the project organization and file locations.

## 📂 Directory Overview

```
AgenticMemory/
├── 📁 src/                     # Lambda function source code
├── 📁 layer/                   # Shared Lambda layer
├── 📁 docs/                    # All documentation (13 files)
├── 📁 scripts/                 # Test & utility scripts (25+ files)
├── 📁 test_data/               # JSON test payloads (4 files)
├── 📁 tests/                   # Unit tests
├── 📁 .github/                 # GitHub configuration
├── 📁 .aws-sam/                # SAM build output (gitignored)
├── 📁 test_env/                # Python virtual env (gitignored)
├── 📄 template.yaml            # SAM deployment template
├── 📄 samconfig.toml           # SAM config with secrets (gitignored)
├── 📄 requirements.txt         # Dev dependencies
├── 📄 .env                     # Environment variables (gitignored)
└── 📄 README.md                # Main project documentation
```

---

## 🗂️ Detailed Structure

### `/src/` - Lambda Functions (3 handlers)

```
src/
├── client_data/
│   └── handler.py              # Pre-call memory retrieval + greeting generation
├── retrieve/
│   └── handler.py              # Mid-call semantic search
└── post_call/
    └── handler.py              # Async memory storage (factual + semantic)
```

**Purpose**: Core Lambda function code deployed to AWS
- Each folder becomes a separate Lambda function
- Handlers import from Lambda layer (`mem0ai`)
- Environment variables configured in `template.yaml`

**Key Files**:
- `client_data/handler.py` (318 lines) - Workspace key auth, get_all(), name extraction, greeting gen
- `retrieve/handler.py` (94 lines) - No auth, search() with limit
- `post_call/handler.py` (187 lines) - HMAC validation, async add() x2 memory types

---

### `/layer/` - Shared Lambda Layer

```
layer/
├── requirements.txt            # ONLY mem0ai package
└── python/                     # Built layer (gitignored)
    ├── mem0/
    ├── openai/
    ├── qdrant_client/
    └── ... (all dependencies)
```

**Purpose**: Shared Python packages across all Lambda functions
- Build with: `cd layer && pip install -r requirements.txt -t python/`
- Contains ONLY `mem0ai` package and its dependencies
- Reused by all three Lambda functions for efficiency

**Important**: Dev dependencies (pytest, boto3) are in root `requirements.txt`, NOT in layer

---

### `/docs/` - Documentation (13 files)

```
docs/
├── README.md                   # 📚 Documentation index
├── SPECIFICATION.md            # Complete technical spec (627 lines)
├── SYSTEM_FLOW.md              # Visual flow diagrams
├── CLAUDE.md                   # Extended dev guide (323 lines)
├── ELEVENLABS_SETUP_GUIDE.md   # Step-by-step integration
├── QUICK_REFERENCE.md          # Command reference card
├── CHANGELOG.md                # Version history
├── USING_TEST_SCRIPT.md        # Comprehensive test guide
├── TEST_SCRIPT_QUICK_GUIDE.md  # Quick test reference
├── HOW_TO_USE_TEST_SCRIPT.md   # Detailed test docs
├── TEST_RESULTS.md             # General test results
├── POSTCALL_TEST_RESULTS.md    # PostCall test results
├── TEST_SUMMARY_CONV_SHEILA.md # Sheila conversation tests
└── POSTCALL_FIX_SUMMARY.md     # Bug fix summaries
```

**Purpose**: All project documentation organized by category
- **Start here**: `README.md` for documentation index
- **Architecture**: `SPECIFICATION.md`, `SYSTEM_FLOW.md`
- **Setup**: `ELEVENLABS_SETUP_GUIDE.md`, `QUICK_REFERENCE.md`
- **Testing**: `USING_TEST_SCRIPT.md`, `TEST_SCRIPT_QUICK_GUIDE.md`
- **Debugging**: `POSTCALL_FIX_SUMMARY.md`, `CLAUDE.md`

---

### `/scripts/` - Test & Utility Scripts (25+ files)

```
scripts/
├── README.md                       # 🧪 Scripts index
│
├── 🎯 PostCall Testing (10 files)
│   ├── test_postcall_with_file.py  # ⭐ RECOMMENDED - Reusable test tool
│   ├── test_postcall.sh            # Bash wrapper with color output
│   ├── test_postcall.py            # Original interactive test
│   ├── test_postcall_simple.py
│   ├── test_postcall_debug.py
│   ├── test_postcall_simple_debug.py
│   ├── test_post_call_comprehensive.py
│   ├── test_post_call_simple.py
│   ├── test_real_payload.py
│   └── test_real_elevenlabs_payload.py
│
├── 🎯 ClientData Testing (3 files)
│   ├── test_clientdata.py
│   ├── test_clientdata_simple.py
│   └── test_personalized_greetings.py
│
├── 🎯 Retrieve Testing (2 files)
│   ├── test_retrieve.py
│   └── test_retrieve_simple.py
│
├── 🎯 Authentication Testing (2 files)
│   ├── test_hmac_auth.py
│   └── test_elevenlabs_hmac.py
│
├── 🎯 Integration Testing (2 files)
│   ├── test_production_ready.py    # ⭐ Comprehensive 3-endpoint check
│   └── final_test.py
│
├── 🎯 Utilities (5 files)
│   ├── test_memory_direct.py       # Direct Mem0 connectivity
│   ├── verify_sheila_memories.py   # Verify user memories
│   ├── test_sheila_call.py
│   ├── debug_elevenlabs.py
│   └── test_fixed_handler.sh
```

**Purpose**: All test scripts and utilities
- **Quick testing**: `./test_postcall.sh ../test_data/conv_*.json`
- **Comprehensive**: `python3 test_production_ready.py`
- **Specific endpoints**: `test_clientdata.py`, `test_retrieve.py`

**Most Used**:
1. `test_postcall_with_file.py` - Test PostCall with any conversation
2. `test_production_ready.py` - Test all 3 endpoints at once
3. `test_postcall.sh` - Bash wrapper with .env support

---

### `/test_data/` - JSON Test Payloads (4 files)

```
test_data/
├── README.md                               # 📋 Test data index
├── conv_01jxd5y165f62a0v7gtr6bkg56.json   # 161-message conversation (Sheila)
├── conv_01jxk1wejhenk8x8tt9enzxw4a.json   # 115-message conversation (Sheila)
├── elevenlabs_post_call_payload.json      # Sample array format payload
└── corrected_postcall_payload.json        # Sample object format payload
```

**Purpose**: Real conversation files and sample payloads for testing
- `conv_*.json` - Actual ElevenLabs webhook payloads from real calls
- `*_payload.json` - Reference structures for development

**Usage**:
```bash
cd scripts
./test_postcall.sh ../test_data/conv_01jxd5y165f62a0v7gtr6bkg56.json
```

---

### `/tests/` - Unit Tests

```
tests/
├── test_client_data_unit.py
└── __pycache__/
```

**Purpose**: Unit tests with mocked dependencies
- Different from integration tests in `/scripts/`
- Mock Mem0 client for isolated testing
- Run with: `pytest tests/`

---

### Root Configuration Files

```
├── template.yaml           # SAM deployment template (227 lines)
│                           # Defines: 3 Lambdas, 3 APIs, 1 layer, env vars
│
├── samconfig.toml          # SAM configuration (gitignored)
│                           # Contains: secrets, region, stack name
│
├── requirements.txt        # Dev dependencies (NOT deployed)
│                           # Contains: pytest, boto3, python-dotenv
│
├── .env                    # Environment variables (gitignored)
│                           # Contains: API URLs, keys, credentials
│
└── .gitignore              # Git ignore rules
```

---

## 🎯 Common Tasks & File Locations

### Deploy the Application
**Files**: `template.yaml`, `samconfig.toml`, `layer/requirements.txt`
```bash
# Build layer
cd layer && pip install -r requirements.txt -t python/ && cd ..

# Build and deploy
sam build --use-container
sam deploy
```

### Test PostCall Endpoint
**Files**: `scripts/test_postcall_with_file.py`, `test_data/*.json`
```bash
cd scripts
./test_postcall.sh ../test_data/conv_01jxd5y165f62a0v7gtr6bkg56.json
```

### Modify Lambda Functions
**Files**: `src/*/handler.py`, `template.yaml`
1. Edit: `src/post_call/handler.py` (or other handler)
2. Build: `sam build --use-container`
3. Deploy: `sam deploy`

### Add Test Data
**Files**: `test_data/*.json`
1. Save ElevenLabs payload to `test_data/your_file.json`
2. Test: `cd scripts && ./test_postcall.sh ../test_data/your_file.json`

### Update Documentation
**Files**: `docs/*.md`
- Architecture: Edit `docs/SPECIFICATION.md` or `docs/SYSTEM_FLOW.md`
- Testing: Edit `docs/USING_TEST_SCRIPT.md`
- Quick ref: Edit `docs/QUICK_REFERENCE.md`

### Monitor Logs
**Command**:
```bash
aws logs tail /aws/lambda/AgenticMemoriesClientData --follow
aws logs tail /aws/lambda/AgenticMemoriesRetrieve --follow
aws logs tail /aws/lambda/AgenticMemoriesPostCall --follow
```

---

## 📊 File Count Summary

| Directory | Files | Purpose |
|-----------|-------|---------|
| `/src/` | 3 handlers | Lambda function code |
| `/layer/` | 1 requirements.txt | Shared dependencies |
| `/docs/` | 13 markdown files | All documentation |
| `/scripts/` | 25+ Python/bash | Test & utility scripts |
| `/test_data/` | 4 JSON files | Test payloads |
| `/tests/` | 1 unit test | Mocked tests |
| **Total** | **45+ files** | Complete project |

---

## 🔍 Finding Files

### By Purpose

**I want to...**
- **Deploy**: `template.yaml`, `layer/requirements.txt`
- **Test PostCall**: `scripts/test_postcall_with_file.py`
- **Test all endpoints**: `scripts/test_production_ready.py`
- **Understand architecture**: `docs/SPECIFICATION.md`
- **Setup ElevenLabs**: `docs/ELEVENLABS_SETUP_GUIDE.md`
- **Debug issues**: `docs/POSTCALL_FIX_SUMMARY.md`
- **Quick commands**: `docs/QUICK_REFERENCE.md`

### By File Type

**Documentation (`.md`)**: `/docs/` directory
**Python scripts (`.py`)**: `/scripts/` directory
**Test data (`.json`)**: `/test_data/` directory
**Lambda code (`.py`)**: `/src/` directory
**Configuration (`.yaml`, `.toml`)**: Project root

---

## 🚀 Getting Started Path

1. **Read**: [README.md](README.md) - Project overview
2. **Deploy**: Follow build instructions in README
3. **Setup**: [docs/ELEVENLABS_SETUP_GUIDE.md](docs/ELEVENLABS_SETUP_GUIDE.md)
4. **Test**: [scripts/test_postcall.sh](scripts/test_postcall.sh)
5. **Monitor**: CloudWatch logs (see README)

---

## 📝 Maintenance

**Regularly updated files**:
- `docs/CHANGELOG.md` - After each release
- `docs/TEST_RESULTS.md` - After test runs
- `test_data/*.json` - New conversation samples
- `scripts/test_*.py` - New test scenarios

**Rarely changed files**:
- `template.yaml` - Only for infrastructure changes
- `src/*/handler.py` - Only for bug fixes/features
- `layer/requirements.txt` - Only for dependency updates

---

## 🔗 Related Resources

- **GitHub**: https://github.com/webmasterarbez/AgenticMemory
- **Mem0 Docs**: https://docs.mem0.ai/
- **ElevenLabs Docs**: https://elevenlabs.io/docs/
- **AWS SAM Docs**: https://docs.aws.amazon.com/serverless-application-model/
