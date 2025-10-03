# Test Scripts Updated - .env Configuration

## Overview

All test scripts have been updated to automatically load configuration from the `.env` file, eliminating the need for manual input of credentials and URLs. The scripts now include validation to ensure all required values are present and properly formatted before running tests.

## Changes Made

### 1. Automatic Configuration Loading

All test scripts now:
- ✅ Load variables from `.env` file using `python-dotenv`
- ✅ Validate that required variables exist
- ✅ Validate URL formats (must start with `https://`)
- ✅ Validate key formats (must start with `wsec_`)
- ✅ Exit with clear error messages if validation fails

### 2. Updated Test Scripts

| Script | Variables Loaded | Status |
|--------|-----------------|--------|
| `test_clientdata.py` | `ELEVENLABS_CLIENT_DATA_URL`, `ELEVENLABS_WORKSPACE_KEY` | ✅ Updated |
| `test_postcall.py` | `ELEVENLABS_POST_CALL_URL`, `ELEVENLABS_HMAC_KEY` | ✅ Updated |
| `test_personalized_greetings.py` | `ELEVENLABS_CLIENT_DATA_URL`, `ELEVENLABS_WORKSPACE_KEY` | ✅ Updated |
| `test_retrieve.py` | `ELEVENLABS_RETRIEVE_URL` | ✅ Updated |
| `test_hmac_auth.py` | `ELEVENLABS_POST_CALL_URL`, `ELEVENLABS_HMAC_KEY` | ✅ Updated |
| `test_elevenlabs_hmac.py` | `ELEVENLABS_POST_CALL_URL`, `ELEVENLABS_HMAC_KEY` | ✅ Updated |
| `test_post_call_simple.py` | `ELEVENLABS_POST_CALL_URL` | ✅ Updated |
| `test_post_call_comprehensive.py` | `ELEVENLABS_POST_CALL_URL`, `ELEVENLABS_HMAC_KEY` | ✅ Updated |
| `test_real_payload.py` | `ELEVENLABS_POST_CALL_URL`, `ELEVENLABS_HMAC_KEY` | ✅ Updated |
| `test_production_ready.py` | All three URLs + keys | ✅ Already configured |
| `test_memory_direct.py` | Mem0 credentials | ✅ Already configured |

## Validation Rules

### URL Validation
- Must exist in `.env` file
- Must start with `https://`
- Example: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`

### Key Validation
- Must exist in `.env` file
- Must start with `wsec_`
- Example: `wsec_955d3f63879a0daf23483809cbc8b135eb851bcecfab6eb6767bc23d11b762ed`

## Error Messages

Scripts will exit immediately with clear error messages if validation fails:

### Missing Variable
```
❌ ERROR: ELEVENLABS_CLIENT_DATA_URL not found in .env file
```

### Invalid URL Format
```
❌ ERROR: Invalid CLIENTDATA_URL format: http://example.com
   URL must start with 'https://'
```

### Invalid Key Format
```
❌ ERROR: Invalid WORKSPACE_KEY format: invalid_key
   Key must start with 'wsec_'
```

### Missing dotenv Package
```
⚠️  Warning: python-dotenv not installed. Install with: pip install python-dotenv
```

## Required .env Variables

Your `.env` file must contain:

```bash
# API Endpoints
ELEVENLABS_CLIENT_DATA_URL=https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data
ELEVENLABS_RETRIEVE_URL=https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve
ELEVENLABS_POST_CALL_URL=https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call

# Authentication Keys
ELEVENLABS_WORKSPACE_KEY=wsec_955d3f63879a0daf23483809cbc8b135eb851bcecfab6eb6767bc23d11b762ed
ELEVENLABS_HMAC_KEY=wsec_955d3f63879a0daf23483809cbc8b135eb851bcecfab6eb6767bc23d11b762ed

# Mem0 Credentials (for test_memory_direct.py)
MEM0_API_KEY=m0-...
MEM0_ORG_ID=org_...
MEM0_PROJECT_ID=proj_...

# S3 Storage
S3_BUCKET_NAME=elevenlabs-agentic-memory-424875385161-us-east-1
```

## Usage

### Before (Manual Input Required)
```bash
$ python3 scripts/test_clientdata.py
Enter your ElevenLabs Workspace Key: wsec_...
```

### After (Automatic from .env)
```bash
$ python3 scripts/test_clientdata.py
=== Testing ClientData Endpoint ===
URL: https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data
...
```

## Running Tests

All tests now run without any manual input:

```bash
# Activate virtual environment (recommended)
source test_env/bin/activate

# Run individual tests
python scripts/test_clientdata.py
python scripts/test_postcall.py
python scripts/test_retrieve.py
python scripts/test_personalized_greetings.py

# Or use virtual environment directly
test_env/bin/python scripts/test_clientdata.py
```

### Comprehensive Test
```bash
python scripts/test_production_ready.py
```

This will test all three endpoints automatically using `.env` configuration.

## Benefits

✅ **No Manual Input**: Tests run completely automated  
✅ **Consistent Configuration**: All tests use same URLs and keys  
✅ **Early Validation**: Catches configuration errors before making API calls  
✅ **Clear Error Messages**: Easy to identify and fix configuration issues  
✅ **CI/CD Ready**: Can run in automated pipelines without interaction  
✅ **Secure**: Credentials stored in `.env` (gitignored), not in code  

## Troubleshooting

### dotenv Module Not Found

Install the required package:

```bash
# Using virtual environment
test_env/bin/pip install python-dotenv

# Or system-wide (if allowed)
pip3 install --user python-dotenv
```

### Invalid URL or Key Format

Check your `.env` file:

```bash
cat .env | grep ELEVENLABS
```

Ensure:
- URLs start with `https://`
- Keys start with `wsec_`
- No extra quotes or spaces

### .env File Not Found

The scripts look for `.env` in the project root. Ensure you're running from the correct directory:

```bash
cd /home/ubuntu/home/ubuntu/proj/claude/AgenticMemory
```

Or that `.env` exists:

```bash
ls -la .env
```

## Testing the Updates

Verify all scripts load configuration correctly:

```bash
# Quick validation test
test_env/bin/python -c "
from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path('.env')
load_dotenv(env_path)

print('✅ ClientData URL:', os.getenv('ELEVENLABS_CLIENT_DATA_URL')[:40] + '...')
print('✅ Retrieve URL:', os.getenv('ELEVENLABS_RETRIEVE_URL')[:40] + '...')
print('✅ PostCall URL:', os.getenv('ELEVENLABS_POST_CALL_URL')[:40] + '...')
print('✅ Workspace Key:', os.getenv('ELEVENLABS_WORKSPACE_KEY')[:20] + '...')
print('✅ HMAC Key:', os.getenv('ELEVENLABS_HMAC_KEY')[:20] + '...')
"
```

## Implementation Details

### Common Pattern

All scripts now follow this pattern:

```python
#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    print("⚠️  Warning: python-dotenv not installed")
    sys.exit(1)

# Load and validate
URL = os.getenv('ELEVENLABS_XXX_URL')
KEY = os.getenv('ELEVENLABS_XXX_KEY')

if not URL:
    print("❌ ERROR: Variable not found in .env")
    sys.exit(1)

if not URL.startswith('https://'):
    print(f"❌ ERROR: Invalid URL format")
    sys.exit(1)

if not KEY.startswith('wsec_'):
    print(f"❌ ERROR: Invalid key format")
    sys.exit(1)

# Continue with test...
```

## Backwards Compatibility

The scripts no longer support manual input. To use different credentials temporarily:

1. **Option A**: Modify `.env` file
2. **Option B**: Use environment variables:
   ```bash
   ELEVENLABS_CLIENT_DATA_URL=https://other-url.com \
   ELEVENLABS_WORKSPACE_KEY=wsec_other_key \
   python scripts/test_clientdata.py
   ```

## Summary

All test scripts have been modernized to:
- Load configuration automatically from `.env`
- Validate all inputs before making API calls
- Provide clear error messages for misconfigurations
- Run without any manual interaction

This makes testing faster, more reliable, and CI/CD-ready! 🚀
