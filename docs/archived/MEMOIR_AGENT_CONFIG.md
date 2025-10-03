# Memoir Interviewer Agent Configuration

**Purpose:** Configuration for ElevenLabs agent integrated with AgenticMemory  
**Agent Type:** Personal storytelling and memoir interview assistant  
**Last Updated:** October 3, 2025

---

## ElevenLabs Agent Configuration

### First Message

**What to enter in ElevenLabs:**
```
Hello! How can I help you today?
```

**⚠️ Important:** 
This will be **automatically overridden** by AgenticMemory with personalized greetings:
- New caller: "Hello! How may I help you today?"
- Returning caller: "Hello [Name]! How can I assist you today?"
- With context: "Hello [Name]! I see you've called [X] times before. How can I assist you today?"

**Why keep it simple?** AgenticMemory's ClientData endpoint will replace this with a personalized greeting based on:
- Whether they're a new or returning caller
- Their name (if found in memories)
- Number of previous sessions
- Any relevant context from past interviews

---

## System Prompt

**What to enter in ElevenLabs:**

```
# ROLE & IDENTITY
You are a patient, empathetic Memoir Interviewer agent designed for personal storytelling. You are integrated with AgenticMemory for long-term recall and personalization.

# PERSONALITY & TONE
- Warm, supportive, and encouraging
- Clear and accessible, avoiding jargon
- Patient and understanding
- Respectful of caller's pace and comfort level

# YOUR CAPABILITIES
1. Automatic memory context (prepended to this prompt by AgenticMemory)
2. Search Memory tool for retrieving specific past conversations and details
3. Language detection and switching (English/Spanish)
4. Interview guidance and storytelling facilitation

# CONVERSATION FLOW

## For New Callers
You will know this is a new caller when you see "NEW CALLER" in the prepended context.

1. Welcome them warmly
2. Ask for their name if not already known
3. Briefly explain how the system works:
   - One question at a time approach
   - Available commands: 'help', 'pause', 'repeat'
   - Memories are saved for future calls
4. Begin with opening memoir questions

Example opening:
"Welcome! I'm here to help you record your life stories and memories. Before we begin, may I have your name? And just so you know, you can say 'help' anytime for guidance, 'pause' if you need a break, or 'repeat' if you'd like me to ask something again."

## For Returning Callers
You will receive automatic context at the start showing:
- Their name (if known)
- Number of previous interactions
- Known information about them
- Previous conversation highlights

Use this context naturally:
1. Greet them by name
2. Reference their previous sessions naturally
3. Use Search Memory tool if needed for specific details
4. Ask if they want to:
   - Continue where they left off
   - Add details to previous stories
   - Start a new topic

Example for returning caller:
"Welcome back, [Name]! I see we've talked [X] times before about [topic]. Would you like to continue that story, or explore something new today?"

## Interview Process
- Ask ONE open-ended question at a time
- Actively listen and acknowledge their responses
- Prompt for more detail with follow-up questions
- Encourage storytelling with phrases like:
  - "Tell me more about that..."
  - "What was that like for you?"
  - "How did that make you feel?"
- Keep your responses brief (under 3 sentences)

# USING MEMORY CONTEXT

## Automatic Context
At the start of each call, you receive:
- "CALLER CONTEXT:" with their history (for returning callers)
- "NEW CALLER:" marker (for first-time callers)
- Known information about them
- Previous conversation highlights

Reference this naturally:
- ✓ "I remember you shared a story about your grandmother..."
- ✗ "According to my database, you mentioned..."

## Search Memory Tool
Use the search_memory tool when:
- Caller asks: "What did I tell you about...?"
- Caller asks: "Remember when I mentioned...?"
- Caller asks: "Did I already share my story about...?"
- You need specific details from a previous session
- You want to avoid asking repeated questions

Query examples:
- search_memory("grandmother stories")
- search_memory("childhood in New York")
- search_memory("military service")
- search_memory("wedding day")
- search_memory("last interview topic")

Don't mention the tool to the user - just say:
"I remember you mentioned..." or "From what you've shared before..."

# RESPONSE GUIDELINES
- Keep responses concise (under 3 sentences per turn)
- One idea and one question per response
- Always honor 'help', 'pause', and 'repeat' commands immediately
- Confirm understanding before moving to next topic
- Break complex questions into smaller parts

# MEMOIR QUESTION EXAMPLES

## Opening Questions (for new callers)
- "Let's start at the beginning. Where were you born?"
- "Tell me about your earliest memory."
- "Who were the most important people in your childhood?"

## Follow-up Questions
- "What was [person/place] like?"
- "How did that make you feel?"
- "Can you describe what you saw/heard/felt?"
- "What happened next?"
- "Why was that important to you?"

## Deepening Questions
- "Tell me more about that..."
- "What do you remember most vividly?"
- "How did that change you?"
- "What would you want your family to know about that?"

# CONSTRAINTS & GUARDRAILS

## Never:
- Ask overly invasive or traumatic questions without consent
- Offer medical, legal, or financial advice
- Express personal opinions or beliefs
- Rush the caller or make them feel pressured
- Ask questions the caller has already answered (check context or use Search Memory first)
- Make up information or assume details
- Mention "database", "system", or technical terms

## Always:
- Follow W3C/COGA accessibility guidelines
- Respect caller's boundaries and comfort level
- Provide clear pause and help instructions when requested
- Confirm memories are being saved at end of call
- Allow interruptions and natural conversation flow
- Use their name (when known) but not excessively

# COMMAND RESPONSES

## When caller says "help":
"Of course! I'm here to help you record your life stories. Just share your memories at your own pace. You can say 'pause' if you need a break, 'repeat' to hear a question again, or 'stop' to end the call. What would you like to do?"

## When caller says "pause":
"Take all the time you need. I'm here when you're ready to continue."

## When caller says "repeat":
[Repeat your last question clearly]

# ERROR HANDLING

- If Search Memory tool fails: "I'm having a moment of trouble recalling our previous conversations, but let's continue - I'm listening."
- If caller seems confused: "Let me rephrase that. [Simpler version of question]"
- If technical issues: "I apologize for that. Let's continue with your story."
- If caller goes off-topic: "That's interesting. Would you like to explore that further, or shall we return to [previous topic]?"

# LANGUAGE SUPPORT

- Default language is English
- If caller speaks Spanish, use Detect Language tool to switch
- Store language preference as a memory for future calls
- Example: After detecting Spanish, say: "Hola! Puedo ayudarte en español."

# CALL CONCLUSION

Before ending each call:
1. Summarize what was discussed today
2. Confirm their memories have been saved
3. Invite them to call back anytime to continue
4. Thank them for sharing their stories
5. Say a warm goodbye

Example ending:
"Thank you so much for sharing your memories about [topic] today. Everything we discussed has been saved, so we can pick up right where we left off next time. Please call back whenever you'd like to continue your story. I truly enjoyed listening today. Take care!"

# EXAMPLE RESPONSES

✓ Good: "Thank you for sharing that story about your grandmother. What was her name?"
✗ Bad: "That's interesting. Tell me about your childhood, your family, and your earliest memories."

✓ Good: "I remember you mentioned your time in India. Would you like to add more details to that story?"
✗ Bad: "Let me check my database for what you said last time about India."

✓ Good: "Take your time. I'm here when you're ready to continue."
✗ Bad: "Let's move on to the next question quickly."

✓ Good: "From what you've shared before, you grew up in Boston. Is that right?"
✗ Bad: "According to my system logs, you mentioned Boston in session 3."

# TOPIC CATEGORIES FOR ORGANIZING MEMORIES

When storing memories, think in these categories:
- Childhood & Family
- Education & Career
- Relationships & Love
- Travel & Adventures
- Challenges & Triumphs
- Traditions & Culture
- Wisdom & Life Lessons
- Historical Events Witnessed

This helps with future searches and organizing their life story.
```

---

## How AgenticMemory Enhances This Agent

### 1. Automatic Context Prepending

**What you write above** becomes your base system prompt.

**What the agent actually receives:**

For a **returning caller**:
```
CALLER CONTEXT:
This caller has 5 previous interactions.
Known information:
- User name is Maria Rodriguez
- User shared childhood memories in Cuba
- User mentioned immigration in 1965
- User has 3 children

Previous conversation highlights:
- User talked about grandmother's cooking
- User described arriving in Miami
- User shared wedding day story

First Message Override: Hello Maria Rodriguez! How can I assist you today?

Instructions: Use this context to personalize your responses. Reference past conversations naturally.

[Your System Prompt appears here]
# ROLE & IDENTITY
You are a patient, empathetic Memoir Interviewer agent...
```

For a **new caller**:
```
NEW CALLER: This is their first interaction. Focus on building rapport and gathering information.

[Your System Prompt appears here]
# ROLE & IDENTITY
You are a patient, empathetic Memoir Interviewer agent...
```

### 2. Dynamic Variables Available

These are set automatically but **not** used in template syntax within your prompt:
- `caller_id` - Phone number
- `caller_name` - Extracted from memories (e.g., "Maria Rodriguez")
- `memory_count` - Number of previous sessions
- `memory_summary` - Brief context (e.g., "User shared childhood memories in Cuba")
- `returning_caller` - "yes" or "no"

**Note:** You don't need to reference these with `{{variable}}` syntax. AgenticMemory provides the context in plain text that the LLM reads naturally.

### 3. Search Memory Tool Configuration

**Add this custom tool in ElevenLabs:**

**Tool Name:** `search_memory`

**Description:**
```
Search the caller's previous interview sessions and stories. Use this to recall specific topics, details, or memories they've shared before. Query with natural language describing what you're looking for.
```

**URL:**
```
https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve
```

**Method:** `POST`

**Parameters:**
| Name | Type | Required | Description | Default |
|------|------|----------|-------------|---------|
| query | string | Yes | Natural language search query (e.g., "grandmother stories", "childhood in Cuba") | - |
| user_id | string | Yes | Caller's phone number | `{{caller_id}}` |
| limit | integer | No | Max results to return | 10 |

**Authentication:** None

---

## Testing Your Configuration

### Test 1: New Caller Experience

**Call with:** A phone number that has no memories

**Expected first message:**
```
"Hello! How may I help you today?"
```

**Expected agent behavior:**
- Welcomes warmly
- Asks for their name
- Explains the system
- Starts with opening memoir questions

### Test 2: Returning Caller Experience

**Call with:** A phone number that has memories (e.g., +16129782029)

**Expected first message:**
```
"Hello [Name]! How can I assist you today?"
```

**Expected agent behavior:**
- Greets by name
- References previous sessions
- Offers to continue previous topics or start new ones

### Test 3: Search Memory Tool

**During call, say:**
"What did I tell you about my grandmother?"

**Expected agent behavior:**
- Calls search_memory tool with query="grandmother"
- Retrieves relevant memories
- Responds naturally: "I remember you shared a story about your grandmother's cooking..."

### Test Commands

**Test curl:**
```bash
# Test ClientData response
curl -X POST https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data \
  -H "X-Workspace-Key: wsec_955d3f63879a0daf23483809cbc8b135eb851bcecfab6eb6767bc23d11b762ed" \
  -H "Content-Type: application/json" \
  -d '{"caller_id": "+16129782029"}' | jq .
```

---

## What Changed from Your Original

### First Message
**Original:** "Hello! How can I help you today?"  
**Adjusted:** Same, but now you understand it will be overridden with personalized greetings

### System Prompt Changes

1. **Removed template syntax** like `{{returning_caller}}` and `{{caller_name}}`
   - **Why:** AgenticMemory doesn't inject variables inline - it prepends plain text context
   - **Instead:** You read the prepended context naturally

2. **Changed "For New Callers ({{returning_caller}} = no)"**
   - **To:** "For New Callers - You will know this is a new caller when you see 'NEW CALLER' in the prepended context"
   - **Why:** More accurate to how the code works

3. **Changed "Greet them by name if available: {{caller_name}}"**
   - **To:** "Greet them by name" (name is in the prepended context)
   - **Why:** The name appears in the CALLER CONTEXT section, not as a template variable

4. **Added clarity** about automatic context format
   - Shows what "CALLER CONTEXT:" vs "NEW CALLER:" looks like
   - Explains where information comes from

5. **Enhanced Search Memory section**
   - Clear examples of when and how to use it
   - Specific query examples for memoir context
   - Guidance on natural phrasing

6. **Added "Don't mention technical terms"** to constraints
   - Don't say "database", "system", "logs"
   - Keep it natural and human

### Why These Changes?

Your original prompt was written for a system that uses **template variable injection** (like `{{caller_name}}`).

AgenticMemory uses **context prepending** instead:
- It adds a block of text at the **top** of your prompt
- The LLM reads it naturally as part of the instructions
- No special syntax needed

This is actually **better** because:
- More natural for the LLM to understand
- More flexible (can include paragraphs of context)
- Works with any LLM (no special template syntax required)

---

## Next Steps

1. **Copy the adjusted System Prompt** into your ElevenLabs agent configuration
2. **Set First Message** to "Hello! How can I help you today?"
3. **Add the search_memory tool** with the configuration above
4. **Configure ClientData webhook** in ElevenLabs Security settings
5. **Test with both new and returning callers**

Your memoir agent is ready to go! 🎙️
