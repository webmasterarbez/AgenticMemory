#!/usr/bin/env python3
"""
Debug script for PostCall endpoint - simplified version
"""

import json
import time
import hmac
import hashlib

# Read from .env file manually
env_vars = {}
with open('.env', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key] = value

POST_CALL_URL = env_vars.get("ELEVENLABS_POST_CALL_URL")
HMAC_KEY = env_vars.get("ELEVENLABS_HMAC_KEY")

# Load the real payload from ElevenLabs
with open('elevenlabs_post_call_payload.json', 'r') as f:
    payload_array = json.load(f)
    payload = payload_array[0]['data']

print("=== PostCall Payload Analysis ===\n")
print(f"URL: {POST_CALL_URL}\n")

# Analyze payload structure
print("Payload structure:")
print(f"- conversation_id: {payload.get('conversation_id')}")
print(f"- agent_id: {payload.get('agent_id')}")
print(f"- Has transcript: {bool(payload.get('transcript'))}")
print(f"- Transcript messages: {len(payload.get('transcript', []))}")
print(f"- Has analysis: {bool(payload.get('analysis'))}")

# Check for caller_id locations
print("\n=== Searching for caller_id ===")
metadata = payload.get('metadata', {})
print(f"metadata keys: {list(metadata.keys())[:10]}")

if 'phone_call' in metadata:
    phone_info = metadata['phone_call']
    print(f"✓ Found in metadata.phone_call.external_number: {phone_info.get('external_number')}")
    
if 'caller_id' in metadata:
    print(f"✓ Found in metadata.caller_id: {metadata['caller_id']}")
else:
    print("✗ NOT found in metadata.caller_id")

conv_init = payload.get('conversation_initiation_client_data', {})
dvars = conv_init.get('dynamic_variables', {})
if 'system__caller_id' in dvars:
    print(f"✓ Found in conversation_initiation_client_data.dynamic_variables.system__caller_id: {dvars['system__caller_id']}")

# Show analysis structure
print("\n=== Analysis Structure ===")
analysis = payload.get('analysis', {})
print(f"Keys: {list(analysis.keys())}")
print(f"transcript_summary: {analysis.get('transcript_summary', '')[:100]}...")

# Show what handler expects vs what we have
print("\n=== Handler Expectations vs Reality ===")
print("Handler expects:")
print("  - metadata.caller_id ❌ (not present)")
print("  - analysis.summary ❌ (not present, use 'transcript_summary')")
print("  - analysis.evaluation ✓ (present as 'evaluation_criteria_results')")
print("  - transcript (array) ✓ (present)")

# Create corrected payload
print("\n=== Creating Handler-Compatible Payload ===")
caller_id = dvars.get('system__caller_id') or phone_info.get('external_number')
print(f"Using caller_id: {caller_id}")

corrected_payload = {
    "conversation_id": payload.get('conversation_id', 'test'),
    "agent_id": payload.get('agent_id', 'test'),
    "call_duration": metadata.get('call_duration_secs', 0),
    "transcript": payload.get('transcript', []),
    "analysis": {
        "summary": analysis.get('transcript_summary', ''),
        "evaluation": analysis.get('evaluation_criteria_results', {})
    },
    "metadata": {
        "caller_id": caller_id
    }
}

print("\n✅ Corrected payload structure created")
print(f"   - caller_id: {corrected_payload['metadata']['caller_id']}")
print(f"   - transcript: {len(corrected_payload['transcript'])} messages")
print(f"   - summary: {len(corrected_payload['analysis']['summary'])} chars")
print(f"   - evaluation: {len(corrected_payload['analysis']['evaluation'])} criteria")

# Save to file for manual testing
with open('corrected_postcall_payload.json', 'w') as f:
    json.dump(corrected_payload, f, indent=2)
print("\n✅ Saved to: corrected_postcall_payload.json")

print("\n=== Handler Fix Required ===")
print("The handler needs to support BOTH payload formats:")
print("1. ElevenLabs format (array with data wrapper)")
print("2. Direct format (flat object with metadata.caller_id)")
print("\nOr ElevenLabs webhook needs to be configured to send the correct format.")
