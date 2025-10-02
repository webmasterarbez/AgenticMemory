# AgenticMemory System Flow

## 📞 Complete Call Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INCOMING CALL                                    │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 1: CONVERSATION INITIATION (Pre-Call)                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ElevenLabs Agent  ──POST──►  Client Data Endpoint                       │
│                               (API Gateway)                               │
│  Sends:                            │                                     │
│  {                                 ▼                                     │
│    "caller_id": "+16129782029"   ClientDataFunction                      │
│  }                                 │ (Lambda)                            │
│                                    │                                     │
│                                    ▼                                     │
│                               Mem0 Cloud API                             │
│                               - Get all memories                         │
│                               - Extract caller name                      │
│                               - Generate greeting                        │
│                                    │                                     │
│                                    ▼                                     │
│  Agent receives:              Response:                                  │
│  - Memory context             {                                          │
│  - Personalized greeting        "type": "conversation_initiation...",   │
│  - Dynamic variables            "dynamic_variables": {                  │
│                                   "caller_id": "+16129782029",          │
│                                   "memory_count": "5"                    │
│                                 },                                       │
│                                 "conversation_config_override": {        │
│                                   "agent": {                             │
│                                     "first_message": "Hi Stefan! ..."   │
│                                   }                                      │
│                                 }                                        │
│                               }                                          │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 2: CONVERSATION IN PROGRESS (During Call)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Caller: "What's my favorite restaurant?"                                │
│          │                                                               │
│          ▼                                                               │
│  Agent thinks: Need to search memory                                     │
│          │                                                               │
│          ▼                                                               │
│  Agent calls memory_search tool                                          │
│          │                                                               │
│          │───POST───►  Retrieve Endpoint                                │
│                       (API Gateway)                                      │
│  Sends:                    │                                            │
│  {                         ▼                                            │
│    "query": "favorite      RetrieveFunction                             │
│     restaurant",           (Lambda)                                     │
│    "user_id":              │                                            │
│     "+16129782029"         ▼                                            │
│  }                    Mem0 Cloud API                                    │
│                       - Semantic search                                  │
│                       - Return top 3 results                             │
│                            │                                            │
│                            ▼                                            │
│  Agent receives:      Response:                                         │
│  - Relevant memories  {                                                 │
│  - Context            "memories": [                                     │
│                         {                                               │
│                           "memory": "Prefers Italian                    │
│                                      from Giuseppe's",                  │
│                           "score": 0.89                                 │
│                         }                                               │
│                       ]                                                 │
│                     }                                                   │
│          │                                                              │
│          ▼                                                              │
│  Agent: "You love Italian food from Giuseppe's Restaurant!"             │
│                                                                          │
│  [Conversation continues with context-aware responses...]               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 3: POST-CALL PROCESSING (After Call)                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Call Ends                                                               │
│     │                                                                    │
│     ▼                                                                    │
│  ElevenLabs ──POST+HMAC──►  Post-Call Endpoint                          │
│                             (API Gateway)                                │
│  Sends:                          │                                      │
│  {                               ▼                                      │
│    "conversation_id": "...",   PostCallFunction                         │
│    "caller_phone_number":      (Lambda)                                 │
│      "+16129782029",             │                                      │
│    "transcript": "...",          │                                      │
│    "transcript_with_             ▼                                      │
│      timestamps": [...]    1. Verify HMAC signature                     │
│  }                               │                                      │
│  Header:                         ▼                                      │
│  X-ElevenLabs-Signature    2. Return 200 OK immediately                 │
│                                  │                                      │
│  ◄──200 OK──                     ▼                                      │
│                            3. Process asynchronously:                    │
│                               - Extract factual info                     │
│                               - Store factual memory                     │
│                                 (names, preferences)                     │
│                                  │                                      │
│                                  ▼                                      │
│                               Mem0 Cloud API                             │
│                               client.add(                                │
│                                 messages=[transcript],                   │
│                                 user_id=caller_id,                       │
│                                 metadata={                               │
│                                   "type": "factual",                     │
│                                   "conversation_id": "..."               │
│                                 }                                        │
│                               )                                          │
│                                  │                                      │
│                                  ▼                                      │
│                               - Store semantic memory                    │
│                                 (full context)                           │
│                                  │                                      │
│                                  ▼                                      │
│                               Mem0 Cloud API                             │
│                               client.add(                                │
│                                 messages=[...],                          │
│                                 user_id=caller_id,                       │
│                                 metadata={                               │
│                                   "type": "semantic",                    │
│                                   "conversation_id": "..."               │
│                                 }                                        │
│                               )                                          │
│                                  │                                      │
│                                  ▼                                      │
│                            ✅ Memories stored!                           │
│                            Ready for next call                           │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Memory Lifecycle

```
┌────────────┐
│ First Call │
└─────┬──────┘
      │
      │ 1. Generic greeting (no memory)
      │ 2. Caller shares: "I'm Sarah, I love pizza"
      │ 3. Call ends
      │
      ▼
┌──────────────────┐
│ Post-Call Stores │
└─────┬────────────┘
      │
      │ Factual: "Name is Sarah", "Loves pizza"
      │ Semantic: Full conversation context
      │
      ▼
┌───────────────┐
│ Memory Index  │ (30-60 seconds)
└─────┬─────────┘
      │
      ▼
┌────────────────┐
│ Second Call    │
└─────┬──────────┘
      │
      │ 1. Pre-call retrieves memories
      │ 2. Personalized: "Hi Sarah! Great to hear from you!"
      │ 3. During call: Agent recalls "You love pizza"
      │ 4. New info shared: "I prefer thin crust"
      │
      ▼
┌──────────────────┐
│ Post-Call Updates│
└─────┬────────────┘
      │
      │ UPDATE: "Prefers thin crust pizza"
      │ ADD: New conversation context
      │
      ▼
┌────────────────┐
│ Richer Profile │
└────────────────┘
```

---

## 🔐 Security Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Authentication & Security                                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Client Data Endpoint:                                       │
│  ┌──────────────┐                                           │
│  │ X-Workspace- │ ──validate──► ✅ Authorized                │
│  │ Key Header   │              OR                            │
│  └──────────────┘               ❌ 401 Unauthorized          │
│                                                               │
│  Retrieve Endpoint:                                          │
│  ┌──────────────┐                                           │
│  │ No Auth      │ ──trusted──► ✅ ElevenLabs agent only     │
│  │ Required     │              (not public)                  │
│  └──────────────┘                                            │
│                                                               │
│  Post-Call Endpoint:                                         │
│  ┌──────────────────────┐                                   │
│  │ HMAC-SHA256          │                                   │
│  │ Signature            │                                   │
│  │                      │                                   │
│  │ 1. Extract timestamp │                                   │
│  │ 2. Compute HMAC      │                                   │
│  │ 3. Compare signature │──► ✅ Valid (process & store)    │
│  │ 4. Check time window │   OR                              │
│  └──────────────────────┘    ❌ Invalid (log & return 200)  │
│                              (Still 200 for ElevenLabs)     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow

```
┌──────────────┐
│  Mem0 Cloud  │
│   Storage    │
└──────┬───────┘
       │
       │ user_id: "+16129782029"
       │
       ├─► Factual Memories
       │   • "Name is Sarah"
       │   • "Loves pizza"
       │   • "Prefers thin crust"
       │   • "Orders from Giuseppe's"
       │   metadata: { type: "factual" }
       │
       └─► Semantic Memories
           • Full conversation #1
           • Full conversation #2
           • Full conversation #3
           metadata: { type: "semantic" }

┌─────────────────────────────────────┐
│  Memory Operations                  │
├─────────────────────────────────────┤
│                                     │
│  get_all(user_id)                   │
│  └─► Returns ALL memories           │
│      (used for pre-call context)    │
│                                     │
│  search(query, user_id, limit=3)    │
│  └─► Returns TOP 3 relevant         │
│      (used during conversation)     │
│                                     │
│  add(messages, user_id, metadata)   │
│  └─► Stores new memories            │
│      (used post-call)               │
│                                     │
└─────────────────────────────────────┘
```

---

## 🎯 Integration Points

```
┌──────────────────┐
│  ElevenLabs      │
│  Dashboard       │
└────────┬─────────┘
         │
         ├──► 1. Agent Configuration
         │    └─ Voice, language, prompt
         │
         ├──► 2. Conversation Initiation Webhook
         │    └─ URL + X-Workspace-Key header
         │
         ├──► 3. Custom Tool: memory_search
         │    └─ URL + parameters (query, user_id)
         │
         └──► 4. Post-Call Webhook
              └─ URL + HMAC signing key
```

---

## 📈 System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    AWS Cloud (Your Backend)              │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────┐ │
│  │ API Gateway 1  │  │ API Gateway 2  │  │ API GW 3   │ │
│  │ (Client Data)  │  │ (Retrieve)     │  │ (Post-Call)│ │
│  └───────┬────────┘  └───────┬────────┘  └──────┬─────┘ │
│          │                   │                   │       │
│          ▼                   ▼                   ▼       │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────┐ │
│  │ Lambda         │  │ Lambda         │  │ Lambda     │ │
│  │ ClientData     │  │ Retrieve       │  │ PostCall   │ │
│  │ Function       │  │ Function       │  │ Function   │ │
│  └───────┬────────┘  └───────┬────────┘  └──────┬─────┘ │
│          │                   │                   │       │
│          └───────────────────┼───────────────────┘       │
│                              │                           │
│                    ┌─────────▼─────────┐                 │
│                    │  Shared Lambda    │                 │
│                    │  Layer (mem0ai)   │                 │
│                    └─────────┬─────────┘                 │
│                              │                           │
└──────────────────────────────┼───────────────────────────┘
                               │
                               │ HTTPS API calls
                               ▼
                    ┌──────────────────┐
                    │   Mem0 Cloud     │
                    │   (Memory Store) │
                    └──────────────────┘
```

---

**See `ELEVENLABS_SETUP_GUIDE.md` for detailed setup instructions!**
