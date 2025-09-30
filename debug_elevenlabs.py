#!/usr/bin/env python3
"""
Simple test to mimic ElevenLabs conversation initiation webhook
"""

import json
import requests

CLIENTDATA_URL = "https://8nv3jj2gie.execute-api.us-east-1.amazonaws.com/Prod/client-data"
WORKSPACE_KEY = "wsec_eb779969b7cb5cde6cdd9c6dfc4e2a08fa38cd6711b86eced6c101039871f6ac"

# Test what ElevenLabs might actually send
test_payloads = [
    # Minimal payload
    {
        "caller_id": "+16129782029"
    },
    # More complete payload
    {
        "caller_id": "+16129782029",
        "agent_id": "agent_01jxbrc1trfxev5sdp5xk4ra67",
        "called_number": "+16123241623",
        "call_sid": "test-call-123"
    },
    # ElevenLabs format from your example
    {
        "system__caller_id": "+16129782029",
        "system__agent_id": "agent_01jxbrc1trfxev5sdp5xk4ra67",
        "system__called_number": "+16123241623"
    }
]

for i, payload in enumerate(test_payloads, 1):
    print(f"\n=== Test {i}: {list(payload.keys())} ===")
    
    headers = {
        "Content-Type": "application/json",
        "X-Workspace-Key": WORKSPACE_KEY,
        "User-Agent": "ElevenLabs/1.0"
    }
    
    try:
        response = requests.post(CLIENTDATA_URL, json=payload, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS - Dynamic vars: {list(data.get('dynamic_variables', {}).keys())}")
            print(f"Sample response: {json.dumps(data, indent=2)[:200]}...")
        else:
            print(f"❌ ERROR: {response.text}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

# Test with different header variations
print(f"\n=== Test: Header Variations ===")
payload = {"caller_id": "+16129782029"}

header_tests = [
    {"Content-Type": "application/json", "x-workspace-key": WORKSPACE_KEY},  # lowercase
    {"Content-Type": "application/json", "X-WORKSPACE-KEY": WORKSPACE_KEY},  # uppercase
    {"Content-Type": "application/json", "workspace-key": WORKSPACE_KEY},    # no X prefix
]

for i, headers in enumerate(header_tests, 1):
    try:
        response = requests.post(CLIENTDATA_URL, json=payload, headers=headers, timeout=5)
        print(f"Header test {i}: {response.status_code} - {list(headers.keys())}")
    except Exception as e:
        print(f"Header test {i}: ERROR - {e}")

print(f"\n=== Raw Response Headers Test ===")
try:
    response = requests.post(CLIENTDATA_URL, json={"caller_id": "+16129782029"}, 
                           headers={"Content-Type": "application/json", "X-Workspace-Key": WORKSPACE_KEY}, 
                           timeout=5)
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Raw test error: {e}")