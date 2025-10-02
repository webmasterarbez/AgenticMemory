# Test Scripts & Utilities

This directory contains all test scripts and utilities for the AgenticMemory project.

## 🚀 Main Test Scripts

### PostCall Endpoint Testing
- **`test_postcall_with_file.py`** ⭐ **RECOMMENDED** - Reusable script for testing PostCall with any conversation file
  ```bash
  python3 test_postcall_with_file.py [conversation_file.json]
  ```

- **`test_postcall.sh`** - Bash wrapper with color output and .env support
  ```bash
  ./test_postcall.sh [conversation_file.json]
  ```

- **`test_postcall.py`** - Original PostCall test script (interactive)
- **`test_postcall_simple.py`** - Simplified PostCall test
- **`test_postcall_debug.py`** - PostCall test with debugging output
- **`test_postcall_simple_debug.py`** - Simple PostCall test with debug info
- **`test_post_call_comprehensive.py`** - Comprehensive PostCall validation
- **`test_post_call_simple.py`** - Simple PostCall endpoint test

### ClientData Endpoint Testing
- **`test_clientdata.py`** - ClientData endpoint test (interactive)
- **`test_clientdata_simple.py`** - Simplified ClientData test
- **`test_personalized_greetings.py`** - Test greeting generation logic

### Retrieve Endpoint Testing
- **`test_retrieve.py`** - Retrieve endpoint test (interactive)
- **`test_retrieve_simple.py`** - Simplified Retrieve test

### Authentication Testing
- **`test_hmac_auth.py`** - Test HMAC signature validation
- **`test_elevenlabs_hmac.py`** - ElevenLabs HMAC validation test

### Integration Testing
- **`test_production_ready.py`** ⭐ - Comprehensive 3-endpoint check (uses .env)
- **`final_test.py`** - Final integration test

### Utility Scripts
- **`test_memory_direct.py`** - Direct Mem0 API connectivity test
- **`verify_sheila_memories.py`** - Verify specific user's memories
- **`test_sheila_call.py`** - Test with Sheila's conversation data
- **`debug_elevenlabs.py`** - Debug ElevenLabs payload structure
- **`test_real_payload.py`** - Test with real ElevenLabs payload
- **`test_real_elevenlabs_payload.py`** - Another real payload test

### Shell Scripts
- **`test_fixed_handler.sh`** - Test fixed handler deployment
- **`test_postcall.sh`** - PostCall bash wrapper (executable)

---

## 📋 Usage Patterns

### Quick Testing (Recommended)
```bash
# Test PostCall with a conversation file
./test_postcall.sh ../test_data/conv_01jxd5y165f62a0v7gtr6bkg56.json

# Or with Python directly
python3 test_postcall_with_file.py ../test_data/conv_01jxk1wejhenk8x8tt9enzxw4a.json

# Test all endpoints
python3 test_production_ready.py
```

### Interactive Testing
```bash
# Tests that prompt for credentials
python3 test_clientdata.py
python3 test_retrieve.py
python3 test_postcall.py
```

### Using .env File
Create a `.env` file in the project root with:
```bash
ELEVENLABS_CLIENT_DATA_URL=https://...
ELEVENLABS_POST_CALL_URL=https://...
ELEVENLABS_WORKSPACE_KEY=wsec_...
ELEVENLABS_HMAC_KEY=wsec_...
MEM0_API_KEY=m0-...
MEM0_ORG_ID=org_...
MEM0_PROJECT_ID=proj_...
```

Then run scripts that support .env:
```bash
python3 test_production_ready.py
./test_postcall.sh ../test_data/conv_01jxd5y165f62a0v7gtr6bkg56.json
```

---

## 🎯 Scripts by Endpoint

### ClientData (`/client-data`)
- `test_clientdata.py` - Main test
- `test_clientdata_simple.py` - Simplified version
- `test_personalized_greetings.py` - Greeting generation

### Retrieve (`/retrieve`)
- `test_retrieve.py` - Main test
- `test_retrieve_simple.py` - Simplified version

### PostCall (`/post-call`)
- `test_postcall_with_file.py` ⭐ - **Best option**
- `test_postcall.sh` - Bash wrapper
- `test_postcall.py` - Interactive
- `test_postcall_simple.py` - Simplified
- `test_postcall_debug.py` - With debugging
- `test_post_call_comprehensive.py` - Full validation
- `test_real_payload.py` - Real payload testing

### All Endpoints
- `test_production_ready.py` ⭐ - Comprehensive check

---

## 📚 Documentation

For detailed usage instructions, see:
- **[../docs/USING_TEST_SCRIPT.md](../docs/USING_TEST_SCRIPT.md)** - Comprehensive guide
- **[../docs/TEST_SCRIPT_QUICK_GUIDE.md](../docs/TEST_SCRIPT_QUICK_GUIDE.md)** - Quick reference
- **[../docs/HOW_TO_USE_TEST_SCRIPT.md](../docs/HOW_TO_USE_TEST_SCRIPT.md)** - Technical details

---

## 🧪 Test Data

Test payload files are in `../test_data/`:
- `conv_01jxd5y165f62a0v7gtr6bkg56.json` - 161-message conversation
- `conv_01jxk1wejhenk8x8tt9enzxw4a.json` - 115-message conversation
- `elevenlabs_post_call_payload.json` - Sample ElevenLabs webhook payload
- `corrected_postcall_payload.json` - Corrected payload format

---

## ⚙️ Making Scripts Executable

If bash scripts aren't executable:
```bash
chmod +x test_postcall.sh test_fixed_handler.sh
```

---

## 🐛 Common Issues

**Timeout errors**: Normal for long conversations (Lambda processes async, client times out at 10s)

**Missing credentials**: Create `.env` file or export environment variables

**Import errors**: Run from project root, not from scripts directory

**HMAC validation fails**: Verify `ELEVENLABS_HMAC_KEY` matches ElevenLabs settings

---

## 📊 Test Results

Historical test results are in `../docs/`:
- `TEST_RESULTS.md`
- `POSTCALL_TEST_RESULTS.md`
- `TEST_SUMMARY_CONV_SHEILA.md`
