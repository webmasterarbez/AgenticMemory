#!/usr/bin/env python3
"""
Simple PostCall endpoint test - uses .env file directly
"""

import json
import requests
import hmac
import hashlib
import time

# Read .env file manually
env_vars = {}
with open('.env', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            key, value = line.split('=', 1)
            env_vars[key] = value

POST_CALL_URL = env_vars.get('ELEVENLABS_POST_CALL_URL')
HMAC_KEY = env_vars.get('ELEVENLABS_HMAC_KEY')

print("🧪 Testing PostCall Endpoint")
print("=" * 60)
print(f"URL: {POST_CALL_URL}")
print(f"HMAC Key: {HMAC_KEY[:20]}... (length: {len(HMAC_KEY)})")
print()

# Create test payload
payload = {
    "conversation_id": "test-conv-" + str(int(time.time())),
    "agent_id": "test-agent-123",
    "call_duration": 120,
    "transcript": [
        {"role": "user", "content": "Hello, my name is Stefan and I'm calling about my account."},
        {"role": "assistant", "content": "Hello Stefan! I'd be happy to help you with your account. What can I assist you with today?"},
        {"role": "user", "content": "I'd like to upgrade to a premium account."},
        {"role": "assistant", "content": "Great choice! I can help you upgrade to our premium tier. Let me get that set up for you."}
    ],
    "analysis": {
        "summary": "Stefan called to upgrade to premium account. Successfully processed the upgrade request.",
        "evaluation": {
            "rationale": "Customer was satisfied with the service and expressed interest in premium features."
        }
    },
    "metadata": {
        "caller_id": "+16129782029"
    }
}

payload_str = json.dumps(payload)

# Generate HMAC signature
timestamp = str(int(time.time()))
signed_payload = f"{timestamp}.{payload_str}"

mac = hmac.new(
    key=HMAC_KEY.encode('utf-8'),
    msg=signed_payload.encode('utf-8'),
    digestmod=hashlib.sha256
)
signature = f"t={timestamp},v0={mac.hexdigest()}"

print("📞 Test 1: Valid HMAC signature with call data")
print("-" * 60)
print(f"Caller ID: {payload['metadata']['caller_id']}")
print(f"Conversation ID: {payload['conversation_id']}")
print(f"Transcript Messages: {len(payload['transcript'])}")
print(f"Summary: {payload['analysis']['summary'][:80]}...")
print(f"\nHMAC Signature: {signature[:50]}...")
print()

headers = {
    "Content-Type": "application/json",
    "ElevenLabs-Signature": signature
}

try:
    response = requests.post(POST_CALL_URL, data=payload_str, headers=headers, timeout=10)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS!")
        print(f"Response: {json.dumps(data, indent=2)}")
        print("\n📝 Note: PostCall returns 200 immediately and processes asynchronously.")
        print("   Check CloudWatch logs to verify memory storage:")
        print(f"   aws logs tail /aws/lambda/AgenticMemoriesPostCall --follow")
    else:
        print(f"\n❌ FAILED!")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

# Test 2: Invalid HMAC signature
print("\n\n📞 Test 2: Invalid HMAC signature (should still return 200)")
print("-" * 60)

invalid_signature = f"t={timestamp},v0=invalid_signature_hash"
headers["ElevenLabs-Signature"] = invalid_signature

try:
    response = requests.post(POST_CALL_URL, data=payload_str, headers=headers, timeout=10)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        print("\n✅ Returns 200 as expected (async pattern)")
        print("   Check CloudWatch logs - should see HMAC validation error")
    else:
        print(f"\n⚠️  Unexpected status code: {response.status_code}")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

# Test 3: Missing signature header
print("\n\n📞 Test 3: Missing HMAC signature header")
print("-" * 60)

headers_no_sig = {"Content-Type": "application/json"}

try:
    response = requests.post(POST_CALL_URL, data=payload_str, headers=headers_no_sig, timeout=10)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        print("\n✅ Returns 200 as expected (async pattern)")
        print("   Check CloudWatch logs - should see 'Missing signature' error")
    else:
        print(f"\n⚠️  Unexpected status code: {response.status_code}")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

print("\n" + "=" * 60)
print("✅ Test Complete!")
print("\n💡 To verify memories were stored, run:")
print("   python3 test_clientdata_simple.py")
print("   (Check if Stefan's memories now appear)")
