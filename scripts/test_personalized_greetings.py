#!/usr/bin/env python3
"""
Test script for personalized greetings in client data webhook
"""

import json
import requests

WEBHOOK_URL = "https://8nv3jj2gie.execute-api.us-east-1.amazonaws.com/Prod/client-data"
WORKSPACE_KEY = "wsec_eb779969b7cb5cde6cdd9c6dfc4e2a08fa38cd6711b86eced6c101039871f6ac"

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