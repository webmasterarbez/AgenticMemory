# ElevenLabs Agent Setup Guide for AgenticMemory

**Version:** 1.0  
**Last Updated:** October 3, 2025  
**Target:** ElevenLabs Agents Platform with AgenticMemory Integration

---

## Table of Contents

1. [Overview](#overview)
2. [Agent Tab Configuration](#agent-tab-configuration)
3. [Workflow Tab Configuration](#workflow-tab-configuration)
4. [Voice Tab Configuration](#voice-tab-configuration)
5. [Analysis Tab Configuration](#analysis-tab-configuration)
6. [Tests Tab Configuration](#tests-tab-configuration)
7. [Security Tab Configuration](#security-tab-configuration)
8. [Advanced Tab Configuration](#advanced-tab-configuration)
9. [Widget Tab Configuration](#widget-tab-configuration)
10. [AgenticMemory Integration Setup](#agenticmemory-integration-setup)
11. [Best Practices & Recommendations](#best-practices--recommendations)

---

## Overview

This guide provides detailed explanations for every configuration option in the ElevenLabs Agents Platform, specifically tailored for integration with the AgenticMemory backend system.

### Prerequisites

- ElevenLabs account with Agents Platform access
- AgenticMemory backend deployed (see `PRODUCT_DOCUMENTATION.md`)
- API endpoint URLs from AgenticMemory deployment
- Workspace keys configured

### Integration Points

AgenticMemory integrates with ElevenLabs at three points:

1. **Pre-Call**: Conversation Initiation webhook (ClientData endpoint)
2. **During Call**: Custom tool for memory search (Retrieve endpoint)
3. **Post-Call**: Post-call webhook (PostCall endpoint)

---

## Agent Tab Configuration

The Agent tab controls the core behavior and intelligence of your conversational agent.

### 1. Agent Language

**What**: Default language for agent communication  
**Why**: Determines the primary language for responses and transcription  
**Who**: All users by default  
**When**: Set during initial agent creation

**Recommended Setting for AgenticMemory**:
```
English (US)
```

**Options**:
- English (multiple variants)
- Spanish
- French
- German
- Italian
- Portuguese
- Polish
- Dutch
- Turkish
- Russian
- Arabic
- Chinese
- Japanese
- Korean
- And more...

**Use Cases**:
- **Single Market**: Choose your primary customer base language
- **Global Business**: Use English as default, add additional languages
- **Localized Service**: Match your customer demographics

**Best Practice**: 
- Choose the language that 80%+ of your callers will use
- Use Additional Languages for minority language speakers
- Consider timezone and regional preferences

---

### 2. Additional Languages

**What**: Secondary languages callers can switch to  
**Why**: Enables multilingual support without creating multiple agents  
**Who**: Callers who speak languages other than the default  
**When**: Enable if you have a multilingual customer base

**Recommended Setting for AgenticMemory**:
```
Add languages only if >10% of callers need them
Common additions: Spanish, French, Mandarin
```

**How It Works**:
- Caller can request language change during call
- Agent uses "Detect language" tool to switch
- Memories stored in original language (language-neutral)

**Use Cases**:
- **Multilingual Support Centers**: Add all supported languages
- **Border Regions**: Add neighboring country languages
- **Tourist Services**: Add common tourist languages

**Best Practice**:
- Don't add languages you can't support well
- Test each language thoroughly
- Consider using separate agents for major languages (better quality)
- AgenticMemory stores all memories language-agnostically

**Integration Note**: AgenticMemory's memory search works across languages but may have reduced accuracy. Consider storing language preference as a memory.

---

### 3. First Message

**What**: Opening statement the agent delivers  
**Why**: Sets tone, provides context, starts conversation  
**Who**: All callers hear this (unless disabled)  
**When**: Immediately after call connects

**⚠️ IMPORTANT FOR AGENTICMEMORY**: 
This field is **DYNAMICALLY OVERRIDDEN** by the ClientData endpoint's `first_message` response!

**Recommended Setting**:
```
Default: "Hello! How can I help you today?"
(This will be replaced with personalized greeting from AgenticMemory)
```

---

#### How AgenticMemory Personalizes First Messages

The ClientData endpoint (`src/client_data/handler.py`) uses the `generate_personalized_greeting()` function to create contextual greetings based on:

1. **Caller Recognition**: Name extracted from memories
2. **Return Status**: New vs. returning caller
3. **Account Status**: Premium, VIP, Gold/Silver tiers
4. **Last Interaction**: Previous inquiry, issue, or request
5. **Preferences**: Communication preferences

---

#### Real Generated First Messages (From Code)

**Scenario 1: New Caller (No Memories)**
```
Input: caller_id="+15551234567", memories=[]
Output: "Hello! How may I help you today?"
```

**Scenario 2: Returning Caller with Name**
```
Input: caller_id="+16129782029", caller_name="Stefan", memories=5
Output: "Hello Stefan! How can I assist you today?"
```

**Scenario 3: Returning Caller without Name**
```
Input: caller_id="+15559876543", memories=3, no name found
Output: "Hello! I see you've called before, but I don't have your name on file. Could you please tell me your name so I can better assist you?"
```

**Scenario 4: Premium Customer with Context**
```
Input: 
  caller_name="Alice"
  account_status="User has premium account"
  memories=12
  
Output: "Hello Alice! I see you're a premium customer. How can I assist you today?"
```

**Scenario 5: VIP Member with Recent Inquiry**
```
Input:
  caller_name="Michael"
  account_status="VIP member since 2023"
  last_interaction="User had inquiry about billing"
  memories=25
  
Output: "Hello Michael! Thank you for being a VIP member, and following up on your recent inquiry. How can I assist you today?"
```

**Scenario 6: Customer with Preference + Previous Issue**
```
Input:
  caller_name="Sarah"
  last_interaction="User reported email access problem"
  preferences=["User prefers email updates"]
  memories=8
  
Output: "Hello Sarah! I hope we resolved your previous concern, and I know you prefer email updates. How can I assist you today?"
```

**Scenario 7: Gold Status Member**
```
Input:
  caller_name="David"
  account_status="Gold tier customer"
  memories=15
  
Output: "Hello David! I see you have gold status. How can I assist you today?"
```

---

#### Name Extraction Patterns (From Code)

AgenticMemory extracts names using these patterns (priority order):

1. **Direct patterns**: "name is Stefan", "called Alice", "goes by Michael"
2. **User patterns**: "user name: Sarah", "user's name is David"
3. **Customer patterns**: "customer name: John"
4. **Self-introduction**: "my name is Emily", "i am Robert", "i'm Jennifer"
5. **Declarative**: "user name is Alex"
6. **Reversed**: "Michael is the user", "Sarah is the customer"
7. **Semantic**: "user Stefan", "customer Alice"

**Validation**: Names must be 1-3 words, 2-30 characters, letters/spaces only, excluding common non-names (wants, needs, help, account, etc.)

---

#### Dynamic Variables Available

When using AgenticMemory, these variables are automatically populated:

| Variable | Always Present | Example | Source |
|----------|---------------|---------|--------|
| `{{caller_id}}` | ✅ Yes | `+16129782029` | Request body |
| `{{memory_count}}` | ✅ Yes | `15` | Mem0 get_all() count |
| `{{memory_summary}}` | ✅ Yes | `User prefers email` | First factual memory |
| `{{returning_caller}}` | ✅ Yes | `yes` / `no` | Based on memory count |
| `{{caller_name}}` | ⚠️ Conditional | `Stefan` | Extracted via regex patterns |

---

#### First Message Decision Tree (From Code Logic)

```
START
  |
  ├─ Has memories? NO → "Hello! How may I help you today?"
  |
  └─ Has memories? YES
       |
       ├─ Has name? NO → "Hello! I see you've called before, but I don't..."
       |
       └─ Has name? YES → "Hello {name}!"
            |
            ├─ Build context_parts[] (max 2):
            │   ├─ Check account_status → "I see you're a premium customer"
            │   │                      → "Thank you for being a VIP member"
            │   │                      → "I see you have {tier} status"
            │   ├─ Check last_interaction → "Following up on your recent inquiry"
            │   │                        → "I hope we resolved your previous concern"
            │   └─ Check preferences → "I know you prefer email updates"
            │                       → "I know you prefer phone communication"
            │
            ├─ Format context:
            │   ├─ 1 part: "{greeting} {context1}. How can I assist you today?"
            │   └─ 2 parts: "{greeting} {context1}, and {context2}. How can..."
            │
            └─ Return formatted greeting
```

---

#### Manual First Message Examples (Without AgenticMemory)

If not using AgenticMemory integration, here are effective first messages:

**Customer Support**:
```
"Hello! Thank you for calling Acme Support. How can I help you today?"
```

**Sales**:
```
"Hi there! Thanks for your interest in our products. What can I tell you about?"
```

**Healthcare**:
```
"Hello! You've reached HealthClinic. How may I assist you today?"
```

**Hospitality**:
```
"Good day! Welcome to Grand Hotel. How may I help make your stay exceptional?"
```

**Technical Support**:
```
"Hello! Welcome to TechSupport. Let's get your issue resolved. What's happening?"
```

---

#### Testing First Messages

**Test Scenarios**:
1. ✅ New caller (no memories)
2. ✅ Returning caller with name in memories
3. ✅ Returning caller without name
4. ✅ Premium/VIP customer
5. ✅ Recent inquiry/issue mentioned
6. ✅ Known preferences
7. ✅ Multiple context factors

**Test with curl**:
```bash
curl -X POST https://YOUR-CLIENT-DATA-URL/client-data \
  -H "X-Workspace-Key: wsec_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"caller_id": "+16129782029"}'
```

**Check response**:
```json
{
  "type": "conversation_initiation_client_data",
  "dynamic_variables": {
    "caller_id": "+16129782029",
    "caller_name": "Stefan",
    "memory_count": "15",
    "memory_summary": "User prefers email",
    "returning_caller": "yes"
  },
  "conversation_config_override": {
    "agent": {
      "first_message": "Hello Stefan! I see you're a premium customer. How can I assist you today?"
    }
  }
}
```

---

#### Best Practices

✅ **DO**:
- Keep default simple (AgenticMemory handles personalization)
- Test both new and returning caller scenarios
- Monitor name extraction accuracy
- Verify greeting sounds natural
- Check context relevance

✗ **DON'T**:
- Hardcode names or specific details
- Make first message too long (>20 words)
- Mention technical terms ("checking database")
- Promise things you can't deliver
- Sound robotic or scripted

---

### 4. Disable Interruptions During First Message

**What**: Prevents caller from speaking during opening message  
**Why**: Ensures important information is delivered completely  
**Who**: All callers  
**When**: During the first message only

**Recommended Setting for AgenticMemory**:
```
☐ UNCHECKED (Allow interruptions)
```

**Why Allow Interruptions**:
- Caller urgency respected
- Natural conversation flow
- Better user experience
- If they interrupt, they're engaged

**When to Enable**:
- Legal disclaimers required
- Critical safety information
- Multi-step instructions must be heard
- Recording consent notification

**Use Cases**:
- **Emergency Services**: ✓ Enable (ensure instructions heard)
- **Customer Support**: ✗ Disable (let them interrupt)
- **Sales**: ✗ Disable (engagement > script)
- **Healthcare**: ✓ Enable (HIPAA consent required)

**AgenticMemory Impact**:
Since first message is personalized ("Hello Stefan!"), interruptions are fine - it's just a greeting, not critical information.

**Best Practice**:
- Default to disabled (allow interruptions)
- Only enable for legally required content
- Keep first message short if enabled
- Test user experience both ways

---

### 5. System Prompt

**What**: Core instructions that define agent personality and behavior  
**Why**: Sets context, rules, knowledge scope, and response style  
**Who**: Affects all agent responses  
**When**: Applied to every LLM call throughout conversation

**⚠️ CRITICAL FOR AGENTICMEMORY**: 
The System Prompt is **ENHANCED** by ClientData endpoint with caller-specific memory context!

**Recommended Structure**:
```
# Role Definition
You are a [role] for [company], specialized in [domain].

# Personality Traits
- Friendly and professional
- Patient and empathetic
- Clear and concise

# Knowledge & Capabilities
- You have access to caller history through the Search Memory tool
- You can retrieve past conversations and preferences
- Use this context to personalize responses

# Rules & Constraints
- Never make up information
- Always verify user identity for sensitive topics
- Escalate complex issues to human support

# Response Guidelines
- Keep responses under 3 sentences
- Ask clarifying questions when needed
- Confirm understanding before taking action

# Memory Usage
When you have access to caller information:
- Reference past interactions naturally
- Don't mention you're "checking memory" - just know it
- Use their name if available
```

---

#### What AgenticMemory Adds to Your System Prompt (ACTUAL CODE OUTPUT)

The ClientData endpoint (`src/client_data/handler.py`) automatically prepends caller context to your system prompt.

**Example 1: Returning Caller with Rich History**
```
CALLER CONTEXT:
This caller has 15 previous interactions.
Known information:
- User name is Stefan
- User prefers email communication
- User has premium account
- User reported email access issue on 2024-09-15
- User's timezone is EST

Previous conversation highlights:
- User called about password reset
- User inquired about premium features
- User requested billing statement

First Message Override: Hello Stefan! I see you're a premium customer. How can I assist you today?

Instructions: Use this context to personalize your responses. Reference past conversations naturally.

[Your System Prompt appears here]
```

**Example 2: New Caller (No History)**
```
NEW CALLER: This is their first interaction. Focus on building rapport and gathering information.

[Your System Prompt appears here]
```

**Example 3: Returning Caller (Limited History)**
```
CALLER CONTEXT:
This caller has 3 previous interactions.
Known information:
- User needs help with account setup
- User called on 2024-10-01

First Message Override: Hello! How can I assist you today?

Instructions: Use this context to personalize your responses. Reference past conversations naturally.

[Your System Prompt appears here]
```

---

#### Memory Context Structure (From Code)

The context is built in this order by `lambda_handler()`:

1. **Header**: "CALLER CONTEXT:" (if memories exist) or "NEW CALLER:" (if no memories)
2. **Memory Count**: "This caller has X previous interactions"
3. **Factual Memories** (up to 5):
   ```
   Known information:
   - User name is Stefan
   - User has premium account
   - User prefers email updates
   ```
4. **Semantic Memories** (up to 3):
   ```
   Previous conversation highlights:
   - User called about password reset
   - User inquired about billing
   ```
5. **First Message Override**: The personalized greeting
6. **Instructions**: Guidance on using the context

---

#### Dynamic Variables in System Prompt

You can reference AgenticMemory variables anywhere in your prompt:

```
You are assisting {{caller_name}}. 
They are a {{returning_caller}} caller with {{memory_count}} previous interactions.
Key context: {{memory_summary}}
```

**Available Variables**:
- `{{caller_id}}` - Always present (phone number)
- `{{caller_name}}` - Conditional (extracted from memories)
- `{{memory_count}}` - Always present (number of memories)
- `{{memory_summary}}` - Always present (first factual memory or "New caller")
- `{{returning_caller}}` - Always present ("yes" or "no")

---

#### Quick System Prompt Examples

**Customer Support (Basic)**:
```
You are a customer support agent for TechCo.
Be patient and solution-focused.
Use the Search Memory tool to check previous issues, account status, and preferences.
Always verify identity before discussing account details.
Keep responses under 3 sentences.
```

**Sales (Basic)**:
```
You are a sales consultant for Acme Corp.
Be consultative, not pushy.
Use Search Memory to understand previous inquiries, products viewed, and budget discussed.
Focus on solving their problem, not selling products.
Ask permission before making recommendations.
```

**Healthcare (Basic)**:
```
You are a medical receptionist for HealthClinic.
Be HIPAA compliant - NEVER discuss medical conditions without verification.
Use Search Memory to check appointment preferences, insurance, and special needs.
Verify identity with name, DOB, and address before any account discussion.
```

**Hospitality (Basic)**:
```
You are a concierge for Grand Hotel.
Be anticipatory and detail-oriented.
Use Search Memory to personalize based on room preferences, dietary restrictions, and past bookings.
Reference past stays naturally: "I remember you enjoyed the spa last time..."
Make guests feel recognized and valued.
```

---

#### 📚 Complete System Prompt Examples

For comprehensive, production-ready system prompts with detailed conversation flows, escalation criteria, and industry-specific guidelines, see:

**[SYSTEM_PROMPT_EXAMPLES.md](SYSTEM_PROMPT_EXAMPLES.md)**

This file includes 8 complete examples:
1. **Customer Support** (Comprehensive) - 150+ lines with verification protocols, escalation criteria, example dialogues
2. **Sales Assistant** (Consultative) - Qualification questions, objection handling, ROI discussions
3. **Healthcare Receptionist** (HIPAA-Compliant) - Strict compliance rules, what you can/cannot discuss
4. **Hotel Concierge** (Anticipatory Service) - VIP treatment, special occasions, insider recommendations
5. **Technical Support** (Expert Troubleshooter) - Systematic troubleshooting, technical communication
6. **E-commerce Support** - Order tracking, returns, shipping issues
7. **Financial Services** - Security protocols, fraud handling, compliance
8. **Real Estate Agent** - Property qualification, market insights, buyer/seller flows

---

#### Best Practices for System Prompts

✅ **DO**:
- Be specific about role and domain
- Include clear escalation criteria
- Provide example responses (good vs bad)
- Define boundaries and constraints
- Reference memory usage explicitly
- Keep it under 800 words (500-600 optimal)
- Use clear section headers
- Test with new AND returning callers

✗ **DON'T**:
- Make it too long (>1000 words - LLM may ignore later parts)
- Include fake examples not in knowledge base
- Try to override AgenticMemory context (it's prepended automatically)
- Mention internal tools/systems to users ("checking database")
- Use ambiguous language
- Forget to define what NOT to do

---

#### System Prompt Template

```
# ROLE & IDENTITY
You are [name], a [role] for [company].
[Brief description of expertise/experience]

# PERSONALITY & TONE
- [Trait 1]
- [Trait 2]
- [Trait 3]

# YOUR CAPABILITIES
1. Automatic memory context (prepended to this prompt)
2. Search Memory tool for specific queries
3. [Domain-specific capability]
4. [Domain-specific capability]

# CONVERSATION FLOW
1. [Step 1]
2. [Step 2]
3. [Step 3]

# USING MEMORY CONTEXT
- Reference naturally: "[example]"
- Don't say: "[bad example]"
- Do say: "[good example]"
- Use search_memory for [specific scenarios]

# RESPONSE GUIDELINES
- [Guideline 1]
- [Guideline 2]
- [Guideline 3]

# CONSTRAINTS
- Never [constraint 1]
- Never [constraint 2]
- Always [requirement 1]

# ESCALATION CRITERIA
Transfer to [role] when:
- [Scenario 1]
- [Scenario 2]
- [Scenario 3]

# EXAMPLE RESPONSES
Good: "[example]"
Bad: "[counter-example]"
```

---

#### Testing Your System Prompt

1. **New Caller Test**: Test with phone number that has no memories
   - Prompt should handle lack of context gracefully
   - Agent should focus on information gathering

2. **Returning Caller Test**: Test with phone number that has rich history
   - Agent should reference memories naturally
   - Context should influence responses

3. **Edge Cases**:
   - Angry customer with complaint history
   - Confused user asking off-topic questions
   - User requesting information you don't have
   - Security-sensitive requests

4. **Monitor For**:
   - Hallucinations (making up information)
   - Ignoring memory context
   - Overly verbose responses
   - Not following escalation criteria
   - Mentioning technical terms ("database", "system")

5. **Iterate Based On**:
   - Conversation logs analysis
   - Customer satisfaction scores
   - Escalation rate
   - Resolution time
   - Common failure patterns

---

### 6. Ignore Default Personality

**What**: Removes ElevenLabs' base personality traits  
**Why**: Gives you complete control over agent behavior  
**Who**: Affects all responses  
**When**: Enable if you want pure custom behavior

**Recommended Setting for AgenticMemory**:
```
☐ UNCHECKED (Keep default personality)
```

**Default Personality Includes**:
- Helpful and friendly tone
- Professional demeanor
- Clear communication style
- Appropriate social cues

**Why Keep It**:
- Good baseline behavior
- Handles edge cases well
- Consistent tone
- Less prompt engineering needed

**When to Enable**:
- Highly specialized personas (e.g., Shakespearean tutor)
- Brand-specific voice very different from default
- Character-based agents (e.g., game NPCs)
- Research/testing specific behaviors

**Use Cases**:

**Keep Default (Recommended)**:
- Customer support
- Sales agents
- Healthcare assistants
- General business use

**Ignore Default**:
- Entertainment characters
- Educational personas (strict teacher, friendly tutor)
- Brand mascots
- Experimental agents

**Best Practice**:
- Start with default enabled
- Only ignore if default conflicts with your needs
- Test extensively if ignoring
- Document why you chose to ignore

---

### 7. Dynamic Variables

**What**: Placeholders that get replaced with actual values at runtime  
**Why**: Personalize prompts and messages without hardcoding  
**Who**: All callers, individual values per call  
**When**: Replaced at conversation start and updated during call

**How AgenticMemory Uses This**:

The ClientData endpoint provides these variables automatically:

| Variable | Always Present | Example | Description |
|----------|---------------|---------|-------------|
| `{{caller_id}}` | ✅ Yes | `+16129782029` | Phone number |
| `{{memory_count}}` | ✅ Yes | `15` | Number of memories |
| `{{memory_summary}}` | ✅ Yes | `User prefers email` | Key fact |
| `{{returning_caller}}` | ✅ Yes | `yes` / `no` | Has memories? |
| `{{caller_name}}` | ⚠️ Conditional | `Stefan` | If found in memories |

**Usage in System Prompt**:
```
You are assisting {{caller_name}}.
[If caller_name not present, this shows as empty]

This caller has {{memory_count}} previous interactions.
[Shows actual number]

Returning caller: {{returning_caller}}
[Shows "yes" or "no"]
```

**Usage in First Message**:
```
Hello{{#if caller_name}} {{caller_name}}{{/if}}! 
How can I help you today?

Result: 
- With name: "Hello Stefan! How can I help you today?"
- Without: "Hello! How can I help you today?"
```

**Custom Variables via Tools**:
Your custom tools can also update variables during the call:
```javascript
// Tool response can include variable updates
{
  "result": "Order status retrieved",
  "variables": {
    "order_status": "Shipped",
    "tracking_number": "1Z999AA10123456784"
  }
}

// Now available as {{order_status}} and {{tracking_number}}
```

**Best Practices**:
✅ **DO**:
- Use conditional syntax for optional variables
- Test with and without each variable
- Provide defaults for missing variables
- Document which tools update which variables

✗ **DON'T**:
- Assume variables always exist
- Use variables without fallbacks
- Hardcode values that could be dynamic
- Expose internal variable names to users

**Advanced Usage**:
```
System Prompt:
"""
You are assisting {{caller_name|default:"a valued customer"}}.

{{#if returning_caller == "yes"}}
Welcome back! I see you have {{memory_count}} previous interactions.
{{else}}
Welcome! This is your first time contacting us.
{{/if}}

Context: {{memory_summary|default:"No previous history available"}}
"""
```

---

### 8. LLM Selection

**What**: AI model that powers agent responses  
**Why**: Different models have different strengths, speeds, costs  
**Who**: Affects all agent responses  
**When**: Choose at agent creation, can change anytime

**Recommended Setting for AgenticMemory**:
```
Gemini 2.0 Flash (001) - RECOMMENDED
OR
GPT-4o (for more complex reasoning)
```

**Available Models** (as of Oct 2025):

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| **Gemini 2.0 Flash** | ⚡⚡⚡ Fast | ⭐⭐⭐ Good | 💰 Low | Customer support, general use |
| **GPT-4o** | ⚡⚡ Medium | ⭐⭐⭐⭐ Excellent | 💰💰 Medium | Complex queries, technical support |
| **Claude 3.5 Sonnet** | ⚡⚡ Medium | ⭐⭐⭐⭐ Excellent | 💰💰 Medium | Long conversations, reasoning |
| **GPT-4o Mini** | ⚡⚡⚡ Fast | ⭐⭐ Fair | 💰 Very Low | Simple tasks, high volume |

**Why Gemini 2.0 Flash**:
- ✅ Fast responses (low latency)
- ✅ Good quality for most use cases
- ✅ Cost-effective for high call volumes
- ✅ Works well with AgenticMemory's memory context
- ✅ ElevenLabs recommended for conversational AI

**When to Use GPT-4o**:
- Complex technical support
- Multi-step reasoning required
- Medical/legal advice (with proper disclaimers)
- High-stakes conversations
- Deep analysis of conversation history

**When to Use Claude 3.5 Sonnet**:
- Very long conversations (maintains context well)
- Nuanced emotional intelligence needed
- Creative problem-solving
- Ethical reasoning scenarios

**Fallback Behavior**:
If your chosen LLM is unavailable, ElevenLabs automatically redirects to another model. This ensures no calls fail due to LLM outages.

**AgenticMemory Compatibility**:
All models work well with AgenticMemory's memory context. Key considerations:

- **Context Window**: All support large contexts (memories + prompt)
- **Tool Calling**: All support calling the Search Memory tool
- **Speed**: Faster models provide better user experience
- **Cost**: Balance quality vs. call volume costs

**Cost Example** (1000 calls, 5 min avg):
```
Gemini Flash: ~$50/month
GPT-4o: ~$200/month
Claude Sonnet: ~$180/month
GPT-4o Mini: ~$20/month
```

**Best Practice**:
1. Start with Gemini 2.0 Flash
2. Monitor conversation quality in Analysis tab
3. Upgrade to GPT-4o if needed for specific use cases
4. Use GPT-4o Mini only for very simple, high-volume scenarios

---

### 9. Temperature

**What**: Controls randomness/creativity in responses  
**Why**: Balance between consistent and creative responses  
**Who**: Affects all agent responses  
**When**: Set based on use case requirements

**Scale**: 0.0 (deterministic) to 1.0+ (creative)

**Recommended Settings**:

**Customer Support (0.3-0.5)** - RECOMMENDED FOR AGENTICMEMORY
```
Temperature: 0.4
Why: Consistent, professional, reliable responses
```

**Sales (0.5-0.7)**
```
Temperature: 0.6
Why: Engaging, persuasive, but still coherent
```

**Creative/Entertainment (0.7-1.0)**
```
Temperature: 0.8
Why: Varied, interesting, unpredictable responses
```

**Technical Support (0.2-0.4)**
```
Temperature: 0.3
Why: Precise, factual, consistent instructions
```

**What Each Setting Does**:

**Temperature 0.2 (Deterministic)**:
```
User: "What's your return policy?"
Agent: "Our return policy allows returns within 30 days of purchase with original receipt."
[Same answer every time]
```

**Temperature 0.5 (Balanced)** - RECOMMENDED:
```
User: "What's your return policy?"
Agent responses vary:
- "We accept returns within 30 days with a receipt."
- "You can return items within 30 days of purchase."
- "Our return window is 30 days from your purchase date."
[Similar but slightly varied]
```

**Temperature 0.9 (Creative)**:
```
User: "What's your return policy?"
Agent responses highly varied:
- "Great question! We've got a flexible 30-day return policy..."
- "Returns? No problem! We give you a full month..."
- "Absolutely! We want you to be happy, so we offer 30 days..."
[Very different styles and embellishments]
```

**Quick Presets**:
```
Deterministic: 0.3
Creative: 0.6
More Creative: 0.9
```

**AgenticMemory Considerations**:

With memory context, lower temperatures work better because:
- Agent has specific facts to work with (memories)
- Consistency is valued in customer service
- Less hallucination risk
- More predictable behavior

**Best Practice**:
- Start at 0.4 for customer service
- Lower (0.2-0.3) for technical/medical
- Higher (0.6-0.7) for sales/entertainment
- Monitor for:
  - Too low: Robotic, repetitive
  - Too high: Inconsistent, unpredictable
  - Just right: Natural but reliable

**Testing**:
Run same query 10 times at different temperatures:
- 0.2: Nearly identical responses
- 0.5: Similar meaning, varied phrasing
- 0.9: Different approaches entirely

Choose based on which feels most appropriate for your brand.

---

### 10. Limit Token Usage

**What**: Maximum tokens LLM can generate per response  
**Why**: Control response length and costs  
**Who**: Affects all agent responses  
**When**: Set to prevent overly long responses

**Recommended Setting for AgenticMemory**:
```
-1 (No limit)
OR
150-200 tokens (for concise responses)
```

**Token Guidelines**:
```
~1 token = ~0.75 words

Token Limits:
50 tokens = ~35 words = 1-2 short sentences
100 tokens = ~75 words = 2-3 sentences (RECOMMENDED)
200 tokens = ~150 words = 4-5 sentences (verbose)
500 tokens = ~375 words = Full paragraph (too long for phone)
-1 = No limit (use with caution)
```

**Why Limit Tokens**:
✅ **Shorter responses are better for voice**:
- Easier to understand
- Caller can interrupt sooner
- Natural conversation rhythm
- Lower latency

**When to Use -1 (No Limit)**:
- Initial setup/testing
- Complex technical explanations needed
- Legal/medical disclosures required
- You trust your system prompt to keep it brief

**When to Set Limit**:
- Customer service (100-150 tokens)
- Sales calls (150-200 tokens)
- Simple Q&A (50-100 tokens)
- Cost optimization needed

**AgenticMemory Impact**:

With memory context, responses can get longer:
```
Without memory (50 tokens):
"I can help you with that. What's your account number?"

With memory (120 tokens):
"Hi Stefan! I see you called last week about email access issues. 
I'm glad to help you again today. Are you still experiencing 
the same problem, or is this about something different?"
```

**Cost Impact**:
```
No limit: Variable cost, risk of runaway tokens
100 token limit: Predictable cost, $0.0001 per response (GPT-4o)
500 token limit: Higher but capped cost
```

**Best Practice**:
```
1. Start with -1 (no limit)
2. Monitor actual token usage in first 100 calls
3. Set limit to 90th percentile + 20%
4. Add to system prompt: "Keep responses under 3 sentences"
```

**System Prompt Enhancement**:
```
Response Guidelines:
- Keep responses concise (under 3 sentences)
- One main point per response
- Ask follow-up questions to clarify
- Break complex answers into multiple turns
```

**Monitoring**:
Check Analysis tab for:
- Average tokens per response
- Longest responses
- Conversations that hit limit
- User satisfaction correlation

---

### 11. Agent Knowledge Base

**What**: Documents that provide domain-specific information  
**Why**: Ground agent in factual, current information  
**Who**: All callers benefit from accurate information  
**When**: Upload before agent goes live, update regularly

**Recommended for AgenticMemory**:
```
Upload:
1. Product documentation
2. Company policies
3. FAQ document
4. Troubleshooting guides
5. Pricing information
```

**What to Upload**:

**Essential Documents**:
```
✅ Product/Service Catalog
✅ Pricing & Plans
✅ Return/Refund Policies
✅ Shipping Information
✅ Warranty Terms
✅ Contact Information
✅ Hours of Operation
✅ Common Issues & Solutions
```

**Format Support**:
- PDF
- TXT
- DOCX
- Markdown
- HTML

**Size Limits**:
- Max file size: 10MB per document
- Max total: 100MB per agent
- Optimal: 10-20 focused documents

**How It Works with AgenticMemory**:

```
Knowledge Base → Static company information
AgenticMemory → Dynamic caller-specific information

Example:
Knowledge Base: "Our premium plan costs $99/month"
AgenticMemory: "Stefan has premium plan, signed up June 2024"

Agent combines both:
"Hi Stefan! Your premium plan ($99/month) that you signed up 
for in June is coming up for renewal next month."
```

**Best Practices**:

✅ **DO**:
- Keep documents current (review monthly)
- Use clear headings and structure
- Include examples and scenarios
- Version control your documents
- Test agent after each update

✗ **DON'T**:
- Upload entire website content
- Include outdated information
- Duplicate information across documents
- Upload personal customer data (use AgenticMemory instead)
- Include contradictory information

**Document Structure Example**:
```markdown
# Return Policy

## Timeline
- 30 days from purchase date
- Must have original receipt

## Conditions
- Item in original condition
- Original packaging preferred
- All accessories included

## Process
1. Contact customer service
2. Receive RMA number
3. Ship item back
4. Refund processed in 5-7 days

## Exceptions
- Opened software (no returns)
- Personalized items (no returns)
- Sale items (store credit only)
```

**Integration with Search Memory Tool**:
```
User: "What's your return policy?"

Agent flow:
1. Check Knowledge Base → Find return policy document
2. Check AgenticMemory → Search "return" in caller history
3. Combine: "Our return policy is 30 days. I see you asked 
   about this last month for your previous order - did you 
   receive that refund successfully?"
```

**Updating Strategy**:
```
Weekly: Price changes, promotions
Monthly: Policy updates, new products
Quarterly: Full document review
Annually: Complete knowledge base audit
```

**Testing**:
After uploading documents:
1. Ask agent specific questions from documents
2. Verify accurate information
3. Check for hallucinations (agent making things up)
4. Test edge cases not covered in documents
5. Monitor for "I don't know" responses

---

### 12. Tools

Tools give your agent the ability to perform specific actions during conversations.

#### Built-in Tools

**12.1 End Call**

**What**: Agent can terminate the conversation  
**Why**: Allows natural conversation endings  
**Who**: Agent decides when appropriate  
**When**: Conversation complete, user satisfied, or abuse detected

**Recommended Setting for AgenticMemory**:
```
✅ ENABLED
```

**How It Works**:
```
User: "Thanks, that's all I needed!"
Agent: "Great! Have a wonderful day. Goodbye!"
[Agent calls end_call tool]
[Call disconnects]
```

**When Agent Uses It**:
- User explicitly ends conversation ("That's all, thanks")
- Issue resolved and confirmed
- User requests to end call
- Abuse/spam detected
- Caller unresponsive after multiple prompts

**System Prompt Guidance**:
```
You can end the call when:
- User explicitly says goodbye or thanks
- You've confirmed the issue is resolved
- User indicates they have no more questions

Always:
- Summarize what was accomplished
- Offer future assistance
- Say a polite goodbye
- Then end the call
```

**Best Practice**:
- Enable for all agents
- Don't end prematurely
- Always confirm satisfaction first
- Log reason for ending in conversation metadata

---

**12.2 Detect Language**

**What**: Agent can identify and switch to caller's language  
**Why**: Supports multilingual callers automatically  
**Who**: Callers speaking non-default languages  
**When**: Agent detects non-default language being spoken

**Recommended Setting for AgenticMemory**:
```
✅ ENABLED (if Additional Languages configured)
☐ DISABLED (if English-only)
```

**How It Works**:
```
User: [Speaks in Spanish]
Agent: [Detects Spanish, switches language]
Agent: "Hola! Puedo ayudarte en español. ¿Cómo puedo ayudarte?"
```

**Requirements**:
- Additional Languages must be configured in Agent tab
- Voice must support target language
- System prompt should address multilingual behavior

**AgenticMemory Behavior**:
- Memories stored regardless of language
- Search Memory tool works across languages (with limitations)
- Caller preferences can include language preference

**System Prompt Addition**:
```
Language Support:
- Detect if user is speaking a non-English language
- Switch to their language if available
- If not available, politely explain English-only limitation
- Store language preference for future calls
```

**Best Practice**:
- Only enable if you truly support the language
- Test thoroughly in each language
- Consider separate agents for major languages (better quality)
- Store detected language as memory for future calls

---

**12.3 Skip Turn**

**What**: Agent pauses to let user gather thoughts  
**Why**: Natural conversation flow when user needs a moment  
**Who**: Users who explicitly request time  
**When**: User says "hold on", "one moment", "let me think"

**Recommended Setting for AgenticMemory**:
```
✅ ENABLED
```

**How It Works**:
```
User: "Wait, let me find that receipt... hold on a second"
Agent: [Uses skip_turn tool]
Agent: [Silent, waits for user]
User: "Okay, found it! The order number is..."
Agent: "Perfect! Let me look that up."
```

**Trigger Phrases**:
- "Hold on"
- "Wait a second"
- "Let me check"
- "One moment"
- "Give me a minute"

**Why Enable**:
- More natural conversation
- Less interruption of user's flow
- Better user experience
- Reduces frustration

**System Prompt Guidance**:
```
If user indicates they need a moment:
- Use skip_turn tool immediately
- Don't speak while they're looking for something
- Wait for them to resume
- Don't apologize excessively when they return
```

**Best Practice**:
- Always enable (no downside)
- Don't overuse (agent shouldn't suggest pauses)
- Keep silence comfortable (not awkward)
- Resume naturally when user speaks

---

**12.4 Transfer to Agent**

**What**: Transfer call to another AI agent  
**Why**: Specialized agents for different departments  
**Who**: Callers needing different expertise  
**When**: Current agent can't help, different department needed

**Recommended Setting for AgenticMemory**:
```
☐ DISABLED (unless multi-agent setup)
✅ ENABLED (if you have specialized agents)
```

**Use Cases**:

**Multi-Agent Setup**:
```
General Agent → Transfer to:
├── Sales Agent (for quotes/purchases)
├── Technical Support Agent (for troubleshooting)
├── Billing Agent (for payment issues)
└── Returns Agent (for returns/refunds)
```

**How It Works**:
```
User: "I need help with a technical issue"
Agent: "I'll transfer you to our technical support specialist 
        who can better assist you."
[Calls transfer_to_agent tool with target agent ID]
[Call transfers, context preserved]
Technical Agent: "Hi! I understand you're having a technical 
                  issue. What's happening?"
```

**AgenticMemory Considerations**:
- All agents share same AgenticMemory backend
- Memories available to all agents
- Transfer reason can be stored as memory
- Agent handoff logged for analysis

**Configuration**:
```
System Prompt for General Agent:
Transfer to specialized agents when:
- Sales inquiries → Sales Agent (agent_id_sales)
- Technical problems → Tech Agent (agent_id_tech)
- Billing questions → Billing Agent (agent_id_billing)

Always:
- Explain why transferring
- Summarize issue for new agent
- Confirm user consent
```

**Best Practice**:
- Use for complex organizations only
- Consider if one smart agent could handle all cases
- Minimize transfers (frustrating for users)
- Preserve context across transfers
- Log transfer reasons for optimization

**When to Skip**:
- Small businesses (one agent is enough)
- Simple support (no specialization needed)
- Low call volume
- Cost concerns (multiple agents = more cost)

---

**12.5 Transfer to Number**

**What**: Transfer call to a human operator  
**Why**: Human intervention needed  
**Who**: Callers with complex issues, escalations  
**When**: AI cannot resolve, user requests human

**Recommended Setting for AgenticMemory**:
```
✅ ENABLED (with configured transfer numbers)
```

**Configuration Required**:
```
Transfer Numbers:
- Support: +1-555-0100
- Sales: +1-555-0101
- Billing: +1-555-0102
- Manager: +1-555-0103
```

**Use Cases**:

**Escalation Scenarios**:
- Angry/frustrated customer
- Complex technical issue
- Payment disputes
- Legal questions
- Medical emergencies
- Security concerns

**How It Works**:
```
User: "This isn't working! I need to speak to a person!"
Agent: "I understand your frustration. Let me transfer you 
        to a specialist who can help immediately."
[Calls transfer_to_number with support number]
[Call transfers to human]
```

**AgenticMemory Integration**:
```
Before Transfer:
1. Store conversation summary in memory
2. Note reason for transfer
3. Pass caller_id to human (they can check memories too)

After Transfer:
1. Human's notes added as memory
2. Resolution stored for future reference
3. Agent learns from escalation patterns
```

**System Prompt Guidance**:
```
Transfer to human when:
- User explicitly requests: "I want to talk to a person"
- Issue is too complex for AI
- User is frustrated/angry
- Sensitive topics (medical, legal, financial)
- You've attempted 3+ unsuccessful resolution attempts

Transfer Process:
1. Acknowledge user's need
2. Summarize their issue
3. Explain what specialist will help
4. Initiate transfer
5. Stay on line until transfer connects (if possible)
```

**Best Practice**:
✅ **DO**:
- Set clear transfer criteria
- Provide context to human
- Make transfer seamless
- Log transfer reasons
- Review transfer patterns monthly

✗ **DON'T**:
- Transfer too quickly (try to help first)
- Transfer without explanation
- Lose conversation context
- Make user repeat everything
- Transfer to wrong department

**Transfer Criteria by Severity**:
```
Immediate Transfer:
- Emergency situations
- Threats/abuse
- Legal demands
- Security breaches

Quick Transfer (1-2 attempts):
- Frustrated customers
- Payment disputes
- Account access issues

Standard Transfer (3+ attempts):
- Complex technical issues
- Policy clarifications
- Special requests
```

---

**12.6 Play Keypad Touch Tone**

**What**: Generate DTMF tones during call  
**Why**: Interact with IVR systems, voicemail, automated systems  
**Who**: Users needing to navigate phone menus  
**When**: Agent must interact with another phone system

**Recommended Setting for AgenticMemory**:
```
☐ DISABLED (most use cases don't need this)
✅ ENABLED (if calling through IVR systems)
```

**Use Cases**:

**When Needed**:
- Transferring through company IVR
- Leaving voicemails with extensions
- Conference call systems
- Automated appointment systems

**How It Works**:
```
Agent: "I'll dial the extension for you."
[Calls play_keypad_touch_tone with "1234"]
[DTMF tones play: 1, 2, 3, 4]
IVR: "Connecting to extension 1234..."
```

**AgenticMemory Integration**:
Limited - this is a phone system interaction, not memory-related.

**Best Practice**:
- Disable unless specifically needed
- Test thoroughly with target systems
- Verify tone duration/spacing
- Have fallback plan if DTMF fails

**When to Skip**:
- Direct calls to users
- No IVR navigation needed
- Simple support scenarios
- Inbound-only calls

---

**12.7 Voicemail Detection**

**What**: Detect when call goes to voicemail and optionally leave message  
**Why**: Handle missed calls professionally  
**Who**: Outbound calls that reach voicemail  
**When**: Making outbound calls, call not answered

**Recommended Setting for AgenticMemory**:
```
☐ DISABLED (for inbound support)
✅ ENABLED (for outbound sales/reminders)
```

**How It Works**:
```
[Agent calls customer]
[Voicemail detected]
Agent: [Leaves message]
"Hi, this is Sarah from Acme Support. I'm calling regarding 
your inquiry about our premium plan. Please call us back at 
1-555-0100. Thank you!"
[Hangs up after message]
```

**Configuration**:
```
Voicemail Message Template:
"Hello, this is [Agent Name] from [Company]. 
I'm calling regarding [reason]. 
Please call us back at [phone number]. 
Thank you!"
```

**AgenticMemory Integration**:
```
After Voicemail:
- Store: "Voicemail left on [date] regarding [topic]"
- Track: Number of voicemail attempts
- Schedule: Retry logic based on voicemail count
```

**Best Practice**:
- Keep message under 20 seconds
- Include callback number
- State reason for call
- Don't sound robotic
- Leave only 1-2 voicemails maximum

**When to Enable**:
- Outbound sales calls
- Appointment reminders
- Follow-up calls
- Customer outreach

**When to Disable**:
- Inbound support only
- No outbound calling
- Text/email preferred
- High volume automated dialing

---

#### 12.8 Custom Tools

**What**: Your own API endpoints the agent can call  
**Why**: Extend agent capabilities beyond built-in tools  
**Who**: Developers integrating external systems  
**When**: Need to fetch data, perform actions, update systems

**🎯 CRITICAL FOR AGENTICMEMORY**: This is where you add the **Search Memory** tool!

**Recommended Custom Tools for AgenticMemory**:

**Tool #1: Search Memory (REQUIRED)**
```json
{
  "name": "search_memory",
  "description": "Search the caller's conversation history and preferences. Use this to recall past interactions, preferences, or previous issues discussed.",
  "url": "https://zv39o5dkzi.execute-api.us-east-1.amazonaws.com/Prod/retrieve",
  "method": "POST",
  "parameters": [
    {
      "name": "query",
      "type": "string",
      "required": true,
      "description": "Natural language search query (e.g., 'last issue', 'preferences', 'previous order')"
    },
    {
      "name": "user_id",
      "type": "string",
      "required": true,
      "description": "Caller's phone number",
      "default": "{{caller_id}}"
    },
    {
      "name": "limit",
      "type": "integer",
      "required": false,
      "description": "Maximum number of results",
      "default": 10
    }
  ],
  "authentication": "none"
}
```

**When Agent Uses It**:
```
User: "What was my last issue about?"
Agent: [Calls search_memory with query="last issue"]
Response: {"memories": [{"memory": "User reported email access problem"}]}
Agent: "I see your last issue was about email access problems. Is this related?"
```

**Additional Custom Tool Examples**:

**Tool #2: Check Order Status**
```json
{
  "name": "check_order_status",
  "description": "Look up the status of a customer's order",
  "url": "https://api.yourcompany.com/orders/status",
  "method": "POST",
  "parameters": [
    {
      "name": "order_number",
      "type": "string",
      "required": true,
      "description": "The order number to look up"
    }
  ],
  "authentication": "bearer_token"
}
```

**Tool #3: Schedule Appointment**
```json
{
  "name": "schedule_appointment",
  "description": "Schedule an appointment for the caller",
  "url": "https://api.yourcompany.com/appointments",
  "method": "POST",
  "parameters": [
    {
      "name": "date",
      "type": "string",
      "required": true,
      "description": "Appointment date (YYYY-MM-DD)"
    },
    {
      "name": "time",
      "type": "string",
      "required": true,
      "description": "Appointment time (HH:MM)"
    },
    {
      "name": "service",
      "type": "string",
      "required": true,
      "description": "Type of service needed"
    }
  ]
}
```

**Tool Design Best Practices**:

✅ **DO**:
- Clear, descriptive names
- Detailed description (agent uses this to decide when to call)
- Required vs. optional parameters
- Use {{caller_id}} for automatic user context
- Return structured JSON
- Handle errors gracefully
- Include success/failure indicators

✗ **DON'T**:
- Vague names ("tool1", "helper")
- Missing descriptions
- Too many parameters (max 5)
- Return HTML or unstructured text
- Assume parameters will be perfect
- Forget authentication
- Make breaking changes without versioning

**System Prompt for Tool Usage**:
```
You have access to these tools:

search_memory:
- Use whenever user references past interactions
- Use to check preferences before suggesting solutions
- Use to avoid asking questions user already answered

When to use:
- User: "What did we discuss last time?" → search_memory
- User: "What's my usual order?" → search_memory  
- User: "You have my address, right?" → search_memory

How to use:
- Be specific in queries: "last issue" not "history"
- Check memory before asking repeated questions
- Reference memories naturally, don't say "checking my database"
```

**Error Handling**:
```
If tool fails:
- Apologize briefly: "I'm having trouble accessing that information"
- Offer alternative: "Can you tell me about your last interaction?"
- Don't retry repeatedly (max 2 attempts)
- Transfer to human if critical
```

**AgenticMemory Search Memory Integration**:
```
Conversation Flow Example:

User: "Hi, I'm calling about an issue"
Agent: [Automatically has memories from ClientData]
Agent: "Hello Stefan! I see you called last week. Is this about 
        the same email access issue?"

User: "No, different problem with billing"
Agent: [Calls search_memory("billing issues")]
Response: {"memories": [{"memory": "User disputed charge on 3/15"}]}
Agent: "I see you had a question about a charge in March. 
        Is this related to that?"

User: "Actually yes, same charge"
Agent: "Let me pull up that information. The $49.99 charge 
        you disputed was reversed on 3/20. Are you seeing 
        a similar charge now?"
```

**Testing Custom Tools**:
1. Test tool endpoint independently (use curl/Postman)
2. Test with agent in sandbox
3. Try edge cases (missing params, errors, timeouts)
4. Monitor tool call logs
5. Optimize based on usage patterns

---

This is Part 1 of the configuration guide. Due to length, I'll continue with the remaining sections in the next part.

**Next Sections**:
- Workflow Tab (Alpha)
- Voice Tab
- Analysis Tab
- Tests Tab (Alpha)
- Security Tab (CRITICAL for AgenticMemory webhooks)
- Advanced Tab
- Widget Tab
- Complete Integration Setup
- Best Practices & Recommendations

Would you like me to continue with the remaining sections?
