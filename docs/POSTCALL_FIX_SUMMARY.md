# PostCall Memory Storage Fix - Summary

## Problem
PostCall Lambda was not storing memories from ElevenLabs agent calls to Mem0.

## Root Causes Identified

### 1. **Payload Format Mismatch**
ElevenLabs sends webhooks in **two different formats**:

**Format 1 (Array):**
```json
[
  {
    "type": "post_call_transcription",
    "data": {
      "conversation_id": "...",
      "transcript": [...],
      ...
    }
  }
]
```

**Format 2 (Object):**
```json
{
  "type": "post_call_transcription",
  "event_timestamp": 1234567890,
  "data": {
    "conversation_id": "...",
    "transcript": [...],
    ...
  }
}
```

**Original handler only supported Format 1**, causing Format 2 to fail.

### 2. **Caller ID Location Mismatch**
Handler expected: `metadata.caller_id`

ElevenLabs actually sends:
- `metadata.phone_call.external_number` (for phone calls)
- `conversation_initiation_client_data.dynamic_variables.system__caller_id`

### 3. **Analysis Field Name Mismatch**
Handler expected: `analysis.summary`

ElevenLabs actually sends: `analysis.transcript_summary`

### 4. **Transcript Format Incompatibility**
**ElevenLabs format:**
```json
{
  "role": "agent",
  "message": "Hello...",
  "tool_calls": [],
  ...
}
```

**Mem0 expected format:**
```json
{
  "role": "assistant",
  "content": "Hello..."
}
```

## Solutions Implemented

### Fix 1: Support Both Payload Formats
```python
# Handle both array and object formats
if isinstance(payload, list) and len(payload) > 0:
    if 'data' in payload[0]:
        payload = payload[0]['data']
elif isinstance(payload, dict) and 'data' in payload and 'type' in payload:
    payload = payload['data']
```

### Fix 2: Multi-Location Caller ID Extraction
```python
# Try multiple locations
caller_id = metadata.get('caller_id')  # Direct format

if not caller_id and 'phone_call' in metadata:
    caller_id = metadata['phone_call'].get('external_number')
    
if not caller_id and 'conversation_initiation_client_data' in payload:
    caller_id = payload['conversation_initiation_client_data']['dynamic_variables'].get('system__caller_id')
```

### Fix 3: Support Both Analysis Field Names
```python
summary = analysis.get('summary') or analysis.get('transcript_summary', '')
evaluation = analysis.get('evaluation') or analysis.get('evaluation_criteria_results', {})
```

### Fix 4: Transform Transcript Format
```python
transformed_transcript = []
for msg in transcript:
    role = msg.get('role', 'user')
    if role == 'agent':
        role = 'assistant'
    content = msg.get('message') or msg.get('content', '')
    if content:
        transformed_transcript.append({
            'role': role,
            'content': content
        })
```

## Test Results

✅ **Factual Memory**: Successfully storing call summaries and evaluations
✅ **Semantic Memory**: Successfully storing full conversation transcripts
✅ **Caller ID Extraction**: Working for phone calls
✅ **Both Payload Formats**: Supported

## Deployment Status

**Deployed**: October 1, 2025 at 20:12 UTC
**Stack**: sam-app
**Region**: us-east-1
**Functions Updated**: AgenticMemoriesPostCall

## Verification

Check CloudWatch logs for successful storage:
```bash
aws logs tail /aws/lambda/AgenticMemoriesPostCall --since 10m | grep -E "Stored"
```

Expected output:
```
[INFO] Stored factual memory for +16129782029
[INFO] Stored semantic memory for +16129782029 (X messages)
```

## Next Steps

1. Monitor production calls for any edge cases
2. Consider adding structured logging for better debugging
3. Document ElevenLabs webhook configuration requirements
4. Add unit tests for both payload formats

## Files Modified

- `src/post_call/handler.py`: Added multi-format support and field mapping
