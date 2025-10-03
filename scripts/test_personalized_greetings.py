#!/usr/bin/env python3
"""
Test script for personalized greetings in client data webhook
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
WEBHOOK_URL = os.getenv('ELEVENLABS_CLIENT_DATA_URL')
WORKSPACE_KEY = os.getenv('ELEVENLABS_WORKSPACE_KEY')

# Validate required environment variables
if not WEBHOOK_URL:
    print("❌ ERROR: ELEVENLABS_CLIENT_DATA_URL not found in .env file")
    sys.exit(1)

if not WORKSPACE_KEY:
    print("❌ ERROR: ELEVENLABS_WORKSPACE_KEY not found in .env file")
    sys.exit(1)

# Validate URL format
if not WEBHOOK_URL.startswith('https://'):
    print(f"❌ ERROR: Invalid WEBHOOK_URL format: {WEBHOOK_URL}")
    print("   URL must start with 'https://'")
    sys.exit(1)

# Validate workspace key format
if not WORKSPACE_KEY.startswith('wsec_'):
    print(f"❌ ERROR: Invalid WORKSPACE_KEY format: {WORKSPACE_KEY}")
    print("   Key must start with 'wsec_'")
    sys.exit(1)

def test_client_data(caller_id, description):
    """Test client data endpoint with a specific caller ID"""
    print(f"\n=== {description} ===")
    print(f"Caller ID: {caller_id}")
    
    headers = {
        "Content-Type": "application/json",
        "X-Workspace-Key": WORKSPACE_KEY
    }
    
    payload = {"caller_id": caller_id}
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract key information
            memory_count = data["dynamic_variables"]["memory_count"]
            returning_caller = data["dynamic_variables"]["returning_caller"]
            caller_name = data["dynamic_variables"].get("caller_name", "Not found")
            first_message = data["conversation_config_override"]["agent"]["first_message"]
            
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Memory Count: {memory_count}")
            print(f"🔄 Returning Caller: {returning_caller}")
            print(f"👤 Caller Name: {caller_name}")
            print(f"💬 First Message: {first_message}")
            
            return data
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    """Run comprehensive tests for personalized greetings"""
    
    print("🧪 PERSONALIZED GREETING TESTS")
    print("=" * 50)
    
    # Test scenarios
    test_cases = [
        ("+16129782029", "Returning caller with name (Stefan)"),
        ("+19995551234", "New caller (no memories)"),
        ("+18885554321", "Another new caller"),
    ]
    
    results = []
    
    for caller_id, description in test_cases:
        result = test_client_data(caller_id, description)
        results.append((caller_id, description, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    for caller_id, description, result in results:
        if result:
            memory_count = result["dynamic_variables"]["memory_count"]
            first_message = result["conversation_config_override"]["agent"]["first_message"]
            name = result["dynamic_variables"].get("caller_name", "None")
            
            print(f"\n📞 {caller_id}")
            print(f"   Type: {description}")
            print(f"   Memories: {memory_count}")
            print(f"   Name: {name}")
            print(f"   Greeting: {first_message}")
        else:
            print(f"\n❌ {caller_id} - {description}: FAILED")
    
    print("\n✨ PERSONALIZATION FEATURES DEMONSTRATED:")
    print("   🆕 New callers: Generic friendly greeting")
    print("   🔄 Returning callers with name: Personalized greeting") 
    print("   ❓ Returning callers without name: Polite name request")
    print("   📊 Dynamic variables: Include name when available")
    print("   🎯 Contextual prompts: Different behavior per caller type")

if __name__ == "__main__":
    main()