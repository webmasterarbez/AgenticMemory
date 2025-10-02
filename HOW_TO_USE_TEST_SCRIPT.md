# How to Use test_postcall_with_file.py

## Quick Start

### Basic Usage
```bash
# Test with the default file (conv_01jxd5y165f62a0v7gtr6bkg56.json)
python3 test_postcall_with_file.py
```

### With Environment Variables (Recommended)
```bash
# Set credentials as environment variables
export ELEVENLABS_POST_CALL_URL="https://7iumhxcckh.execute-api.us-east-1.amazonaws.com/Prod/post-call"
export ELEVENLABS_HMAC_KEY="wsec_eb779969b7cb5cde6cdd9c6dfc4e2a08fa38cd6711b86eced6c101039871f6ac"

# Run test
python3 test_postcall_with_file.py
```

### With Inline Environment Variables
```bash
# One-liner (credentials only used for this command)
ELEVENLABS_POST_CALL_URL="https://7iumhxcckh.execute-api.us-east-1.amazonaws.com/Prod/post-call" \
ELEVENLABS_HMAC_KEY="wsec_eb779969b7cb5cde6cdd9c6dfc4e2a08fa38cd6711b86eced6c101039871f6ac" \
python3 test_postcall_with_file.py
```

### Interactive Mode
```bash
# Run without env vars - will prompt for credentials
python3 test_postcall_with_file.py

# You'll be prompted:
# Enter ELEVENLABS_POST_CALL_URL: [paste URL]
# Enter ELEVENLABS_HMAC_KEY: [paste key]
```

## Getting Your Credentials

### 1. PostCall URL
Get from SAM deployment outputs:
```bash
aws cloudformation describe-stacks \
  --stack-name sam-app \
  --query 'Stacks[0].Outputs[?OutputKey==`PostCallApiUrl`].OutputValue' \
  --output text
```

Or from `samconfig.toml` after deployment.

### 2. HMAC Key
Get from Lambda environment variables:
```bash
aws lambda get-function-configuration \
  --function-name AgenticMemoriesPostCall \
  --query 'Environment.Variables.ELEVENLABS_HMAC_KEY' \
  --output text
```

Or from your ElevenLabs dashboard → Agent Settings → Webhooks → Signing Secret.

## Understanding the Output

### Successful Test
```
📂 Reading conversation file...

📋 Payload Summary:
   Conversation ID: conv_01jxd5y165f62a0v7gtr6bkg56
   Agent ID: agent_01jxbrc1trfxev5sdp5xk4ra67
   Status: done
   Caller ID: +15074595005
   Transcript messages: 161
   Summary: Sheila Cunningham shares memories...
   Evaluation criteria: 5 items

🔐 Generating HMAC signature...
   Timestamp: 1759357173
   Signature (v0): 5010f94c60b39d9f...

🚀 Sending POST request to https://...
================================================================================

📊 Response Status: 200

✅ Response Body:
{
  "status": "ok"
}

✅ SUCCESS: PostCall endpoint accepted the payload
```

### What This Means
- ✅ **Status 200**: Webhook accepted (async processing started)
- The Lambda is now processing the payload in the background
- Memories will be stored (check logs for confirmation)

### Common Errors

#### 1. Invalid HMAC Signature
```
❌ HTTP ERROR: 401 - Unauthorized
```
**Fix**: Check that your `ELEVENLABS_HMAC_KEY` matches Lambda configuration.

#### 2. Timeout Error
```
❌ UNEXPECTED ERROR: The read operation timed out
```
**Fix**: This is normal! The Lambda returns 200 immediately but processes async. The client timeout doesn't affect processing.

#### 3. File Not Found
```
FileNotFoundError: [Errno 2] No such file or directory: 'conv_01jxd5y165f62a0v7gtr6bkg56.json'
```
**Fix**: Make sure you're in the correct directory or update the filename in the script.

## Verifying Success

### 1. Check CloudWatch Logs
```bash
# Watch logs in real-time
aws logs tail /aws/lambda/AgenticMemoriesPostCall --since 5m --follow

# Look for these messages:
# ✅ "Extracted caller_id from metadata.phone_call.external_number: +1..."
# ✅ "Processing post-call data for user_id: +1..."
# ✅ "Stored factual memory for +1..."
# ✅ "Stored semantic memory for +1... (X messages)"
```

### 2. Query Mem0 Memories
```bash
# Use the Retrieve endpoint
curl -X POST https://7h6j2vasna.execute-api.us-east-1.amazonaws.com/Prod/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "what do you know about this user?", "user_id": "+15074595005"}'
```

### 3. Check Mem0 Dashboard
Visit: https://app.mem0.ai/memories

Filter by user_id to see stored memories.

## Testing Different Conversation Files

### Option 1: Edit the Script
Change line 26 to use a different file:
```python
with open("YOUR_CONVERSATION_FILE.json", "r") as f:
```

### Option 2: Use Command-Line Argument
I can modify the script to accept a filename as an argument. Would you like me to do that?

## Expected Processing Times

| Conversation Length | Processing Time | Timeout Risk |
|---------------------|-----------------|--------------|
| 10-30 messages      | 10-20 seconds   | ❌ None      |
| 31-60 messages      | 20-40 seconds   | ❌ None      |
| 61-100 messages     | 40-70 seconds   | ⚠️ Low       |
| 101-150 messages    | 70-110 seconds  | ⚠️ Medium    |
| 151-200 messages    | 110-180 seconds | ⚠️ High      |
| 200+ messages       | 180+ seconds    | ❌ Very High |

**Current Lambda timeout**: 120 seconds  
**Recommended timeout**: 300 seconds (for long conversations)

## Troubleshooting

### Script Hangs at "Sending POST request"
- Normal if Lambda is processing (especially for large payloads)
- Client times out after 10 seconds, but Lambda continues processing
- Check CloudWatch logs to verify processing

### 200 Response but No Memories Stored
Check logs for:
1. **HMAC validation failure**: Wrong key or timestamp too old
2. **Caller ID extraction failure**: Payload format issue
3. **Mem0 API errors**: API key or project ID issues
4. **Lambda timeout**: Conversation too long for current timeout

### Want to Test Without HMAC Validation?
You can temporarily disable HMAC check in `src/post_call/handler.py` for testing:
```python
# Comment out this line:
# if not verify_hmac_signature(raw_body, signature_header):
#     logger.error("Invalid HMAC signature")
#     return response
```

**⚠️ Warning**: Remember to re-enable for production!

## Advanced Usage

### Save Output to File
```bash
python3 test_postcall_with_file.py > test_results.log 2>&1
```

### Test Multiple Files in Batch
```bash
for file in conv_*.json; do
    echo "Testing $file..."
    # Modify script to accept $file as argument
    python3 test_postcall_with_file.py "$file"
    sleep 5  # Wait between tests
done
```

### Monitor in Real-Time
```bash
# Terminal 1: Watch logs
aws logs tail /aws/lambda/AgenticMemoriesPostCall --since 1m --follow

# Terminal 2: Run test
python3 test_postcall_with_file.py
```

## Next Steps

After successful test:
1. ✅ Verify memories in Mem0 dashboard
2. ✅ Test Retrieve endpoint with queries
3. ✅ Test ClientData endpoint for greeting generation
4. ✅ Run full integration test with real ElevenLabs call

## Need Help?

Common questions:
- **Q**: How do I test with a different conversation file?  
  **A**: Edit line 26 or let me modify the script to accept arguments

- **Q**: What if I don't have the HMAC key?  
  **A**: Get it from ElevenLabs dashboard or Lambda config

- **Q**: Can I test without making network requests?  
  **A**: Yes, use `sam local invoke` with test events

- **Q**: How do I know if it really worked?  
  **A**: Check CloudWatch logs and query Mem0 for stored memories
