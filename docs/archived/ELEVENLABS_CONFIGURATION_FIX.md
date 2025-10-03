# ElevenLabs Agent Configuration - Step by Step

## Problem Diagnosis
Your AgenticMemory backend is working perfectly, but ElevenLabs is not configured correctly. The CloudWatch logs show:
- "Invalid workspace key" - ElevenLabs not sending correct authentication
- "Missing caller_id" - ElevenLabs not sending caller phone number

## Required Configuration

### 1. Conversation Initiation Webhook
In your ElevenLabs Agent settings:

**URL:** `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`

**Method:** `POST`

**Headers:**
```
X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70
Content-Type: application/json
```

**Payload Template:**
```json
{
  "caller_id": "{{system__caller_id}}"
}
```

### 2. Agent Tool Configuration (for memory search)
**URL:** `https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve`

**Method:** `POST`

**Tool Name:** `search_memory`

**Description:** `Search previous conversations and memories for this caller`

**Parameters:**
```json
{
  "query": {
    "type": "string",
    "description": "What to search for in previous conversations"
  },
  "user_id": {
    "type": "string", 
    "default": "{{system__caller_id}}"
  }
}
```

### 3. Post-Call Webhook (for storing memories)
**URL:** `https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call`

**Method:** `POST`

**Authentication:** HMAC signature (automatically handled by ElevenLabs)

**HMAC Secret:** `wsec_a8dc8b6e25ec3ddf11d7e651c40a5cb4931c2ca39d161fa4c94139f12f3ba9d3`

## Testing Your Configuration

### Test 1: Manual Webhook Test
```bash
curl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \
  -H 'X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70' \
  -H 'Content-Type: application/json' \
  -d '{"caller_id": "+16129782029"}' \
  -v
```

Expected response: 200 OK with personalized data for Stefan

### Test 2: Check CloudWatch Logs
After making a test call, check logs for errors:
```bash
aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow
```

Should see successful requests, not "Invalid workspace key" or "Missing caller_id" errors.

## Common Configuration Mistakes

### ❌ Wrong Header Name
- `x-workspace-key` (lowercase)
- `X-WORKSPACE-KEY` (all caps)
- `workspace-key` (missing X-)

### ✅ Correct Header Name
- `X-Workspace-Key` (exactly this case)

### ❌ Wrong Payload Format
- `{"phone": "+16129782029"}`
- `{"user_id": "+16129782029"}`
- `{"system_caller_id": "+16129782029"}`

### ✅ Correct Payload Format
- `{"caller_id": "{{system__caller_id}}"}`
- `{"system__caller_id": "{{system__caller_id}}"}`

### ❌ Wrong Variable Syntax
- `{system__caller_id}` (single braces)
- `{{caller_id}}` (wrong variable name)

### ✅ Correct Variable Syntax
- `{{system__caller_id}}` (double braces, correct ElevenLabs system variable)

## System Prompt Configuration

Use the corrected system prompt from `CORRECTED_MEMOIR_SYSTEM_PROMPT.md` with proper `{{variable_name}}` syntax.

## Expected Workflow

1. **Call starts** → ElevenLabs calls conversation initiation webhook
2. **AgenticMemory returns** → Personalized context + dynamic variables
3. **Agent uses context** → References past conversations naturally
4. **During call** → Agent can call search_memory tool for specific details
5. **Call ends** → ElevenLabs calls post-call webhook
6. **AgenticMemory stores** → New memories for future personalization

## Verification Checklist

- [ ] Conversation initiation webhook URL is correct
- [ ] X-Workspace-Key header is exactly `wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70`
- [ ] Payload includes `caller_id` with `{{system__caller_id}}` variable
- [ ] System prompt uses `{{variable_name}}` syntax (double braces)
- [ ] Agent tool configured for search_memory
- [ ] Post-call webhook configured with HMAC secret
- [ ] Test call shows personalized greeting for Stefan (+16129782029)

## Support

If issues persist:
1. Check CloudWatch logs for specific error messages
2. Test webhook manually with curl command above
3. Verify ElevenLabs sends correct payload format
4. Ensure all headers are configured exactly as specified