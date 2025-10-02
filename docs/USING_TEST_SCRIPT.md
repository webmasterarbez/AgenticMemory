# 🚀 Using test_postcall_with_file.py - Complete Guide

## Three Ways to Use It

### 1️⃣ Simple - Python Script (Recommended)
```bash
# Test with default file
python3 test_postcall_with_file.py

# Test with specific file  
python3 test_postcall_with_file.py conv_01jxk1wejhenk8x8tt9enzxw4a.json

# With credentials (no prompts)
ELEVENLABS_POST_CALL_URL="https://..." ELEVENLABS_HMAC_KEY="wsec_..." \
python3 test_postcall_with_file.py YOUR_FILE.json
```

### 2️⃣ Easier - Bash Wrapper
```bash
# Test with default file
./test_postcall.sh

# Test with specific file
./test_postcall.sh conv_01jxk1wejhenk8x8tt9enzxw4a.json
```
**Bonus**: The bash script automatically loads credentials from `.env` file!

### 3️⃣ Best - Using .env File
```bash
# 1. Create .env file (one time)
cat > .env << 'EOF'
ELEVENLABS_POST_CALL_URL=https://7iumhxcckh.execute-api.us-east-1.amazonaws.com/Prod/post-call
ELEVENLABS_HMAC_KEY=wsec_eb779969b7cb5cde6cdd9c6dfc4e2a08fa38cd6711b86eced6c101039871f6ac
EOF

# 2. Test any file (no prompts!)
./test_postcall.sh conv_01jxk1wejhenk8x8tt9enzxw4a.json
```

## What You'll See

### During Test
```
📂 Reading conversation file: conv_01jxk1wejhenk8x8tt9enzxw4a.json

📋 Payload Summary:
   Conversation ID: conv_01jxk1wejhenk8x8tt9enzxw4a
   Agent ID: agent_01jxbrc1trfxev5sdp5xk4ra67
   Status: done
   Caller ID: +16129782029
   Transcript messages: 115
   Summary: Sheila recounts her travel adventures...

🔐 Generating HMAC signature...
   Timestamp: 1759362261
   Signature (v0): 2e7461237de3dbbe...

🚀 Sending POST request to https://...
================================================================================

📊 Response Status: 200
✅ Response Body:
{
  "status": "ok"
}

✅ SUCCESS: PostCall endpoint accepted the payload

💡 Next steps:
   1. Check CloudWatch logs for processing details:
      aws logs tail /aws/lambda/AgenticMemoriesPostCall --since 5m --follow
   2. Verify memories stored for caller: +16129782029
   3. Test Retrieve endpoint to confirm memories are searchable
```

### In CloudWatch Logs
```bash
# Run this in another terminal to watch processing
aws logs tail /aws/lambda/AgenticMemoriesPostCall --since 5m --follow
```

You should see:
```
[INFO] Extracted caller_id from metadata.phone_call.external_number: +16129782029
[INFO] Processing post-call data for user_id: +16129782029
[INFO] Stored factual memory for +16129782029
[INFO] Stored semantic memory for +16129782029 (115 messages)
```

## Files You Have

| File | Purpose | Usage |
|------|---------|-------|
| `test_postcall_with_file.py` | Main test script | `python3 test_postcall_with_file.py [file.json]` |
| `test_postcall.sh` | Bash wrapper with colors | `./test_postcall.sh [file.json]` |
| `HOW_TO_USE_TEST_SCRIPT.md` | Full documentation | Read for details |
| `TEST_SCRIPT_QUICK_GUIDE.md` | Quick reference | Cheat sheet |

## Your Conversation Files

```bash
# List available files
ls -lh conv_*.json

# You have:
# - conv_01jxd5y165f62a0v7gtr6bkg56.json (Sheila, 161 messages)
# - conv_01jxk1wejhenk8x8tt9enzxw4a.json (Sheila/Stefan, 115 messages)
```

## Testing Both Files

```bash
# Test Sheila's first conversation (161 messages - will timeout)
./test_postcall.sh conv_01jxd5y165f62a0v7gtr6bkg56.json

# Test second conversation (115 messages - should complete)
./test_postcall.sh conv_01jxk1wejhenk8x8tt9enzxw4a.json
```

## Understanding Results

### ✅ Success Indicators
1. **HTTP 200 response** - Webhook accepted
2. **Logs show "Stored factual memory"** - Summary saved
3. **Logs show "Stored semantic memory"** - Transcript saved
4. **No timeout in logs** - Processing completed

### ⚠️ Partial Success
1. **HTTP 200 response** - Webhook accepted
2. **Logs show "Stored factual memory"** - Summary saved ✅
3. **Logs show timeout** - Transcript not saved ❌
4. **Reason**: Conversation too long for 120s timeout

### ❌ Failure Indicators
1. **HTTP 401/403** - HMAC validation failed
2. **Logs show "Missing caller_id"** - Payload format issue
3. **Logs show "Error storing"** - Mem0 API issue

## Pro Tips

### Test Multiple Files
```bash
# Test all conversation files
for file in conv_*.json; do
    echo "====== Testing $file ======"
    ./test_postcall.sh "$file"
    echo ""
    sleep 5  # Wait between tests
done
```

### Monitor in Real-Time
```bash
# Terminal 1: Watch logs
aws logs tail /aws/lambda/AgenticMemoriesPostCall --since 1m --follow

# Terminal 2: Run tests
./test_postcall.sh conv_01jxk1wejhenk8x8tt9enzxw4a.json
```

### Save Results
```bash
# Save output to file
./test_postcall.sh conv_01jxk1wejhenk8x8tt9enzxw4a.json 2>&1 | tee test_results.log
```

### Check File Before Testing
```bash
# Quick peek at conversation details
jq '{
  conversation_id, 
  agent_id, 
  caller: .metadata.phone_call.external_number,
  messages: (.transcript | length)
}' conv_01jxk1wejhenk8x8tt9enzxw4a.json
```

## Troubleshooting

### "File not found"
```bash
# Check current directory
ls conv_*.json

# Use full path if needed
python3 test_postcall_with_file.py /full/path/to/conv_file.json
```

### "Invalid JSON"
```bash
# Validate JSON
jq . conv_01jxk1wejhenk8x8tt9enzxw4a.json

# If broken, you'll see the error location
```

### "Timeout error" (Normal!)
This is expected. The Lambda returns 200 immediately and processes async.
The client timeout (10s) doesn't affect Lambda processing.

**Check logs to verify actual processing:**
```bash
aws logs tail /aws/lambda/AgenticMemoriesPostCall --since 5m
```

### "Invalid HMAC signature"
```bash
# Get correct key from Lambda
aws lambda get-function-configuration \
  --function-name AgenticMemoriesPostCall \
  --query 'Environment.Variables.ELEVENLABS_HMAC_KEY' \
  --output text

# Update your .env or environment variable
```

## Next Steps After Testing

### 1. Verify Memories Stored
```bash
# Query for specific caller
# (Use caller_id from test output)
python3 verify_sheila_memories.py
```

### 2. Test Retrieve Endpoint
```bash
curl -X POST https://7h6j2vasna.execute-api.us-east-1.amazonaws.com/Prod/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "what do you know?", "user_id": "+16129782029"}'
```

### 3. Test ClientData Endpoint
```bash
curl -X POST https://CLIENT_DATA_URL/Prod/client-data \
  -H "X-Workspace-Key: wsec_..." \
  -H "Content-Type: application/json" \
  -d '{"caller_id": "+16129782029"}'
```

## Summary

**Easiest way to use:**
```bash
# One-time setup
cat > .env << EOF
ELEVENLABS_POST_CALL_URL=https://YOUR_URL/Prod/post-call
ELEVENLABS_HMAC_KEY=wsec_YOUR_KEY
EOF

# Then just run
./test_postcall.sh YOUR_FILE.json
```

**That's it!** 🎉

---

**Questions?** Check `HOW_TO_USE_TEST_SCRIPT.md` for full details.
