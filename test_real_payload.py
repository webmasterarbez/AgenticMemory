#!/usr/bin/env python3
"""
Test script for PostCall endpoint using the actual ElevenLabs payload
"""

import json
import hmac
import hashlib
import time
import requests

# Configuration
POSTCALL_URL = "https://7iumhxcckh.execute-api.us-east-1.amazonaws.com/Prod/post-call"
HMAC_KEY = input("Enter your ElevenLabs HMAC Key: ").strip()

# Load the actual ElevenLabs payload
with open("elevenlabs_post_call_payload.json", "r") as f:
    elevenlabs_payload = json.load(f)

# Extract the relevant data from the ElevenLabs format
post_call_data = elevenlabs_payload[0]["data"]

# Transform to our expected format
payload = {
    "conversation_id": post_call_data["conversation_id"],
    "agent_id": post_call_data["agent_id"],
    "call_duration": post_call_data["metadata"]["call_duration_secs"],
    "transcript": [
        {
            "role": "assistant" if msg["role"] == "agent" else "user",
            "content": msg["message"]
        }
        for msg in post_call_data["transcript"]
    ],
    "analysis": {
        "summary": post_call_data["analysis"]["transcript_summary"],
        "evaluation": {
            "rationale": f"Call success: {post_call_data['analysis']['call_successful']}. " +
                        f"Session closure: {post_call_data['analysis']['evaluation_criteria_results']['session_closure']['result']}. " +
                        f"Empathy displayed: {post_call_data['analysis']['evaluation_criteria_results']['empathy_displayed']['result']}."
        }
    },
    "metadata": {
        "caller_id": post_call_data["conversation_initiation_client_data"]["dynamic_variables"]["system__caller_id"]
    }
}

# Convert to JSON string
body = json.dumps(payload)

# Generate HMAC signature
timestamp = str(int(time.time()))
payload_to_sign = f"{timestamp}.{body}"

mac = hmac.new(
    key=HMAC_KEY.encode('utf-8'),
    msg=payload_to_sign.encode('utf-8'),
    digestmod=hashlib.sha256
)
signature = f"t={timestamp},v0={mac.hexdigest()}"

print(f"\n=== Testing PostCall with Real ElevenLabs Data ===")
print(f"URL: {POSTCALL_URL}")
print(f"Caller ID: {payload['metadata']['caller_id']}")
print(f"Conversation ID: {payload['conversation_id']}")
print(f"Agent ID: {payload['agent_id']}")
print(f"Call Duration: {payload['call_duration']} seconds")
print(f"Transcript Messages: {len(payload['transcript'])}")
print(f"Summary: {payload['analysis']['summary'][:100]}...")
print(f"Payload size: {len(body)} bytes")

# Send the request
headers = {
    "Content-Type": "application/json",
    "ElevenLabs-Signature": signature
}

try:
    print(f"\n--- Sending Request ---")
    response = requests.post(POSTCALL_URL, data=body, headers=headers, timeout=15)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: PostCall request accepted!")
        print("\n💡 Check CloudWatch Logs for processing details:")
        print("   aws logs get-log-events --log-group-name /aws/lambda/AgenticMemoriesPostCall --log-stream-name $(aws logs describe-log-streams --log-group-name /aws/lambda/AgenticMemoriesPostCall --query 'logStreams[0].logStreamName' --output text --region us-east-1) --region us-east-1 --start-time $(date -d '2 minutes ago' +%s)000")
        
        print(f"\n📊 Expected Memory Storage:")
        print(f"   - Factual Memory: Summary + evaluation rationale")
        print(f"   - Semantic Memory: {len(payload['transcript'])} conversation messages")
        print(f"   - User ID: {payload['metadata']['caller_id']}")
        
    else:
        print(f"❌ FAILED: Expected 200, got {response.status_code}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print(f"\n=== Payload Preview ===")
print(json.dumps(payload, indent=2)[:500] + "...")