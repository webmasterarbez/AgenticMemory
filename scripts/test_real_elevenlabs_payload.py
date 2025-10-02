#!/usr/bin/env python3
"""
Test the updated PostCall handler with actual ElevenLabs payload format
"""
import json
import time
import hmac
import hashlib
import sys

# Read env vars
env_vars = {}
with open('.env', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key] = value

POST_CALL_URL = env_vars.get("ELEVENLABS_POST_CALL_URL")
HMAC_KEY = env_vars.get("ELEVENLABS_HMAC_KEY")

# Load real ElevenLabs payload (as array)
with open('elevenlabs_post_call_payload.json', 'r') as f:
    payload = json.load(f)  # Keep as array

print("=== Testing PostCall with Real ElevenLabs Payload ===\n")
print(f"URL: {POST_CALL_URL}")
print(f"Payload type: {type(payload)}")
print(f"Payload length: {len(payload)}")

# Create HMAC signature
payload_json = json.dumps(payload, separators=(',', ':'))
current_timestamp = str(int(time.time()))
full_payload_to_sign = f"{current_timestamp}.{payload_json}"

mac = hmac.new(
    key=HMAC_KEY.encode('utf-8'),
    msg=full_payload_to_sign.encode('utf-8'),
    digestmod=hashlib.sha256
)
signature = f"t={current_timestamp},v0={mac.hexdigest()}"

print(f"HMAC Signature: {signature[:50]}...")

# Test with curl
import subprocess

curl_cmd = [
    'curl', '-X', 'POST', POST_CALL_URL,
    '-H', 'Content-Type: application/json',
    '-H', f'ElevenLabs-Signature: {signature}',
    '-d', payload_json,
    '-w', '\nHTTP Status: %{http_code}\n',
    '-s'
]

print("\n=== Sending Request ===")
result = subprocess.run(curl_cmd, capture_output=True, text=True)
print(result.stdout)

if result.returncode == 0:
    print("\n✅ Request sent successfully")
    print("\nWaiting 10 seconds for async processing...")
    time.sleep(10)
    
    print("\n=== Checking CloudWatch Logs ===")
    logs_cmd = ['aws', 'logs', 'tail', '/aws/lambda/AgenticMemoriesPostCall', '--since', '1m', '--format', 'short']
    logs_result = subprocess.run(logs_cmd, capture_output=True, text=True)
    
    # Filter for relevant logs
    for line in logs_result.stdout.split('\n'):
        if any(keyword in line for keyword in ['Processing post-call', 'Stored', 'caller_id', 'ERROR', 'Missing']):
            print(line)
    
    print("\n=== Verification ===")
    print("Check if memories were stored:")
    print("1. Look for 'Stored factual memory' in logs above")
    print("2. Look for 'Stored semantic memory' in logs above")
    print("\nIf you see both, the fix worked! ✅")
else:
    print(f"\n❌ Request failed with return code: {result.returncode}")
    print(result.stderr)

