# ElevenLabs Integration - Quick Reference Card

## 🚀 Your AgenticMemory Endpoints

### 1️⃣ Client Data (Conversation Initiation)
```
URL: https://8nv3jj2gie.execute-api.us-east-1.amazonaws.com/Prod/client-data
Method: POST
Header: X-Workspace-Key: wsec_eb779969b7cb5cde6cdd9c6dfc4e2a08fa38cd6711b86eced6c101039871f6ac
```

**What it does:** Retrieves caller memory and generates personalized greeting

---

### 2️⃣ Memory Search Tool (Agent Tool)
```
URL: https://7h6j2vasna.execute-api.us-east-1.amazonaws.com/Prod/retrieve
Method: POST
Auth: None (trusted agent connection)
```

**Parameters:**
```json
{
  "query": "what to search for",
  "user_id": "{{caller_phone}}"
}
```

**What it does:** Searches caller's conversation history during call

---

### 3️⃣ Post-Call Webhook (Memory Storage)
```
URL: https://7iumhxcckh.execute-api.us-east-1.amazonaws.com/Prod/post-call
Method: POST
Auth: HMAC-SHA256 signature
Header: X-ElevenLabs-Signature
```

**What it does:** Automatically stores conversation after call ends

---

## 📋 ElevenLabs Configuration Steps

### In ElevenLabs Dashboard:

1. **Create Agent** → Set voice, language, and prompt

2. **Add Conversation Initiation Webhook:**
   - Webhook URL: [Client Data URL above]
   - Add header: `X-Workspace-Key` with value above
   - Sends: `{"caller_id": "+phone"}`

3. **Add Memory Search Tool:**
   - Tool name: `memory_search`
   - URL: [Retrieve URL above]
   - Parameters: `query` (string), `user_id` (string)
   - Map `user_id` to caller phone variable

4. **Add Post-Call Webhook:**
   - Webhook URL: [Post-Call URL above]
   - Enable HMAC signing (SHA-256)
   - Signing key: [from your AWS parameters]

---

## 🧪 Quick Test Commands

### Test Client Data:
```bash
curl -X POST https://8nv3jj2gie.execute-api.us-east-1.amazonaws.com/Prod/client-data \
  -H "X-Workspace-Key: wsec_eb779969b7cb5cde6cdd9c6dfc4e2a08fa38cd6711b86eced6c101039871f6ac" \
  -H "Content-Type: application/json" \
  -d '{"caller_id": "+16129782029"}'
```

### Test Retrieve:
```bash
curl -X POST https://7h6j2vasna.execute-api.us-east-1.amazonaws.com/Prod/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "pizza preferences", "user_id": "+16129782029"}'
```

### Run All Tests:
```bash
cd /home/ubuntu/proj/claude/AgenticMemory
source test_env/bin/activate
python test_production_ready.py
```

---

## 🔍 Monitoring

### CloudWatch Log Groups:
```
/aws/lambda/sam-app-ClientDataFunction-*
/aws/lambda/sam-app-RetrieveFunction-*
/aws/lambda/sam-app-PostCallFunction-*
```

### Tail Logs:
```bash
aws logs tail /aws/lambda/sam-app-ClientDataFunction-* --follow
```

---

## ✅ Expected Behavior

### First Call (New Caller):
- Generic greeting
- No prior memory
- Conversation saved after call

### Second Call (Returning Caller):
- Personalized greeting with name
- Agent remembers preferences
- Memory search tool available
- Updated memory saved

---

## 🐛 Common Issues

**No personalized greeting?**
- Wait 30-60 seconds after first call
- Check CloudWatch logs
- Verify name was mentioned in conversation

**Memory search not working?**
- Check tool parameter mapping
- Verify `user_id` has caller phone
- Test retrieve endpoint directly

**401 Unauthorized?**
- Check `X-Workspace-Key` header
- Verify exact key match (no spaces)

---

## 📞 Support

Run diagnostics:
```bash
python test_production_ready.py
python test_memory_direct.py
```

Check logs:
```bash
aws logs tail /aws/lambda/sam-app-* --follow
```

---

**Quick Start:** Follow `ELEVENLABS_SETUP_GUIDE.md` for detailed instructions!
