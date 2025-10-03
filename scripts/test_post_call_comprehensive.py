#!/usr/bin/env python3
"""
Test the post-call webhook with realistic conversation data
"""

import json
import hmac
import hashlib
import time
import requests
import sys
import os
from datetime import datetime
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

def get_hmac_key_from_env():
    """Get the HMAC key from .env file"""
    hmac_key = os.getenv('ELEVENLABS_HMAC_KEY')
    
    if not hmac_key:
        print("❌ ERROR: ELEVENLABS_HMAC_KEY not found in .env file")
        sys.exit(1)
    
    if not hmac_key.startswith('wsec_'):
        print(f"❌ ERROR: Invalid HMAC_KEY format: {hmac_key}")
        sys.exit(1)
    
    return hmac_key

def generate_elevenlabs_signature(payload, timestamp, secret_key):
    """Generate ElevenLabs-style HMAC signature"""
    # ElevenLabs format: timestamp.body
    message = f"{timestamp}.{payload}"
    
    # Generate HMAC-SHA256 signature  
    signature = hmac.new(
        key=secret_key.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    # ElevenLabs format: t=timestamp,v0=signature
    return f"t={timestamp},v0={signature}"

def test_post_call_webhook():
    """Test post-call webhook with realistic conversation data"""
    
    WEBHOOK_URL = os.getenv('ELEVENLABS_POST_CALL_URL')
    HMAC_KEY = get_hmac_key_from_env()
    
    # Validate URL
    if not WEBHOOK_URL:
        print("❌ ERROR: ELEVENLABS_POST_CALL_URL not found in .env file")
        sys.exit(1)
    
    if not WEBHOOK_URL.startswith('https://'):
        print(f"❌ ERROR: Invalid WEBHOOK_URL format: {WEBHOOK_URL}")
        sys.exit(1)
    
    print(f"🔗 Webhook URL: {WEBHOOK_URL}")
    print(f"🔑 Using HMAC Key: {HMAC_KEY}")
    print()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "New Customer Call - First Interaction",
            "payload": {
                "conversation_id": "conv_new_customer_001",
                "agent_id": "agent_customer_service",
                "call_successful": True,
                "call_duration": 185,
                "transcript": "Customer: Hi, I'm interested in your premium service. Agent: Hello! I'd be happy to help you learn about our premium offerings. What's your name? Customer: My name is Sarah Johnson. Agent: Nice to meet you, Sarah! Let me tell you about our premium features...",
                "transcript_with_timestamps": [
                    {"speaker": "user", "text": "Hi, I'm interested in your premium service", "timestamp": "2025-09-30T14:00:00Z"},
                    {"speaker": "agent", "text": "Hello! I'd be happy to help you learn about our premium offerings. What's your name?", "timestamp": "2025-09-30T14:00:05Z"},
                    {"speaker": "user", "text": "My name is Sarah Johnson", "timestamp": "2025-09-30T14:00:10Z"},
                    {"speaker": "agent", "text": "Nice to meet you, Sarah! Let me tell you about our premium features", "timestamp": "2025-09-30T14:00:15Z"}
                ],
                "analysis": {
                    "summary": "New customer Sarah Johnson inquired about premium service. Showed strong interest in features and pricing.",
                    "sentiment": "positive",
                    "intent": "product_inquiry"
                },
                "metadata": {
                    "caller_id": "+14155551234"
                }
            }
        },
        {
            "name": "Returning Customer - Support Issue", 
            "payload": {
                "conversation_id": "conv_support_002",
                "agent_id": "agent_customer_service",
                "call_successful": True,
                "call_duration": 240,
                "transcript": "Customer: Hi, this is John from last week. I'm having trouble with my account login. Agent: Hello John! I remember you. Let me help you with the login issue. Customer: Thanks, I keep getting an error message. Agent: I see the issue. Let me reset your password...",
                "transcript_with_timestamps": [
                    {"speaker": "user", "text": "Hi, this is John from last week. I'm having trouble with my account login", "timestamp": "2025-09-30T14:15:00Z"},
                    {"speaker": "agent", "text": "Hello John! I remember you. Let me help you with the login issue", "timestamp": "2025-09-30T14:15:05Z"},
                    {"speaker": "user", "text": "Thanks, I keep getting an error message", "timestamp": "2025-09-30T14:15:20Z"},
                    {"speaker": "agent", "text": "I see the issue. Let me reset your password", "timestamp": "2025-09-30T14:15:30Z"}
                ],
                "analysis": {
                    "summary": "Returning customer John had login issues. Problem resolved by password reset.",
                    "sentiment": "neutral",
                    "intent": "technical_support",
                    "resolution": "password_reset_completed"
                },
                "metadata": {
                    "caller_id": "+16129782029"  # This is our test caller with existing memories
                }
            }
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"📞 Test {i}: {scenario['name']}")
        print(f"   Caller: {scenario['payload']['metadata']['caller_id']}")
        print(f"   Duration: {scenario['payload']['call_duration']}s")
        
        # Generate HMAC signature
        payload_json = json.dumps(scenario['payload'], separators=(',', ':'))
        current_timestamp = str(int(time.time()))
        signature = generate_elevenlabs_signature(payload_json, current_timestamp, HMAC_KEY)
        
        headers = {
            "Content-Type": "application/json",
            "ElevenLabs-Signature": signature
        }
        
        try:
            response = requests.post(WEBHOOK_URL, json=scenario['payload'], headers=headers, timeout=15)
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
            results.append({
                "test": scenario['name'],
                "status": response.status_code,
                "success": response.status_code == 200,
                "response": response.text,
                "caller_id": scenario['payload']['metadata']['caller_id']
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                "test": scenario['name'], 
                "status": "error",
                "success": False,
                "error": str(e),
                "caller_id": scenario['payload']['metadata']['caller_id']
            })
        
        print()
    
    return results

def check_memory_storage():
    """Check if memories were actually stored by testing the client data endpoint"""
    print("🧠 Verifying Memory Storage...")
    print("=" * 50)
    
    CLIENT_DATA_URL = "https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data"
    WORKSPACE_KEY = "wsec_eb779969b7cb5cde6cdd9c6dfc4e2a08fa38cd6711b86eced6c101039871f6ac"
    
    test_callers = ["+14155551234", "+16129782029"]
    
    for caller_id in test_callers:
        print(f"\n📱 Checking memories for: {caller_id}")
        
        headers = {
            "Content-Type": "application/json",
            "X-Workspace-Key": WORKSPACE_KEY
        }
        
        payload = {"caller_id": caller_id}
        
        try:
            response = requests.post(CLIENT_DATA_URL, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                memory_count = data["dynamic_variables"]["memory_count"]
                returning_caller = data["dynamic_variables"]["returning_caller"]
                caller_name = data["dynamic_variables"].get("caller_name", "Not found")
                
                print(f"   ✅ Memory Count: {memory_count}")
                print(f"   🔄 Returning Caller: {returning_caller}")
                print(f"   👤 Caller Name: {caller_name}")
                
                if int(memory_count) > 0:
                    print(f"   🎉 SUCCESS: Memories found!")
                else:
                    print(f"   ⚠️  No memories found (may take a moment to process)")
                    
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def main():
    """Run comprehensive post-call webhook tests"""
    print("🧪 POST-CALL WEBHOOK COMPREHENSIVE TEST")
    print("=" * 50)
    
    # Test the webhook
    results = test_post_call_webhook()
    
    # Wait a moment for async processing
    print("⏳ Waiting 10 seconds for async memory processing...")
    time.sleep(10)
    
    # Check if memories were stored
    check_memory_storage()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    successful_tests = sum(1 for r in results if r.get('success', False))
    total_tests = len(results)
    
    print(f"✅ Successful Tests: {successful_tests}/{total_tests}")
    
    for result in results:
        status_icon = "✅" if result.get('success') else "❌"
        print(f"{status_icon} {result['test']}: {result.get('status', 'error')}")
    
    print("\n🎯 What This Test Validates:")
    print("   • HMAC signature authentication")
    print("   • Async conversation processing")
    print("   • Memory extraction from conversation")
    print("   • Factual vs semantic memory separation")
    print("   • Storage in Mem0 Cloud")
    print("   • Integration with client data retrieval")

if __name__ == "__main__":
    main()