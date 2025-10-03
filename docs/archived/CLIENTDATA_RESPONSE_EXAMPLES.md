# ClientData Response Payload Examples

**Purpose:** This document shows the exact JSON payloads that the AgenticMemory ClientData endpoint sends back to ElevenLabs agents.

**Source:** `src/client_data/handler.py` (lines 285-310)

**Last Updated:** October 3, 2025

---

## Table of Contents

1. [Response Structure](#response-structure)
2. [Example 1: New Caller (No Memories)](#example-1-new-caller-no-memories)
3. [Example 2: Returning Caller with Name](#example-2-returning-caller-with-name)
4. [Example 3: Returning Caller without Name](#example-3-returning-caller-without-name)
5. [Example 4: Premium Customer with Rich History](#example-4-premium-customer-with-rich-history)
6. [Example 5: VIP Member with Context](#example-5-vip-member-with-context)
7. [Example 6: Customer with Multiple Context Factors](#example-6-customer-with-multiple-context-factors)
8. [Field Descriptions](#field-descriptions)
9. [How ElevenLabs Uses This Data](#how-elevenlabs-uses-this-data)

---

## Response Structure

The ClientData endpoint returns this JSON structure (from code lines 286-299):

```json
{
  "type": "conversation_initiation_client_data",
  "dynamic_variables": {
    "caller_id": "string (always present)",
    "memory_count": "string (always present)",
    "memory_summary": "string (always present)",
    "returning_caller": "string (always present: 'yes' or 'no')",
    "caller_name": "string (conditional: only if extracted from memories)"
  },
  "conversation_config_override": {
    "agent": {
      "prompt": {
        "prompt": "string (prepended to system prompt)"
      },
      "first_message": "string (overrides agent's default first message)"
    }
  }
}
```

---

## Example 1: New Caller (No Memories)

**Scenario:** First-time caller, no previous interactions

**Request to ClientData:**
```json
{
  "caller_id": "+15551234567"
}
```

**Response from ClientData:**
```json
{
  "type": "conversation_initiation_client_data",
  "dynamic_variables": {
    "caller_id": "+15551234567",
    "memory_count": "0",
    "memory_summary": "New caller",
    "returning_caller": "no"
  },
  "conversation_config_override": {
    "agent": {
      "prompt": {
        "prompt": "NEW CALLER: This is their first interaction. Focus on building rapport and gathering information."
      },
      "first_message": "Hello! How may I help you today?"
    }
  }
}
```

**What ElevenLabs Does:**
1. Sets dynamic variables in agent context
2. Prepends "NEW CALLER: ..." to system prompt
3. Uses "Hello! How may I help you today?" as opening message

---

## Example 2: Returning Caller with Name

**Scenario:** Returning caller with name extracted from memories

**Request to ClientData:**
```json
{
  "caller_id": "+16129782029"
}
```

**Memories in Mem0:**
```
Factual memories:
- User name is Stefan
- User prefers email communication
- User has account #12345

Semantic memories:
- User called about password reset
- User inquired about premium features
```

**Response from ClientData:**
```json
{
  "type": "conversation_initiation_client_data",
  "dynamic_variables": {
    "caller_id": "+16129782029",
    "caller_name": "Stefan",
    "memory_count": "5",
    "memory_summary": "User name is Stefan",
    "returning_caller": "yes"
  },
  "conversation_config_override": {
    "agent": {
      "prompt": {
        "prompt": "CALLER CONTEXT:\nThis caller has 5 previous interactions.\nKnown information:\n- User name is Stefan\n- User prefers email communication\n- User has account #12345\n\nPrevious conversation highlights:\n- User called about password reset\n- User inquired about premium features\n\nFirst Message Override: Hello Stefan! How can I assist you today?\n\nInstructions: Use this context to personalize your responses. Reference past conversations naturally."
      },
      "first_message": "Hello Stefan! How can I assist you today?"
    }
  }
}
```

**What ElevenLabs Does:**
1. Sets all 5 dynamic variables (including `caller_name`)
2. Prepends full caller context to system prompt
3. Uses personalized greeting with name

---

## Example 3: Returning Caller without Name

**Scenario:** Returning caller but name not found in memories

**Request to ClientData:**
```json
{
  "caller_id": "+15559876543"
}
```

**Memories in Mem0:**
```
Factual memories:
- User called about billing issue
- User has basic plan

Semantic memories:
- User reported charge error
```

**Response from ClientData:**
```json
{
  "type": "conversation_initiation_client_data",
  "dynamic_variables": {
    "caller_id": "+15559876543",
    "memory_count": "3",
    "memory_summary": "User called about billing issue",
    "returning_caller": "yes"
  },
  "conversation_config_override": {
    "agent": {
      "prompt": {
        "prompt": "CALLER CONTEXT:\nThis caller has 3 previous interactions.\nKnown information:\n- User called about billing issue\n- User has basic plan\n\nPrevious conversation highlights:\n- User reported charge error\n\nFirst Message Override: Hello! I see you've called before, but I don't have your name on file. Could you please tell me your name so I can better assist you?\n\nInstructions: Use this context to personalize your responses. Reference past conversations naturally."
      },
      "first_message": "Hello! I see you've called before, but I don't have your name on file. Could you please tell me your name so I can better assist you?"
    }
  }
}
```

**What ElevenLabs Does:**
1. Sets 4 dynamic variables (no `caller_name`)
2. Prepends caller context to system prompt
3. Uses greeting that asks for name

---

## Example 4: Premium Customer with Rich History

**Scenario:** Premium customer with extensive history

**Request to ClientData:**
```json
{
  "caller_id": "+14155551234"
}
```

**Memories in Mem0:**
```
Factual memories:
- User name is Alice Johnson
- User has premium account since 2023
- User prefers phone communication
- User is in timezone EST
- User's account manager is John Smith

Semantic memories:
- User upgraded to premium on 2023-06-15
- User called about API integration
- User requested billing statement
```

**Response from ClientData:**
```json
{
  "type": "conversation_initiation_client_data",
  "dynamic_variables": {
    "caller_id": "+14155551234",
    "caller_name": "Alice Johnson",
    "memory_count": "8",
    "memory_summary": "User name is Alice Johnson",
    "returning_caller": "yes"
  },
  "conversation_config_override": {
    "agent": {
      "prompt": {
        "prompt": "CALLER CONTEXT:\nThis caller has 8 previous interactions.\nKnown information:\n- User name is Alice Johnson\n- User has premium account since 2023\n- User prefers phone communication\n- User is in timezone EST\n- User's account manager is John Smith\n\nPrevious conversation highlights:\n- User upgraded to premium on 2023-06-15\n- User called about API integration\n- User requested billing statement\n\nFirst Message Override: Hello Alice Johnson! I see you're a premium customer. How can I assist you today?\n\nInstructions: Use this context to personalize your responses. Reference past conversations naturally."
      },
      "first_message": "Hello Alice Johnson! I see you're a premium customer. How can I assist you today?"
    }
  }
}
```

**What ElevenLabs Does:**
1. Sets all 5 dynamic variables
2. Prepends rich context (5 factual + 3 semantic memories)
3. Uses personalized greeting acknowledging premium status

---

## Example 5: VIP Member with Context

**Scenario:** VIP member with recent inquiry

**Request to ClientData:**
```json
{
  "caller_id": "+13105551234"
}
```

**Memories in Mem0:**
```
Factual memories:
- User name is Michael Chen
- User is VIP member since 2022
- User prefers email updates
- User has enterprise plan

Semantic memories:
- User had inquiry about billing on 2024-09-28
- User requested feature documentation
- User mentioned using API integration
```

**Response from ClientData:**
```json
{
  "type": "conversation_initiation_client_data",
  "dynamic_variables": {
    "caller_id": "+13105551234",
    "caller_name": "Michael Chen",
    "memory_count": "7",
    "memory_summary": "User name is Michael Chen",
    "returning_caller": "yes"
  },
  "conversation_config_override": {
    "agent": {
      "prompt": {
        "prompt": "CALLER CONTEXT:\nThis caller has 7 previous interactions.\nKnown information:\n- User name is Michael Chen\n- User is VIP member since 2022\n- User prefers email updates\n- User has enterprise plan\n\nPrevious conversation highlights:\n- User had inquiry about billing on 2024-09-28\n- User requested feature documentation\n- User mentioned using API integration\n\nFirst Message Override: Hello Michael Chen! Thank you for being a VIP member, and following up on your recent inquiry. How can I assist you today?\n\nInstructions: Use this context to personalize your responses. Reference past conversations naturally."
      },
      "first_message": "Hello Michael Chen! Thank you for being a VIP member, and following up on your recent inquiry. How can I assist you today?"
    }
  }
}
```

**What ElevenLabs Does:**
1. Sets all 5 dynamic variables
2. Prepends context with VIP status
3. Uses greeting that acknowledges VIP status + recent inquiry

---

## Example 6: Customer with Multiple Context Factors

**Scenario:** Customer with preference and previous issue

**Request to ClientData:**
```json
{
  "caller_id": "+12065551234"
}
```

**Memories in Mem0:**
```
Factual memories:
- User name is Sarah Williams
- User prefers email updates
- User has gold tier status
- User timezone is PST

Semantic memories:
- User reported email access problem on 2024-09-20
- User asked about account upgrade
- User mentioned traveling frequently
```

**Response from ClientData:**
```json
{
  "type": "conversation_initiation_client_data",
  "dynamic_variables": {
    "caller_id": "+12065551234",
    "caller_name": "Sarah Williams",
    "memory_count": "7",
    "memory_summary": "User name is Sarah Williams",
    "returning_caller": "yes"
  },
  "conversation_config_override": {
    "agent": {
      "prompt": {
        "prompt": "CALLER CONTEXT:\nThis caller has 7 previous interactions.\nKnown information:\n- User name is Sarah Williams\n- User prefers email updates\n- User has gold tier status\n- User timezone is PST\n\nPrevious conversation highlights:\n- User reported email access problem on 2024-09-20\n- User asked about account upgrade\n- User mentioned traveling frequently\n\nFirst Message Override: Hello Sarah Williams! I see you have gold status, and I hope we resolved your previous concern. How can I assist you today?\n\nInstructions: Use this context to personalize your responses. Reference past conversations naturally."
      },
      "first_message": "Hello Sarah Williams! I see you have gold status, and I hope we resolved your previous concern. How can I assist you today?"
    }
  }
}
```

**What ElevenLabs Does:**
1. Sets all 5 dynamic variables
2. Prepends context with tier status + issue history
3. Uses greeting with 2 context parts (gold status + previous concern)

---

## Field Descriptions

### Required Fields (Always Present)

#### `type`
- **Value:** `"conversation_initiation_client_data"`
- **Purpose:** Identifies this as conversation initiation data for ElevenLabs
- **Source:** Line 287 in handler

#### `dynamic_variables.caller_id`
- **Type:** String (phone number format)
- **Example:** `"+16129782029"`
- **Purpose:** Unique identifier for the caller
- **Source:** Request body, line 273

#### `dynamic_variables.memory_count`
- **Type:** String (number as string)
- **Example:** `"15"`
- **Purpose:** Number of previous interactions/memories
- **Source:** Mem0 `get_all()` count, line 274

#### `dynamic_variables.memory_summary`
- **Type:** String
- **Example:** `"User prefers email"` or `"New caller"`
- **Purpose:** Quick summary of most important fact
- **Source:** First factual memory or "New caller", lines 265-269

#### `dynamic_variables.returning_caller`
- **Type:** String (`"yes"` or `"no"`)
- **Example:** `"yes"`
- **Purpose:** Indicates if caller has previous history
- **Source:** Based on memory_count > 0, line 275

#### `conversation_config_override.agent.prompt.prompt`
- **Type:** String (multi-line)
- **Example:** `"CALLER CONTEXT:\nThis caller has 15 previous interactions..."`
- **Purpose:** Context prepended to agent's system prompt
- **Source:** Built from memories, lines 214-256

#### `conversation_config_override.agent.first_message`
- **Type:** String
- **Example:** `"Hello Stefan! How can I assist you today?"`
- **Purpose:** Overrides agent's default first message
- **Source:** `generate_personalized_greeting()`, lines 258-264

### Optional Fields (Conditional)

#### `dynamic_variables.caller_name`
- **Type:** String (proper case name)
- **Example:** `"Stefan"`, `"Alice Johnson"`
- **Purpose:** Caller's name for personalization
- **Source:** Extracted via regex from memories, lines 277-278
- **Condition:** Only included if name found in memories

---

## How ElevenLabs Uses This Data

### 1. Dynamic Variables Injection

ElevenLabs injects these variables into the agent's context, making them available in:
- System prompts via `{{caller_name}}`, `{{memory_count}}`, etc.
- First messages via template variables
- Tool calls (can be passed to custom tools)

**Example System Prompt:**
```
You are assisting {{caller_name}}.
They have {{memory_count}} previous interactions.
Returning caller: {{returning_caller}}
```

**Becomes:**
```
You are assisting Stefan.
They have 15 previous interactions.
Returning caller: yes
```

### 2. Prompt Override (Memory Context)

The `prompt.prompt` field is **prepended** to your agent's system prompt:

**Your System Prompt:**
```
You are a customer support agent for TechCo.
Be patient and helpful.
```

**What Agent Actually Receives:**
```
CALLER CONTEXT:
This caller has 15 previous interactions.
Known information:
- User name is Stefan
- User prefers email
- User has premium account

[Your System Prompt appears here]
You are a customer support agent for TechCo.
Be patient and helpful.
```

### 3. First Message Override

The `first_message` field **replaces** your agent's default first message:

**Your Agent Config First Message:**
```
"Hello! Welcome to TechCo. How can I help?"
```

**What Caller Hears:**
```
"Hello Stefan! I see you're a premium customer. How can I assist you today?"
```

### 4. Conversation Flow

```
1. Call starts
   ↓
2. ElevenLabs sends request to ClientData webhook
   POST https://your-clientdata-url/client-data
   Body: {"caller_id": "+16129782029"}
   Headers: {"X-Workspace-Key": "wsec_..."}
   ↓
3. ClientData retrieves memories from Mem0
   ↓
4. ClientData generates personalized response (this document)
   ↓
5. ElevenLabs receives response
   ↓
6. ElevenLabs:
   - Sets dynamic variables
   - Prepends prompt context
   - Uses custom first message
   ↓
7. Agent starts conversation with full context
```

---

## Testing the Response

### Using curl

```bash
curl -X POST https://YOUR-CLIENTDATA-URL/client-data \
  -H "X-Workspace-Key: wsec_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"caller_id": "+16129782029"}' \
  | jq .
```

### Using Python

```python
import requests
import json

url = "https://YOUR-CLIENTDATA-URL/client-data"
headers = {
    "X-Workspace-Key": "wsec_YOUR_KEY",
    "Content-Type": "application/json"
}
payload = {"caller_id": "+16129782029"}

response = requests.post(url, headers=headers, json=payload)
print(json.dumps(response.json(), indent=2))
```

### Expected Response Time

- **Cold start:** 3-5 seconds (first request)
- **Warm start:** 200-500ms (subsequent requests)
- **With many memories:** +100-300ms (Mem0 API call time)

---

## Error Responses

### 401 Unauthorized (Invalid Workspace Key)

```json
{
  "error": "Unauthorized"
}
```

**HTTP Status:** 401

### 400 Bad Request (Missing caller_id)

```json
{
  "error": "Missing caller_id"
}
```

**HTTP Status:** 400

### 500 Internal Server Error

```json
{
  "error": "Error message describing what went wrong"
}
```

**HTTP Status:** 500

---

## Response Headers

All successful responses include:

```
Content-Type: application/json
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Workspace-Key
Access-Control-Allow-Methods: POST,OPTIONS
```

**Purpose:** Enable CORS for ElevenLabs webhook calls

---

## Memory Context Limits

Based on code implementation (lines 226-242):

- **Factual Memories:** Up to 5 included in context
- **Semantic Memories:** Up to 3 included in context
- **Total Context Size:** ~500-1500 characters typical

**Why Limits?**
- Keep prompt concise
- Avoid LLM context bloat
- Focus on most relevant information
- Most recent/important memories prioritized

---

## Best Practices

### For Testing

1. **Test new caller:** Use phone number with no memories
2. **Test returning caller:** Use phone number with existing memories
3. **Test name extraction:** Ensure memories contain proper name format
4. **Test context limits:** Create caller with 10+ memories, verify only 5 factual + 3 semantic shown

### For Production

1. **Monitor response times:** Should be <500ms warm
2. **Check name extraction accuracy:** Review logs for false positives
3. **Verify greeting appropriateness:** Listen to actual calls
4. **Review context relevance:** Ensure most important memories included

### For Debugging

```bash
# Check CloudWatch logs
aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow

# Test with specific caller
curl -X POST https://your-url/client-data \
  -H "X-Workspace-Key: wsec_..." \
  -d '{"caller_id": "+16129782029"}' | jq .
```

---

## Related Documentation

- **ELEVENLABS_AGENT_SETUP_GUIDE.md** - Complete agent configuration guide
- **SYSTEM_PROMPT_EXAMPLES.md** - System prompt templates
- **CLIENTDATA_DYNAMIC_VARIABLES.md** - Dynamic variables reference
- **PRODUCT_DOCUMENTATION.md** - Full system architecture

---

## Version History

- **v1.0** (Oct 3, 2025) - Initial documentation with 6 comprehensive examples
