#!/usr/bin/env python3
"""
Test script for PostCall endpoint HMAC verification
Generates a valid HMAC signature to test the authentication
"""

import json
import hmac
import hashlib
import time
import requests
import sys

# Configuration
POSTCALL_URL = "https://7iumhxcckh.execute-api.us-east-1.amazonaws.com/Prod/post-call"
HMAC_KEY = input("Enter your ElevenLabs HMAC Key: ").strip()

# Test payload
payload = {
    "conversation_id": "test-conv-123",
    "agent_id": "test-agent-456",
    "call_duration": 120,
    "transcript": [
        {"role": "user", "content": "Hello, I need help with my account"},
        {"role": "assistant", "content": "I'd be happy to help you with your account. What specifically do you need assistance with?"},
        {"role": "user", "content": "I want to update my email address"}
    ],
    "analysis": {
        "summary": "Customer requested help updating their email address",
        "evaluation": {
            "rationale": "Customer was polite and clearly stated their needs"
        }
    },
    "metadata": {
        "caller_id": "+16129782029"
    }
}

# Convert to JSON string
body = json.dumps(payload)

# Generate HMAC signature (ElevenLabs format: t=timestamp,v0=hash)
timestamp = str(int(time.time()))
payload_to_sign = f"{timestamp}.{body}"

# Create HMAC
mac = hmac.new(
    key=HMAC_KEY.encode('utf-8'),
    msg=payload_to_sign.encode('utf-8'),
    digestmod=hashlib.sha256
)
signature = f"t={timestamp},v0={mac.hexdigest()}"

print(f"\n=== Testing PostCall Endpoint ===")
print(f"URL: {POSTCALL_URL}")
print(f"Timestamp: {timestamp}")
print(f"Signature: {signature[:50]}...")
print(f"Payload size: {len(body)} bytes")

# Test 1: Valid HMAC signature
print("\n--- Test 1: Valid HMAC Signature ---")
headers = {
    "Content-Type": "application/json",
    "ElevenLabs-Signature": signature
}

try:
    response = requests.post(POSTCALL_URL, data=body, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: HMAC verification passed!")
    else:
        print("❌ FAILED: Expected 200, got", response.status_code)
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: Missing signature header
print("\n--- Test 2: Missing Signature Header ---")
try:
    response = requests.post(POSTCALL_URL, data=body, headers={"Content-Type": "application/json"}, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: Request accepted (HMAC validation should have logged error)")
    else:
        print("⚠️  Note: Got status", response.status_code)
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 3: Invalid signature
print("\n--- Test 3: Invalid Signature ---")
invalid_headers = {
    "Content-Type": "application/json",
    "ElevenLabs-Signature": f"t={timestamp},v0=invalidsignature123"
}

try:
    response = requests.post(POSTCALL_URL, data=body, headers=invalid_headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: Request accepted (HMAC validation should have logged error)")
    else:
        print("⚠️  Note: Got status", response.status_code)
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 4: Old timestamp (should fail timestamp validation)
print("\n--- Test 4: Old Timestamp (31 minutes ago) ---")
old_timestamp = str(int(time.time()) - 31 * 60)
old_payload_to_sign = f"{old_timestamp}.{body}"
old_mac = hmac.new(
    key=HMAC_KEY.encode('utf-8'),
    msg=old_payload_to_sign.encode('utf-8'),
    digestmod=hashlib.sha256
)
old_signature = f"t={old_timestamp},v0={old_mac.hexdigest()}"

old_headers = {
    "Content-Type": "application/json",
    "ElevenLabs-Signature": old_signature
}

try:
    response = requests.post(POSTCALL_URL, data=body, headers=old_headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: Request accepted (timestamp validation should have logged error)")
    else:
        print("⚠️  Note: Got status", response.status_code)
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n=== Test Complete ===")
print("\n💡 Check CloudWatch Logs for detailed validation results:")
print("   aws logs tail /aws/lambda/AgenticMemoriesPostCall --follow")
