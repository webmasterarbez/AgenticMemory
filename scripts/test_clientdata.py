#!/usr/bin/env python3
"""
Test script for ClientData endpoint workspace secret authentication
Tests memory retrieval for pre-call personalization
"""

import json
import requests
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
CLIENTDATA_URL = os.getenv('ELEVENLABS_CLIENT_DATA_URL')
WORKSPACE_KEY = os.getenv('ELEVENLABS_WORKSPACE_KEY')

# Validate required environment variables
if not CLIENTDATA_URL:
    print("❌ ERROR: ELEVENLABS_CLIENT_DATA_URL not found in .env file")
    sys.exit(1)

if not WORKSPACE_KEY:
    print("❌ ERROR: ELEVENLABS_WORKSPACE_KEY not found in .env file")
    sys.exit(1)

# Validate URL format
if not CLIENTDATA_URL.startswith('https://'):
    print(f"❌ ERROR: Invalid CLIENTDATA_URL format: {CLIENTDATA_URL}")
    print("   URL must start with 'https://'")
    sys.exit(1)

# Validate workspace key format
if not WORKSPACE_KEY.startswith('wsec_'):
    print(f"❌ ERROR: Invalid WORKSPACE_KEY format: {WORKSPACE_KEY}")
    print("   Key must start with 'wsec_'")
    sys.exit(1)

# Test payload for client data request
payload = {
    "caller_id": "+16129782029",
    "agent_id": "agent_01jxbrc1trfxev5sdp5xk4ra67", 
    "called_number": "+16123241623",
    "call_sid": "test-call-123"
}

print(f"\n=== Testing ClientData Endpoint ===")
print(f"URL: {CLIENTDATA_URL}")
print(f"Caller ID: {payload['caller_id']}")
print(f"Agent ID: {payload['agent_id']}")

# Test 1: Valid workspace key
print(f"\n--- Test 1: Valid Workspace Key ---")
headers = {
    "Content-Type": "application/json",
    "X-Workspace-Key": WORKSPACE_KEY
}

try:
    response = requests.post(CLIENTDATA_URL, json=payload, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: Authentication passed!")
        
        # Parse response
        data = response.json()
        print(f"Response Type: {data.get('type', 'unknown')}")
        
        # Check dynamic variables
        dynamic_vars = data.get('dynamic_variables', {})
        print(f"\nDynamic Variables:")
        for key, value in dynamic_vars.items():
            print(f"  {key}: {value}")
        
        # Check conversation config override (memory context)
        config_override = data.get('conversation_config_override', {})
        agent_config = config_override.get('agent', {})
        prompt_config = agent_config.get('prompt', {})
        memory_context = prompt_config.get('prompt', '')
        
        if memory_context:
            print(f"\n📝 Memory Context Preview:")
            print(f"{memory_context[:300]}...")
            print(f"\nTotal context length: {len(memory_context)} characters")
            
            # Count memories mentioned
            factual_count = memory_context.count("1.") + memory_context.count("2.") + memory_context.count("3.")
            print(f"Factual memories found: ~{factual_count}")
            
            if "Previous Conversation Context" in memory_context:
                print("✅ Semantic memories included")
            else:
                print("ℹ️  No semantic memories found")
        else:
            print("ℹ️  No memory context found (new caller)")
            
    else:
        print(f"❌ FAILED: Expected 200, got {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: Missing workspace key
print(f"\n--- Test 2: Missing Workspace Key ---")
try:
    response = requests.post(CLIENTDATA_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 401:
        print("✅ SUCCESS: Correctly rejected unauthorized request")
    else:
        print(f"⚠️  Expected 401, got {response.status_code}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 3: Invalid workspace key
print(f"\n--- Test 3: Invalid Workspace Key ---")
invalid_headers = {
    "Content-Type": "application/json",
    "X-Workspace-Key": "invalid-key-123"
}

try:
    response = requests.post(CLIENTDATA_URL, json=payload, headers=invalid_headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 401:
        print("✅ SUCCESS: Correctly rejected invalid key")
    else:
        print(f"⚠️  Expected 401, got {response.status_code}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 4: Missing caller_id
print(f"\n--- Test 4: Missing caller_id ---")
invalid_payload = {
    "agent_id": "agent_01jxbrc1trfxev5sdp5xk4ra67",
    "called_number": "+16123241623"
}

try:
    response = requests.post(CLIENTDATA_URL, json=invalid_payload, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 400:
        print("✅ SUCCESS: Correctly rejected missing caller_id")
    else:
        print(f"⚠️  Expected 400, got {response.status_code}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print(f"\n=== Test Complete ===")
print(f"\n💡 This endpoint should be configured in ElevenLabs as:")
print(f"   - Conversation Initiation webhook URL: {CLIENTDATA_URL}")
print(f"   - Header: X-Workspace-Key: {WORKSPACE_KEY}")
print(f"\n📋 Expected behavior:")
print(f"   - Returns personalized memory context for agent prompts")
print(f"   - Provides dynamic variables for call personalization")
print(f"   - Authenticates via workspace key validation")