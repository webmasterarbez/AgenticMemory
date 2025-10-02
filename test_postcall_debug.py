#!/usr/bin/env python3
"""
Debug script for PostCall endpoint - tests with real ElevenLabs payload structure
"""

import json
import requests
import time
import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

POST_CALL_URL = os.getenv("ELEVENLABS_POST_CALL_URL")
HMAC_KEY = os.getenv("ELEVENLABS_HMAC_KEY")

# Load the real payload from ElevenLabs
with open('elevenlabs_post_call_payload.json', 'r') as f:
    payload_array = json.load(f)
    # Extract the first item from the array
    payload = payload_array[0]['data']

print("=== PostCall Debug Test ===")
print(f"URL: {POST_CALL_URL}")
print(f"\nPayload structure:")
print(f"- Has transcript: {'transcript' in payload}")
print(f"- Has analysis: {'analysis' in payload}")
print(f"- Has metadata: {'metadata' in payload}")

# Check where caller_id might be
if 'metadata' in payload:
    print(f"\nMetadata keys: {list(payload['metadata'].keys())}")
    if 'phone_call' in payload['metadata']:
        print(f"Phone call info: {payload['metadata']['phone_call']}")
    if 'caller_id' in payload['metadata']:
        print(f"Direct caller_id: {payload['metadata']['caller_id']}")
        
if 'conversation_initiation_client_data' in payload:
    dvars = payload['conversation_initiation_client_data'].get('dynamic_variables', {})
    print(f"\nDynamic variables: {dvars}")
    caller_id = dvars.get('system__caller_id')
    print(f"Caller ID from dynamic vars: {caller_id}")

# Try sending with current structure
print("\n\n=== Test 1: Sending payload AS-IS (will likely fail) ===")
payload_json = json.dumps(payload, separators=(',', ':'))
current_timestamp = str(int(time.time()))
full_payload_to_sign = f"{current_timestamp}.{payload_json}"
mac = hmac.new(
    key=HMAC_KEY.encode('utf-8'),
    msg=full_payload_to_sign.encode('utf-8'),
    digestmod=hashlib.sha256
)
signature = f"t={current_timestamp},v0={mac.hexdigest()}"

headers = {
    "Content-Type": "application/json",
    "ElevenLabs-Signature": signature
}

try:
    response = requests.post(POST_CALL_URL, json=payload, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Try with modified structure that handler expects
print("\n\n=== Test 2: Sending with caller_id in metadata ===")
modified_payload = {
    "conversation_id": payload.get('conversation_id', 'test-conv'),
    "agent_id": payload.get('agent_id', 'test-agent'),
    "call_duration": payload.get('metadata', {}).get('call_duration_secs', 0),
    "transcript": payload.get('transcript', []),
    "analysis": {
        "summary": payload.get('analysis', {}).get('transcript_summary', ''),
        "evaluation": payload.get('analysis', {}).get('evaluation_criteria_results', {})
    },
    "metadata": {
        "caller_id": payload.get('conversation_initiation_client_data', {}).get('dynamic_variables', {}).get('system__caller_id', '+16129782029')
    }
}

print(f"Modified caller_id: {modified_payload['metadata']['caller_id']}")

payload_json = json.dumps(modified_payload, separators=(',', ':'))
current_timestamp = str(int(time.time()))
full_payload_to_sign = f"{current_timestamp}.{payload_json}"
mac = hmac.new(
    key=HMAC_KEY.encode('utf-8'),
    msg=full_payload_to_sign.encode('utf-8'),
    digestmod=hashlib.sha256
)
signature = f"t={current_timestamp},v0={mac.hexdigest()}"

headers = {
    "Content-Type": "application/json",
    "ElevenLabs-Signature": signature
}

try:
    response = requests.post(POST_CALL_URL, json=modified_payload, headers=headers, timeout=60)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Wait a bit then check if memories were stored
    print("\nWaiting 5 seconds for async processing...")
    time.sleep(5)
    
    print("\nCheck CloudWatch logs for confirmation:")
    print("aws logs tail /aws/lambda/AgenticMemoriesPostCall --since 1m")
    
except Exception as e:
    print(f"Error: {e}")

