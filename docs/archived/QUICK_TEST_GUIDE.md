# Quick Test Guide

## Running Tests (No Manual Input Required!)

All tests now run automatically using `.env` configuration.

### Activate Virtual Environment

```bash
cd /home/ubuntu/home/ubuntu/proj/claude/AgenticMemory
source test_env/bin/activate
```

### Run Individual Tests

```bash
# Test ClientData endpoint (pre-call memory + greeting)
python scripts/test_clientdata.py

# Test Retrieve endpoint (in-call semantic search)
python scripts/test_retrieve.py

# Test PostCall endpoint (post-call memory storage)
python scripts/test_postcall.py

# Test personalized greetings
python scripts/test_personalized_greetings.py

# Test HMAC authentication
python scripts/test_hmac_auth.py
python scripts/test_elevenlabs_hmac.py
```

### Run Comprehensive Test

```bash
# Tests all three endpoints
python scripts/test_production_ready.py
```

## Expected Output

### ✅ Success
```
=== Testing ClientData Endpoint ===
URL: https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data
Status Code: 200
✅ SUCCESS: Authentication passed!
```

### ❌ Error (Missing Config)
```
❌ ERROR: ELEVENLABS_CLIENT_DATA_URL not found in .env file
```

### ❌ Error (Invalid URL)
```
❌ ERROR: Invalid CLIENTDATA_URL format: http://example.com
   URL must start with 'https://'
```

### ❌ Error (Invalid Key)
```
❌ ERROR: Invalid WORKSPACE_KEY format: invalid_key
   Key must start with 'wsec_'
```

## Quick Validation

Verify `.env` is configured correctly:

```bash
# Show configured URLs (truncated for security)
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('ClientData:', os.getenv('ELEVENLABS_CLIENT_DATA_URL')[:50] + '...')
print('Retrieve:', os.getenv('ELEVENLABS_RETRIEVE_URL')[:50] + '...')
print('PostCall:', os.getenv('ELEVENLABS_POST_CALL_URL')[:50] + '...')
print('Workspace Key:', os.getenv('ELEVENLABS_WORKSPACE_KEY')[:20] + '...')
"
```

## Troubleshooting

### "python-dotenv not installed"
```bash
pip install python-dotenv
```

### ".env file not found"
```bash
# Check if .env exists
ls -la .env

# Check you're in the right directory
pwd
# Should be: /home/ubuntu/home/ubuntu/proj/claude/AgenticMemory
```

### "Invalid URL format"
Check `.env` file:
```bash
cat .env | grep ELEVENLABS
```

Ensure URLs start with `https://` and keys start with `wsec_`

## Test Without Virtual Environment

```bash
# Use virtual environment Python directly
test_env/bin/python scripts/test_clientdata.py
test_env/bin/python scripts/test_production_ready.py
```

## CI/CD Usage

Tests can now run in automated pipelines:

```bash
#!/bin/bash
# Ensure .env exists with proper values
if [ ! -f .env ]; then
    echo "ERROR: .env file not found"
    exit 1
fi

# Run tests
python scripts/test_production_ready.py
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Tests failed with exit code $exit_code"
    exit $exit_code
fi
```

## Current Endpoints (from latest deployment)

```
ClientData: https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data
Retrieve:   https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve
PostCall:   https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call
```

## Test Data

Default test uses:
- **Caller ID**: `+16129782029` (has existing memories)
- **New Caller**: `+19995551234` (no memories)

## What Each Test Does

| Test | Purpose | Validates |
|------|---------|-----------|
| `test_clientdata.py` | Pre-call memory loading | Auth, memory retrieval, greeting |
| `test_retrieve.py` | In-call search | Semantic search, relevance |
| `test_postcall.py` | Post-call storage | HMAC auth, memory storage |
| `test_personalized_greetings.py` | Greeting generation | Name extraction, personalization |
| `test_production_ready.py` | Full system | All endpoints, all features |

## Success Criteria

All tests should show:
- ✅ Status 200 for valid requests
- ✅ Status 401 for invalid auth
- ✅ Status 400 for missing required fields
- ✅ Proper JSON responses
- ✅ Memory count displayed
- ✅ Personalized greetings generated
