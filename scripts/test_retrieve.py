#!/usr/bin/env python3
"""Test the Retrieve endpoint for semantic search"""
import json
import subprocess
import sys
import os
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    # Load .env from project root
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    print("⚠️  Warning: python-dotenv not installed. Install with: pip install python-dotenv")
    sys.exit(1)

# Configuration from .env
RETRIEVE_URL = os.getenv('ELEVENLABS_RETRIEVE_URL')

# Validate required environment variables
if not RETRIEVE_URL:
    print("❌ ERROR: ELEVENLABS_RETRIEVE_URL not found in .env file")
    sys.exit(1)

# Validate URL format
if not RETRIEVE_URL.startswith('https://'):
    print(f"❌ ERROR: Invalid RETRIEVE_URL format: {RETRIEVE_URL}")
    print("   URL must start with 'https://'")
    sys.exit(1)

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
