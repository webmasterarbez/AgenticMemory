# Test Data Files

This directory contains JSON test payloads and conversation files for testing the AgenticMemory endpoints.

## 📝 Conversation Files

These are real ElevenLabs post-call webhook payloads from actual phone conversations:

### `conv_01jxd5y165f62a0v7gtr6bkg56.json`
- **Messages**: 161
- **Caller**: +15074595005 (Sheila)
- **Description**: Sheila's first call - extensive conversation about travel in Russia, Scandinavia, and Europe
- **Use Case**: Test long conversation handling and timeout behavior
- **Processing Time**: ~110+ seconds (factual: 52s, semantic: 68+s)
- **Status**: Tests Lambda timeout limits

### `conv_01jxk1wejhenk8x8tt9enzxw4a.json`
- **Messages**: 115
- **Caller**: +16129782029 (Sheila's second call)
- **Description**: Follow-up conversation with slightly shorter transcript
- **Use Case**: Test medium-length conversation handling
- **Processing Time**: ~90 seconds
- **Status**: Processing successfully within 120s timeout

---

## 🧪 Sample Payloads

### `elevenlabs_post_call_payload.json`
- **Format**: Array format `[{"type": "post_call_transcription", "data": {...}}]`
- **Purpose**: Reference payload structure from ElevenLabs documentation
- **Use Case**: Understanding the expected webhook payload format

### `corrected_postcall_payload.json`
- **Format**: Object format `{"type": "post_call_transcription", "data": {...}}`
- **Purpose**: Corrected payload format after debugging
- **Use Case**: Testing alternate payload format support

---

## 📊 Payload Structure

ElevenLabs sends post-call webhooks in two formats:

### Array Format
```json
[
  {
    "type": "post_call_transcription",
    "data": {
      "conversation_id": "conv_...",
      "metadata": {
        "phone_call": {
          "external_number": "+1234567890"
        }
      },
      "transcript": [
        {"role": "agent", "message": "..."},
        {"role": "user", "message": "..."}
      ],
      "analysis": {
        "transcript_summary": "...",
        "call_successful": true
      }
    }
  }
]
```

### Object Format
```json
{
  "type": "post_call_transcription",
  "event_timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "conversation_id": "conv_...",
    "metadata": {
      "caller_id": "+1234567890"
    },
    "transcript": [...],
    "analysis": {...}
  }
}
```

---

## 🎯 Usage Examples

### Test with Conversation Files
```bash
# Using Python script
cd scripts
python3 test_postcall_with_file.py ../test_data/conv_01jxd5y165f62a0v7gtr6bkg56.json

# Using bash wrapper
cd scripts
./test_postcall.sh ../test_data/conv_01jxk1wejhenk8x8tt9enzxw4a.json
```

### Test with Sample Payloads
```bash
cd scripts
python3 test_real_payload.py
python3 test_real_elevenlabs_payload.py
```

---

## 📈 Performance Characteristics

| File | Messages | Caller ID | Processing Time | Status |
|------|----------|-----------|----------------|--------|
| conv_01jxd5y165f62a0v7gtr6bkg56.json | 161 | +15074595005 | 110+s | Timeout (semantic) |
| conv_01jxk1wejhenk8x8tt9enzxw4a.json | 115 | +16129782029 | 90s | Success |
| elevenlabs_post_call_payload.json | Varies | Sample | N/A | Reference only |
| corrected_postcall_payload.json | Varies | Sample | N/A | Reference only |

**Note**: Factual memory always stores successfully within 60s. Semantic memory may timeout for conversations with 150+ messages.

---

## 🔍 Caller ID Locations

The handler checks multiple locations for caller ID:

1. `data.metadata.phone_call.external_number` (primary for phone calls)
2. `data.metadata.caller_id` (fallback)
3. `data.conversation_initiation_client_data.dynamic_variables.system__caller_id` (fallback)

All conversation files in this directory include caller IDs in one of these locations.

---

## 🛠️ Adding New Test Files

To add your own conversation file:

1. Save the ElevenLabs webhook payload as JSON
2. Place it in this directory with a descriptive name
3. Test with: `./scripts/test_postcall.sh test_data/your_file.json`

---

## 📚 Related Documentation

- **[../docs/USING_TEST_SCRIPT.md](../docs/USING_TEST_SCRIPT.md)** - How to use test scripts
- **[../docs/POSTCALL_FIX_SUMMARY.md](../docs/POSTCALL_FIX_SUMMARY.md)** - PostCall bug fixes
- **[../docs/TEST_RESULTS.md](../docs/TEST_RESULTS.md)** - Historical test results
- **[../scripts/README.md](../scripts/README.md)** - All test scripts
