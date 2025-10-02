# ElevenLabs Agent Setup Guide
## AgenticMemory Integration

This guide walks you through setting up your ElevenLabs conversational AI agent with personalized memory capabilities powered by AgenticMemory.

---

## 🎯 Overview

Your AgenticMemory system provides three endpoints that work together:

1. **Client Data** - Pre-call memory retrieval & personalized greetings
2. **Memory Search** - In-call semantic search tool for agents
3. **Post-Call** - Automatic memory storage after conversations

---

## 📋 Prerequisites

- [ ] ElevenLabs account (https://elevenlabs.io)
- [ ] AgenticMemory endpoints deployed (✅ Already done!)
- [ ] Your workspace key and API credentials

---

## 🚀 Step-by-Step Setup

### Step 1: Create Your ElevenLabs Agent

1. **Log into ElevenLabs Dashboard**
   - Go to https://elevenlabs.io/app/conversational-ai
   - Click **"Create Agent"** or **"New Conversational AI"**

2. **Configure Basic Settings**
   ```
   Agent Name: [Your Agent Name]
   Voice: [Select your preferred voice]
   Language: English (or your preference)
   ```

3. **Set Agent Prompt**
   
   Use this as your base prompt (customize as needed):
   
   ```
   You are a helpful and friendly AI assistant. You have access to conversation 
   history and caller preferences through your memory system.
   
   When greeting callers:
   - If you recognize them (have their name), greet them warmly by name
   - Reference relevant past interactions naturally
   - Show you remember their preferences
   
   During conversations:
   - Use the memory_search tool to recall specific details when needed
   - Keep responses natural and conversational
   - Don't mention the memory system explicitly unless asked
   
   Your goal is to provide personalized, context-aware assistance that makes 
   every caller feel valued and remembered.
   ```

---

### Step 2: Configure Client Data Webhook (Conversation Initiation)

This enables personalized greetings for returning callers.

1. **In Agent Settings, find "Conversation Initiation" or "Client Data"**

2. **Add Webhook Configuration:**
   ```
   Webhook URL:
   https://8nv3jj2gie.execute-api.us-east-1.amazonaws.com/Prod/client-data
   
   Method: POST
   ```

3. **Add Custom Header:**
   ```
   Header Name: X-Workspace-Key
   Header Value: wsec_eb779969b7cb5cde6cdd9c6dfc4e2a08fa38cd6711b86eced6c101039871f6ac
   ```

4. **Request Body Format:**
   
   ElevenLabs will automatically send:
   ```json
   {
     "caller_id": "+16129782029"
   }
   ```

5. **What This Does:**
   - ✅ Retrieves caller's memory before conversation starts
   - ✅ Generates personalized first message if name is known
   - ✅ Provides conversation context to your agent
   - ✅ Makes returning callers feel recognized immediately

---

### Step 3: Add Memory Search Tool (Agent Tool)

This allows your agent to search conversation history during calls.

1. **In Agent Settings, find "Tools" or "Custom Tools"**

2. **Click "Add Tool" or "Create Custom Tool"**

3. **Configure Tool:**
   ```
   Tool Name: memory_search
   
   Description: 
   Search the caller's conversation history and stored preferences. 
   Use this to recall specific details, preferences, or past interactions.
   
   Tool Type: HTTP Request / API Call
   Method: POST
   
   URL:
   https://7h6j2vasna.execute-api.us-east-1.amazonaws.com/Prod/retrieve
   ```

4. **Parameters:**
   ```json
   {
     "query": {
       "type": "string",
       "description": "What to search for (e.g., 'food preferences', 'last order', 'account issues')",
       "required": true
     },
     "user_id": {
       "type": "string",
       "description": "The caller's phone number (automatically provided)",
       "required": true
     }
   }
   ```

5. **Parameter Mapping:**
   - Map `user_id` to the caller's phone number variable (usually `{{caller_phone}}` or `{{phone_number}}`)

6. **Example Tool Usage:**
   
   When your agent needs to recall information:
   ```
   Agent thinks: "I need to check their food preferences"
   Tool Call: memory_search(query="food preferences", user_id="+16129782029")
   Response: Returns relevant memories about pizza, restaurants, etc.
   Agent responds: "I remember you love pepperoni pizza from Tony's!"
   ```

---

### Step 4: Configure Post-Call Webhook (Memory Storage)

This automatically saves conversation details after each call.

1. **In Agent Settings, find "Post-Call Webhook" or "Call Completion"**

2. **Add Webhook Configuration:**
   ```
   Webhook URL:
   https://7iumhxcckh.execute-api.us-east-1.amazonaws.com/Prod/post-call
   
   Method: POST
   ```

3. **Enable HMAC Signature Verification:**
   ```
   HMAC Algorithm: SHA-256
   
   HMAC Signing Key:
   [Your HMAC key - stored in your AWS CloudFormation parameters]
   
   Signature Header: X-ElevenLabs-Signature
   Timestamp Tolerance: 30 minutes
   ```
   
   > **Note:** If you don't have your HMAC key, check your AWS CloudFormation 
   > stack parameters or use the AWS Console to view your Lambda environment 
   > variables (ELEVENLABS_HMAC_KEY).

4. **Payload Format:**
   
   ElevenLabs automatically sends this structure:
   ```json
   {
     "conversation_id": "conv_abc123",
     "call_id": "call_xyz789",
     "agent_id": "agent_456",
     "caller_phone_number": "+16129782029",
     "transcript": "Full conversation text...",
     "transcript_with_timestamps": [...],
     "call_duration_seconds": 245,
     "call_successful": true,
     "metadata": {...}
   }
   ```

5. **What This Does:**
   - ✅ Automatically stores conversation after each call
   - ✅ Extracts factual information (names, preferences, etc.)
   - ✅ Saves full semantic context
   - ✅ Builds caller profile over time
   - ✅ HMAC security prevents unauthorized memory injection

---

### Step 5: Test Your Setup

#### Test 1: First-Time Caller (No Memory)

1. **Call your agent** with a new phone number
2. **Expected behavior:**
   - Generic greeting (no personalization)
   - Agent has no prior context
3. **During call, share information:**
   ```
   "Hi, my name is Sarah and I love Italian food, 
   especially from Giuseppe's Restaurant."
   ```
4. **After call:**
   - Memory automatically stored
   - Wait 30 seconds for processing

#### Test 2: Returning Caller (With Memory)

1. **Call again with the same number**
2. **Expected behavior:**
   - Personalized greeting: "Hi Sarah! Great to hear from you again!"
   - Agent remembers your preferences
3. **Test memory search:**
   ```
   You: "What's my favorite restaurant?"
   Agent: [Uses memory_search tool]
   Agent: "You love Italian food from Giuseppe's Restaurant!"
   ```

#### Test 3: Verify Memory Storage

Run the test script to see stored memories:

```bash
cd /home/ubuntu/proj/claude/AgenticMemory
source test_env/bin/activate
python test_production_ready.py
```

Or use the direct memory viewer:

```bash
python test_memory_direct.py
```

---

## 🔧 Advanced Configuration

### Custom First Messages

Edit the greeting logic in `src/client_data/handler.py`:

```python
def generate_personalized_greeting(caller_name, memory_count):
    """Customize your greeting messages here"""
    
    if caller_name:
        greetings = [
            f"Hi {caller_name}! Great to hear from you again!",
            f"Hello {caller_name}! How can I help you today?",
            f"Welcome back, {caller_name}!",
        ]
        return random.choice(greetings)
    
    return None  # Use default agent greeting
```

### Adjust Memory Search Limits

In `src/retrieve/handler.py`:

```python
# Change how many memories are returned per search
SEARCH_LIMIT = int(os.environ.get('MEM0_SEARCH_LIMIT', '3'))  # Default: 3
```

### Memory Types

Your system stores two types of memories:

**Factual Memory** (`metadata.type = "factual"`)
- Names, preferences, specific facts
- Quick lookup data
- Example: "User's name is Sarah", "Prefers Italian food"

**Semantic Memory** (`metadata.type = "semantic"`)
- Full conversation context
- Detailed interactions
- Example: Full transcript with timestamps

---

## 🐛 Troubleshooting

### Issue: Agent doesn't greet by name

**Check:**
1. Post-call webhook is configured and firing
2. Wait 30-60 seconds after first call for memory processing
3. Verify name was mentioned in conversation
4. Check CloudWatch logs: `/aws/lambda/sam-app-ClientDataFunction-*`

**Debug:**
```bash
# Test client-data endpoint directly
curl -X POST https://8nv3jj2gie.execute-api.us-east-1.amazonaws.com/Prod/client-data \
  -H "X-Workspace-Key: wsec_eb779969b7cb5cde6cdd9c6dfc4e2a08fa38cd6711b86eced6c101039871f6ac" \
  -H "Content-Type: application/json" \
  -d '{"caller_id": "+16129782029"}'
```

### Issue: Memory search not working

**Check:**
1. Tool parameters are correctly mapped
2. `user_id` is receiving the caller's phone number
3. Query string is descriptive enough

**Debug:**
```bash
# Test retrieve endpoint directly
curl -X POST https://7h6j2vasna.execute-api.us-east-1.amazonaws.com/Prod/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "food preferences", "user_id": "+16129782029"}'
```

### Issue: Memories not saving

**Check:**
1. Post-call webhook URL is correct
2. HMAC signature is configured (or webhook still fires but logs auth failure)
3. CloudWatch logs: `/aws/lambda/sam-app-PostCallFunction-*`

**Debug:**
```bash
# Check recent Lambda invocations
aws logs tail /aws/lambda/sam-app-PostCallFunction-* --follow
```

### Issue: 401 Unauthorized on client-data

**Check:**
1. `X-Workspace-Key` header is included
2. Header value matches exactly (no extra spaces)
3. Header name uses correct capitalization

---

## 📊 Monitoring & Logs

### CloudWatch Log Groups

Monitor your functions in AWS CloudWatch:

```
/aws/lambda/sam-app-ClientDataFunction-*    # Pre-call memory retrieval
/aws/lambda/sam-app-RetrieveFunction-*      # Memory searches during calls
/aws/lambda/sam-app-PostCallFunction-*      # Post-call memory storage
```

### View Logs

```bash
# Client Data logs
aws logs tail /aws/lambda/sam-app-ClientDataFunction-* --follow

# Retrieve logs  
aws logs tail /aws/lambda/sam-app-RetrieveFunction-* --follow

# Post-Call logs
aws logs tail /aws/lambda/sam-app-PostCallFunction-* --follow
```

### Key Metrics to Monitor

- **Client Data**: Response time, memory count, personalization rate
- **Retrieve**: Search queries, result count, relevance scores
- **Post-Call**: Processing success rate, memory storage count

---

## 🔐 Security Best Practices

### Rotate Keys Regularly

Update your workspace key periodically:

```bash
# Generate new workspace key
NEW_KEY="wsec_$(openssl rand -hex 32)"

# Update CloudFormation parameter
aws cloudformation update-stack \
  --stack-name sam-app \
  --use-previous-template \
  --parameters ParameterKey=ElevenLabsWorkspaceKey,ParameterValue=$NEW_KEY

# Update ElevenLabs webhook header
```

### Monitor for Suspicious Activity

Watch for:
- Unusual caller_id patterns
- High volume of failed auth attempts
- Unexpected memory queries

### HMAC Signature

Always enable HMAC signing for post-call webhook to prevent:
- Unauthorized memory injection
- Spoofed conversation data
- Malicious memory poisoning

---

## 📚 Additional Resources

### Documentation
- [ElevenLabs API Docs](https://elevenlabs.io/docs)
- [Mem0 Platform Docs](https://docs.mem0.ai)
- [AWS Lambda Logs](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-cloudwatchlogs.html)

### Test Scripts
- `test_memory_direct.py` - Direct Mem0 API testing
- `test_production_ready.py` - Full system validation
- `test_post_call_comprehensive.py` - HMAC authentication testing

### Support Files
- `README.md` - Project overview
- `SPECIFICATION.md` - Technical specifications
- `.env` - Local environment configuration

---

## ✅ Setup Checklist

Use this to verify your configuration:

- [ ] ElevenLabs agent created
- [ ] Agent prompt configured
- [ ] Client Data webhook added with X-Workspace-Key header
- [ ] Memory Search tool configured with correct parameters
- [ ] Post-Call webhook added with HMAC signing
- [ ] Test call completed (first-time caller)
- [ ] Memory storage verified (check after 30 seconds)
- [ ] Test call completed (returning caller with personalized greeting)
- [ ] Memory search tested during call
- [ ] CloudWatch logs reviewed for errors
- [ ] Production endpoints validated with test scripts

---

## 🎉 You're All Set!

Your AgenticMemory system is now integrated with ElevenLabs. Every conversation will:

1. **Start** with personalized context
2. **Enable** intelligent memory recall during calls
3. **End** with automatic memory storage

Your callers will experience truly personalized, context-aware conversations that improve over time!

---

## 📞 Need Help?

If you encounter issues:

1. Check the troubleshooting section above
2. Review CloudWatch logs for error details
3. Run test scripts to validate individual components
4. Check AWS Lambda function configurations

**Happy building! 🚀**
