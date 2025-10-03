# ⚠️ CRITICAL AUTHENTICATION REFERENCE

## DO NOT CHANGE THESE AUTHENTICATION METHODS

### ClientData Authentication
**Method**: ElevenLabs Secrets Manager (NOT direct headers)

**Configuration**:
1. Go to [ElevenLabs Settings](https://elevenlabs.io/app/agents/settings)
2. Add secret: `WORKSPACE_KEY` = `wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70`
3. Map to header: `X-Workspace-Key` → `WORKSPACE_KEY` secret
4. Enable in agent Security tab: "Fetch conversation initiation data"

**Why**: ElevenLabs requires authentication headers to be managed through their secure secrets interface, not as direct header configuration.

### PostCall Authentication
**Method**: HMAC-SHA256 Signature

**Reference**: https://elevenlabs.io/docs/agents-platform/workflows/post-call-webhooks#authentication

**Configuration**:
- HMAC Key: `wsec_a8dc8b6e25ec3ddf11d7e651c40a5cb4931c2ca39d161fa4c94139f12f3ba9d3`
- Header: `ElevenLabs-Signature` (format: `t=timestamp,v0=signature`)
- Tolerance: 30 minutes
- Always return 200 OK (async processing)

**Why**: ElevenLabs uses HMAC signatures to verify webhook authenticity and prevent replay attacks.

### Retrieve Authentication  
**Method**: None (trusted connection)

**Configuration**: No authentication required

**Why**: Direct communication between ElevenLabs agent and backend during active calls is considered trusted.

---

## Quick Reference

### Test Authentication
```bash
# ClientData (should return 200 with memory data)
curl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \
  -H 'X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70' \
  -H 'Content-Type: application/json' \
  -d '{"caller_id": "+16129782029"}' -v

# Test wrong key (should return 401)
curl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \
  -H 'X-Workspace-Key: wrong_key' \
  -H 'Content-Type: application/json' \
  -d '{"caller_id": "+16129782029"}' -s -w "Status: %{http_code}\n"
```

### Debug Logs
```bash
aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow
```

**Look for**:
- ✅ "Retrieving memories for user_id: +16129782029"
- ❌ "Invalid workspace key" (means ElevenLabs config wrong)
- ❌ "Missing caller_id" (means payload format wrong)

---

*Reference: MASTER_DOCUMENTATION.md for complete details*