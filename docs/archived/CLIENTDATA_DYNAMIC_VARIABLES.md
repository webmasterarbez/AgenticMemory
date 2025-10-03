# ClientData Dynamic Variables

## Overview

The **ClientData endpoint** (`/Prod/client-data`) returns dynamic variables in the ElevenLabs Conversation Initiation webhook format. These variables are used to personalize the conversation before the call starts.

---

## Dynamic Variables Returned

The ClientData Lambda function returns the following dynamic variables in the `dynamic_variables` object:

### Always Present

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `caller_id` | string | The caller's phone number (user_id in Mem0) | `"+16129782029"` |
| `memory_count` | string | Total number of memories for this caller | `"15"` |
| `memory_summary` | string | First/most important factual memory, or "New caller" | `"User sympathizes with people of color"` |
| `returning_caller` | string | Whether this is a returning caller | `"yes"` or `"no"` |

### Conditionally Present

| Variable | Type | Description | When Present | Example |
|----------|------|-------------|--------------|---------|
| `caller_name` | string | Extracted caller name from memories | Only if name found in memories | `"Stefan"`, `"Alice"` |

---

## Code Implementation

From `src/client_data/handler.py` (lines 280-290):

```python
# Add caller name to dynamic variables if found
dynamic_vars = {
    "caller_id": caller_id,
    "memory_count": str(memory_count),
    "memory_summary": memory_summary,
    "returning_caller": "yes" if memory_count > 0 else "no"
}

if caller_name:
    dynamic_vars["caller_name"] = caller_name
```

---

## Full Response Format

The complete response structure:

```json
{
  "type": "conversation_initiation_client_data",
  "dynamic_variables": {
    "caller_id": "+16129782029",
    "memory_count": "15",
    "memory_summary": "User sympathizes with people of color",
    "returning_caller": "yes",
    "caller_name": "Stefan"
  },
  "conversation_config_override": {
    "agent": {
      "prompt": {
        "prompt": "CALLER CONTEXT:\nThis caller has 15 previous interactions.\n..."
      },
      "first_message": "Hello Stefan! How can I assist you today?"
    }
  }
}
```

---

## Variable Details

### 1. `caller_id`
- **Always present**: Yes
- **Source**: From webhook request body (`caller_id` or `system__caller_id`)
- **Format**: E.164 phone number format (e.g., `+16129782029`)
- **Usage**: Unique identifier for caller, used as `user_id` in Mem0

### 2. `memory_count`
- **Always present**: Yes
- **Source**: Count of memories from `client.get_all(user_id=caller_id)`
- **Format**: String representation of integer
- **Values**: 
  - `"0"` for new callers
  - `"1"` to `"n"` for returning callers with memories
- **Usage**: Determine if caller is new or returning

### 3. `memory_summary`
- **Always present**: Yes
- **Source**: 
  - First factual memory if available
  - `"New caller"` if no memories exist
- **Format**: String (memory text or default message)
- **Example Values**:
  - New caller: `"New caller"`
  - Returning caller: `"User sympathizes with people of color"`
  - Or: `"Customer prefers email communication"`
- **Usage**: Quick summary of most important fact

### 4. `returning_caller`
- **Always present**: Yes
- **Source**: Derived from `memory_count > 0`
- **Format**: String literal
- **Values**: 
  - `"yes"` - Caller has memories
  - `"no"` - New caller (no memories)
- **Usage**: Quick boolean check for new vs returning

### 5. `caller_name` (Conditional)
- **Always present**: No (only if name extracted)
- **Source**: Extracted from memories using regex patterns
- **Format**: Proper case name (e.g., "Stefan", "Alice Johnson")
- **Patterns Used**: Multiple regex patterns including:
  - "name is [Name]"
  - "called [Name]"
  - "my name is [Name]"
  - "user [Name]"
  - "[Name] is the user"
- **Validation**: 
  - 2-30 characters
  - Only letters and spaces
  - Maximum 3 words
  - Excludes common non-names (wants, needs, help, etc.)
- **Usage**: Personalize greeting and responses
- **Example Values**: `"Stefan"`, `"Alice Johnson"`, `"Bob"`

---

## Name Extraction Logic

The `extract_caller_name()` function searches both factual and semantic memories using these patterns:

```python
name_patterns = [
    # Direct name patterns
    r"(?:name is|called|goes by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    r"(?:user(?:'s)?\s+name:?\s*)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    r"(?:customer name:?\s*)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    r"(?:my name is|i am|i'm)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    # More flexible patterns  
    r"user\s+name\s+is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+is\s+(?:the\s+)?(?:user|customer|caller)",
    # Semantic memory patterns
    r"user\s+([A-Z][a-z]+)",
    r"customer\s+([A-Z][a-z]+)",
]
```

---

## Usage in ElevenLabs

These dynamic variables can be referenced in your ElevenLabs agent configuration:

### In Agent Prompt
```
You are speaking with {{caller_name}}.
This is a {{returning_caller}} caller with {{memory_count}} previous interactions.
Key information: {{memory_summary}}
```

### In Agent Logic
```javascript
if (dynamic_variables.returning_caller === "yes") {
  // Use personalized approach
  greet("Welcome back, " + dynamic_variables.caller_name);
} else {
  // Use new caller approach
  greet("Hello! How may I help you today?");
}
```

### In Conditional Flows
```yaml
condition:
  variable: dynamic_variables.returning_caller
  operator: equals
  value: "yes"
action:
  message: "I see you've contacted us before. Let me pull up your information."
```

---

## Example Scenarios

### Scenario 1: New Caller
**Input:** Caller ID `+19995551234` (no existing memories)

**Output:**
```json
{
  "dynamic_variables": {
    "caller_id": "+19995551234",
    "memory_count": "0",
    "memory_summary": "New caller",
    "returning_caller": "no"
  }
}
```
**Note:** No `caller_name` field (not extracted)

---

### Scenario 2: Returning Caller Without Name
**Input:** Caller ID `+18885554321` with 5 memories, no name in memories

**Output:**
```json
{
  "dynamic_variables": {
    "caller_id": "+18885554321",
    "memory_count": "5",
    "memory_summary": "Customer prefers email communication",
    "returning_caller": "yes"
  }
}
```
**Note:** No `caller_name` field (not found in memories)

---

### Scenario 3: Returning Caller With Name
**Input:** Caller ID `+16129782029` with 15 memories, name "Stefan" in memories

**Output:**
```json
{
  "dynamic_variables": {
    "caller_id": "+16129782029",
    "memory_count": "15",
    "memory_summary": "User sympathizes with people of color",
    "returning_caller": "yes",
    "caller_name": "Stefan"
  }
}
```
**Note:** `caller_name` present because extracted from memories

---

## Personalized Greeting Generation

The `first_message` is also generated based on these variables:

### Logic:
```python
def generate_personalized_greeting(
    caller_name: Optional[str],
    is_returning: bool,
    account_status: Optional[str] = None,
    last_interaction: Optional[str] = None,
    preferences: List[str] = None
) -> str:
```

### Examples:

| Scenario | Greeting |
|----------|----------|
| New caller | `"Hello! How may I help you today?"` |
| Returning, no name | `"Hello! How can I assist you today?"` |
| Returning with name | `"Hello Stefan! How can I assist you today?"` |
| Returning with name + context | `"Hello Alice! I see you're a premium customer. How can I help?"` |

---

## Memory Context in Prompt

In addition to dynamic variables, the response includes a `prompt` override with full memory context:

```
CALLER CONTEXT:
This caller has 15 previous interactions.
Known information:
- User sympathizes with people of color
- User has friends
- User participates in rallies across the country
- User is engaged in civil social justice
- Sheila Cunningham is the user

Previous conversation highlights:
- She traveled to India with a friend
- Sheila's parents never married and did not graduate college
- User discussed education and independence

First Message Override: Hello Stefan! How can I assist you today?

Instructions: Use this context to personalize your responses. Reference past conversations naturally.
```

---

## Testing Dynamic Variables

Use the test script to see dynamic variables for any caller:

```bash
# Test with returning caller
python scripts/test_clientdata.py

# Output shows dynamic variables:
Dynamic Variables:
  caller_id: +16129782029
  memory_count: 15
  memory_summary: User sympathizes with people of color
  returning_caller: yes
  caller_name: Stefan
```

---

## Summary

**Always Present (4 variables):**
1. ✅ `caller_id` - Phone number
2. ✅ `memory_count` - Number of memories
3. ✅ `memory_summary` - Most important fact or "New caller"
4. ✅ `returning_caller` - "yes" or "no"

**Conditionally Present (1 variable):**
5. ⚠️ `caller_name` - Only if name extracted from memories

**Total:** Up to 5 dynamic variables returned per request.

---

## API Reference

**Endpoint:** `POST /Prod/client-data`

**Request:**
```json
{
  "caller_id": "+16129782029"
}
```

**Response:**
```json
{
  "type": "conversation_initiation_client_data",
  "dynamic_variables": {
    "caller_id": "+16129782029",
    "memory_count": "15",
    "memory_summary": "...",
    "returning_caller": "yes",
    "caller_name": "Stefan"
  },
  "conversation_config_override": {
    "agent": {
      "prompt": {"prompt": "..."},
      "first_message": "..."
    }
  }
}
```

**Authentication:** `X-Workspace-Key` header required
