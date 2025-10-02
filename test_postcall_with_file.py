#!/usr/bin/env python3
"""
Test PostCall endpoint with ElevenLabs conversation files.

Usage:
    python3 test_postcall_with_file.py [conversation_file.json]
    
    If no file specified, defaults to: conv_01jxd5y165f62a0v7gtr6bkg56.json

Examples:
    python3 test_postcall_with_file.py
    python3 test_postcall_with_file.py conv_01jxk1wejhenk8x8tt9enzxw4a.json
    python3 test_postcall_with_file.py my_conversation.json
"""

import json
import os
import sys
import hmac
import hashlib
import time
import urllib.request
import urllib.error

# Get conversation file from command line or use default
if len(sys.argv) > 1:
    conversation_file = sys.argv[1]
else:
    conversation_file = "conv_01jxd5y165f62a0v7gtr6bkg56.json"

# Check if file exists
if not os.path.exists(conversation_file):
    print(f"❌ ERROR: File not found: {conversation_file}")
    print("\nUsage:")
    print(f"  {sys.argv[0]} [conversation_file.json]")
    print("\nExample:")
    print(f"  {sys.argv[0]} conv_01jxk1wejhenk8x8tt9enzxw4a.json")
    exit(1)

# Get environment variables (or prompt for them)
POST_CALL_URL = os.getenv("ELEVENLABS_POST_CALL_URL")
HMAC_KEY = os.getenv("ELEVENLABS_HMAC_KEY")

# If not in env, prompt user
if not POST_CALL_URL:
    POST_CALL_URL = input("Enter ELEVENLABS_POST_CALL_URL: ").strip()
if not HMAC_KEY:
    HMAC_KEY = input("Enter ELEVENLABS_HMAC_KEY: ").strip()

if not POST_CALL_URL or not HMAC_KEY:
    print("❌ ERROR: Missing required environment variables")
    print("   Required: ELEVENLABS_POST_CALL_URL, ELEVENLABS_HMAC_KEY")
    exit(1)

# Read the conversation file
print(f"📂 Reading conversation file: {conversation_file}")
try:
    with open(conversation_file, "r") as f:
        payload = json.load(f)
except json.JSONDecodeError as e:
    print(f"❌ ERROR: Invalid JSON in {conversation_file}")
    print(f"   {str(e)}")
    exit(1)
except Exception as e:
    print(f"❌ ERROR: Could not read {conversation_file}")
    print(f"   {str(e)}")
    exit(1)

# Pretty print some key details from the payload
print("\n📋 Payload Summary:")
print(f"   Conversation ID: {payload.get('conversation_id')}")
print(f"   Agent ID: {payload.get('agent_id')}")
print(f"   Status: {payload.get('status')}")

# Check for caller ID in various locations
caller_id = None
if 'metadata' in payload:
    phone_call = payload['metadata'].get('phone_call', {})
    caller_id = phone_call.get('external_number')
    print(f"   Caller ID (from metadata.phone_call.external_number): {caller_id}")

if 'conversation_initiation_client_data' in payload:
    dynamic_vars = payload['conversation_initiation_client_data'].get('dynamic_variables', {})
    system_caller_id = dynamic_vars.get('system__caller_id')
    print(f"   System Caller ID (from dynamic_variables): {system_caller_id}")

# Print transcript length
transcript_length = len(payload.get('transcript', []))
print(f"   Transcript messages: {transcript_length}")

# Print analysis summary
if 'analysis' in payload:
    analysis = payload['analysis']
    if 'transcript_summary' in analysis:
        summary = analysis['transcript_summary'][:100] + "..." if len(analysis['transcript_summary']) > 100 else analysis['transcript_summary']
        print(f"   Summary: {summary}")
    if 'evaluation_criteria_results' in analysis:
        results = analysis['evaluation_criteria_results']
        print(f"   Evaluation criteria: {len(results)} items")

# Generate HMAC signature
print("\n🔐 Generating HMAC signature...")
timestamp = str(int(time.time()))
body_json = json.dumps(payload, separators=(',', ':'))

# Create signed content: timestamp.body
signed_content = f"{timestamp}.{body_json}"

# Generate HMAC-SHA256 signature
signature = hmac.new(
    HMAC_KEY.encode('utf-8'),
    signed_content.encode('utf-8'),
    hashlib.sha256
).hexdigest()

# Format signature header
signature_header = f"t={timestamp},v0={signature}"
print(f"   Timestamp: {timestamp}")
print(f"   Signature (v0): {signature[:20]}...")

# Make request
print(f"\n🚀 Sending POST request to {POST_CALL_URL}")
print("=" * 80)

# Create request with urllib
req = urllib.request.Request(
    POST_CALL_URL,
    data=body_json.encode('utf-8'),
    headers={
        "Content-Type": "application/json",
        "ElevenLabs-Signature": signature_header
    },
    method='POST'
)

try:
    with urllib.request.urlopen(req, timeout=10) as response:
        status_code = response.status
        response_body = response.read().decode('utf-8')
        
        print(f"\n📊 Response Status: {status_code}")
        
        try:
            response_data = json.loads(response_body)
            print(f"\n✅ Response Body:")
            print(json.dumps(response_data, indent=2))
        except json.JSONDecodeError:
            print(f"\n📄 Response Body (text):")
            print(response_body)
        
        if status_code == 200:
            print("\n✅ SUCCESS: PostCall endpoint accepted the payload")
            print("\n💡 Next steps:")
            print("   1. Check CloudWatch logs for processing details:")
            print("      aws logs tail /aws/lambda/AgenticMemoriesPostCall --since 5m --follow")
            print(f"   2. Verify memories stored for caller: {caller_id}")
            print("   3. Test Retrieve endpoint to confirm memories are searchable")
        else:
            print(f"\n❌ FAILURE: PostCall endpoint returned {status_code}")
            
except urllib.error.HTTPError as e:
    print(f"\n❌ HTTP ERROR: {e.code} - {e.reason}")
    print(f"   Response: {e.read().decode('utf-8')}")
    exit(1)
except urllib.error.URLError as e:
    print(f"\n❌ URL ERROR: {str(e)}")
    exit(1)
except Exception as e:
    print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
    exit(1)

print("\n" + "=" * 80)
