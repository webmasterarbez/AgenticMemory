#!/usr/bin/env python3
"""Test the Retrieve endpoint for semantic search"""
import json
import subprocess

# Read env vars
env = {}
for line in open('.env'):
    if '=' in line and not line.startswith('#'):
        k, v = line.strip().split('=', 1)
        env[k] = v

RETRIEVE_URL = env.get('ELEVENLABS_RETRIEVE_URL', 'https://7h6j2vasna.execute-api.us-east-1.amazonaws.com/Prod/retrieve')

print("=== Testing Retrieve Endpoint ===\n")
print(f"URL: {RETRIEVE_URL}")

# Test 1: Search for user preferences
test_cases = [
    {
        "query": "What are the user's preferences?",
        "user_id": "+16129782029",
        "description": "General preferences search"
    },
    {
        "query": "Tell me about Stefan",
        "user_id": "+16129782029", 
        "description": "Search for user name"
    },
    {
        "query": "previous conversations",
        "user_id": "+16129782029",
        "description": "Search conversation history"
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*60}")
    print(f"Test {i}: {test['description']}")
    print(f"Query: {test['query']}")
    print(f"User ID: {test['user_id']}")
    print('-'*60)
    
    payload = json.dumps({
        "query": test["query"],
        "user_id": test["user_id"]
    })
    
    result = subprocess.run([
        'curl', '-X', 'POST', RETRIEVE_URL,
        '-H', 'Content-Type: application/json',
        '-d', payload,
        '-s', '-w', '\nHTTP: %{http_code}\n'
    ], capture_output=True, text=True, timeout=15)
    
    print(result.stdout)
    
    # Parse and display results nicely
    try:
        lines = result.stdout.split('\n')
        json_part = '\n'.join(lines[:-2])  # Remove HTTP status line
        data = json.loads(json_part)
        
        if 'memories' in data:
            memories = data['memories']
            print(f"\n✅ Found {len(memories)} memories:")
            for j, mem in enumerate(memories, 1):
                if isinstance(mem, dict):
                    memory_text = mem.get('memory', str(mem))
                else:
                    memory_text = str(mem)
                print(f"  {j}. {memory_text[:100]}{'...' if len(memory_text) > 100 else ''}")
        else:
            print(f"\n⚠️  Unexpected response format: {list(data.keys())}")
    except Exception as e:
        print(f"\n❌ Error parsing response: {e}")

print(f"\n{'='*60}")
print("\n✅ Retrieve endpoint test complete!")
