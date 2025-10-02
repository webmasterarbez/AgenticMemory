# Quick Guide: test_postcall_with_file.py

## TL;DR - How to Use

### 1. Default File
```bash
python3 test_postcall_with_file.py
```
Tests with `conv_01jxd5y165f62a0v7gtr6bkg56.json`

### 2. Specific File
```bash
python3 test_postcall_with_file.py YOUR_FILE.json
```
Tests with any conversation file you specify

### 3. With Credentials (No Prompts)
```bash
ELEVENLABS_POST_CALL_URL="https://YOUR_URL/Prod/post-call" \
ELEVENLABS_HMAC_KEY="wsec_YOUR_KEY" \
python3 test_postcall_with_file.py YOUR_FILE.json
```

## Real Examples

### Test Sheila's First Conversation (161 messages)
```bash
python3 test_postcall_with_file.py conv_01jxd5y165f62a0v7gtr6bkg56.json
```

### Test Sheila's Second Conversation (115 messages) 
```bash
python3 test_postcall_with_file.py conv_01jxk1wejhenk8x8tt9enzxw4a.json
```

### Test Stefan's Conversation
```bash
python3 test_postcall_with_file.py conv_stefan.json
```

## What to Look For

### Success ✅
```
📊 Response Status: 200
✅ Response Body:
{
  "status": "ok"
}
```

### Then Check Logs
```bash
aws logs tail /aws/lambda/AgenticMemoriesPostCall --since 5m --follow
```

Look for:
- ✅ `Extracted caller_id from metadata.phone_call.external_number: +1...`
- ✅ `Stored factual memory for +1...`
- ✅ `Stored semantic memory for +1... (X messages)`

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| File not found | Wrong filename or path | Check filename, use `ls *.json` |
| Timeout error | Normal for async processing | Check CloudWatch logs |
| 401 Unauthorized | Wrong HMAC key | Verify key matches Lambda config |
| Invalid JSON | Corrupted file | Check file with `jq . file.json` |

## Need Credentials?

### PostCall URL
```bash
aws cloudformation describe-stacks --stack-name sam-app \
  --query 'Stacks[0].Outputs[?OutputKey==`PostCallApiUrl`].OutputValue' \
  --output text
```

### HMAC Key  
```bash
aws lambda get-function-configuration \
  --function-name AgenticMemoriesPostCall \
  --query 'Environment.Variables.ELEVENLABS_HMAC_KEY' \
  --output text
```

## Full Documentation
See `HOW_TO_USE_TEST_SCRIPT.md` for complete details, troubleshooting, and advanced usage.
