#!/usr/bin/env python3
"""
Simple ClientData endpoint test - uses .env file directly
"""

import json
import requests
import os

# Read .env file manually
env_vars = {}
with open('.env', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            key, value = line.split('=', 1)
            env_vars[key] = value

CLIENT_DATA_URL = env_vars.get('ELEVENLABS_CLIENT_DATA_URL')
WORKSPACE_KEY = env_vars.get('ELEVENLABS_WORKSPACE_KEY')

print("🧪 Testing ClientData Endpoint")
print("=" * 60)
print(f"URL: {CLIENT_DATA_URL}")
print(f"Auth: X-Workspace-Key (length: {len(WORKSPACE_KEY)})")
print()

# Test with existing caller (Stefan)
print("📞 Test 1: Returning caller with memories (+16129782029)")
print("-" * 60)

headers = {
    "Content-Type": "application/json",
    "X-Workspace-Key": WORKSPACE_KEY
}
payload = {"caller_id": "+16129782029"}

try:
    response = requests.post(CLIENT_DATA_URL, json=payload, headers=headers, timeout=10)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        # Print key information
        print("\n✅ SUCCESS!")
        print(f"Type: {data.get('type')}")
        print(f"\nDynamic Variables:")
        for key, value in data.get('dynamic_variables', {}).items():
            print(f"  - {key}: {value}")

        # Check for personalized greeting
        if 'conversation_config_override' in data:
            agent_config = data['conversation_config_override'].get('agent', {})
            first_message = agent_config.get('first_message', 'Not found')
            prompt_snippet = agent_config.get('prompt', {}).get('prompt', '')[:200]

            print(f"\n🎙️ First Message (Personalized Greeting):")
            print(f"  {first_message}")

            print(f"\n📝 Prompt Override (first 200 chars):")
            print(f"  {prompt_snippet}...")

        # Pretty print full response
        print("\n📄 Full Response:")
        print(json.dumps(data, indent=2))
    else:
        print(f"\n❌ FAILED!")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

# Test with new caller
print("\n\n📞 Test 2: New caller without memories (+15551234567)")
print("-" * 60)

payload = {"caller_id": "+15551234567"}

try:
    response = requests.post(CLIENT_DATA_URL, json=payload, headers=headers, timeout=10)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        print("\n✅ SUCCESS!")
        print(f"Returning Caller: {data.get('dynamic_variables', {}).get('returning_caller')}")
        print(f"Memory Count: {data.get('dynamic_variables', {}).get('memory_count')}")

        if 'conversation_config_override' in data:
            first_message = data['conversation_config_override'].get('agent', {}).get('first_message', '')
            print(f"\n🎙️ First Message:")
            print(f"  {first_message}")
    else:
        print(f"\n❌ FAILED!")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

print("\n" + "=" * 60)
print("✅ Test Complete!")
