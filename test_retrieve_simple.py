#!/usr/bin/env python3
"""
Simple Retrieve endpoint test - uses .env file directly
"""

import json
import requests

# Read .env file manually
env_vars = {}
with open('.env', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            key, value = line.split('=', 1)
            env_vars[key] = value

RETRIEVE_URL = env_vars.get('ELEVENLABS_RETRIEVE_URL')

print("🧪 Testing Retrieve Endpoint (Semantic Search)")
print("=" * 60)
print(f"URL: {RETRIEVE_URL}")
print("Auth: None (trusted agent connection)")
print()

# Test 1: Search for account-related memories
print("📞 Test 1: Search for 'account' (Stefan with memories)")
print("-" * 60)

headers = {"Content-Type": "application/json"}
payload = {
    "query": "account upgrade premium",
    "user_id": "+16129782029"
}

try:
    response = requests.post(RETRIEVE_URL, json=payload, headers=headers, timeout=10)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        memories = data.get('memories', [])

        print(f"\n✅ SUCCESS!")
        print(f"Found {len(memories)} relevant memories")

        if memories:
            print(f"\n📝 Search Results:")
            for i, mem in enumerate(memories, 1):
                if isinstance(mem, dict):
                    memory_text = mem.get('memory', 'N/A')
                    score = mem.get('score', 'N/A')
                    mem_id = mem.get('id', 'N/A')
                    print(f"\n  {i}. Memory ID: {mem_id}")
                    print(f"     Score: {score}")
                    print(f"     Content: {memory_text}")
                else:
                    print(f"\n  {i}. {mem}")
        else:
            print("\n⚠️  No memories found for this query")

        print(f"\n📄 Full Response:")
        print(json.dumps(data, indent=2))
    else:
        print(f"\n❌ FAILED!")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

# Test 2: Search for email preferences
print("\n\n📞 Test 2: Search for 'email preferences'")
print("-" * 60)

payload = {
    "query": "email communication preferences",
    "user_id": "+16129782029"
}

try:
    response = requests.post(RETRIEVE_URL, json=payload, headers=headers, timeout=10)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        memories = data.get('memories', [])

        print(f"\n✅ SUCCESS!")
        print(f"Found {len(memories)} relevant memories")

        if memories:
            print(f"\n📝 Top Memories:")
            for i, mem in enumerate(memories, 1):
                if isinstance(mem, dict):
                    print(f"  {i}. {mem.get('memory', 'N/A')[:100]}...")
                else:
                    print(f"  {i}. {str(mem)[:100]}...")
    else:
        print(f"\n❌ FAILED!")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

# Test 3: Search for user with no memories
print("\n\n📞 Test 3: Search for user with no memories")
print("-" * 60)

payload = {
    "query": "anything",
    "user_id": "+15551234567"
}

try:
    response = requests.post(RETRIEVE_URL, json=payload, headers=headers, timeout=10)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        memories = data.get('memories', [])

        print(f"\n✅ SUCCESS!")
        print(f"Found {len(memories)} memories (expected 0)")

        if not memories:
            print("✓ Correctly returns empty array for new users")
    else:
        print(f"\n❌ FAILED!")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

# Test 4: Missing query parameter (error case)
print("\n\n📞 Test 4: Missing query parameter (error handling)")
print("-" * 60)

payload = {
    "user_id": "+16129782029"
    # Missing "query"
}

try:
    response = requests.post(RETRIEVE_URL, json=payload, headers=headers, timeout=10)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 400:
        print(f"\n✅ Correctly returns 400 for missing query")
        print(f"Error message: {response.json().get('error', 'N/A')}")
    else:
        print(f"\n⚠️  Status: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

# Test 5: Missing user_id parameter (error case)
print("\n\n📞 Test 5: Missing user_id parameter (error handling)")
print("-" * 60)

payload = {
    "query": "test"
    # Missing "user_id"
}

try:
    response = requests.post(RETRIEVE_URL, json=payload, headers=headers, timeout=10)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 400:
        print(f"\n✅ Correctly returns 400 for missing user_id")
        print(f"Error message: {response.json().get('error', 'N/A')}")
    else:
        print(f"\n⚠️  Status: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

print("\n" + "=" * 60)
print("✅ Retrieve Endpoint Test Complete!")
print("\n💡 Key Features:")
print("   - Semantic search with relevance scoring")
print("   - Returns top N results (configured via MEM0_SEARCH_LIMIT)")
print("   - No authentication required (trusted agent connection)")
print("   - Fast response times for mid-call queries")
