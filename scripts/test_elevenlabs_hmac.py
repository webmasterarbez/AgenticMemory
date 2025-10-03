#!/usr/bin/env python3
"""
Test the HMAC authentication with ElevenLabs signature format
"""

import json
import hmac
import hashlib
import time
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
WEBHOOK_URL = os.getenv('ELEVENLABS_POST_CALL_URL')
TEST_HMAC_KEY = os.getenv('ELEVENLABS_HMAC_KEY')

# Validate required environment variables
if not WEBHOOK_URL:
    print("❌ ERROR: ELEVENLABS_POST_CALL_URL not found in .env file")
    sys.exit(1)

if not TEST_HMAC_KEY:
    print("❌ ERROR: ELEVENLABS_HMAC_KEY not found in .env file")
    sys.exit(1)

# Validate URL format
if not WEBHOOK_URL.startswith('https://'):
    print(f"❌ ERROR: Invalid WEBHOOK_URL format: {WEBHOOK_URL}")
    print("   URL must start with 'https://'")
    sys.exit(1)

# Validate HMAC key format
if not TEST_HMAC_KEY.startswith('wsec_'):
    print(f"❌ ERROR: Invalid HMAC_KEY format: {TEST_HMAC_KEY}")
    print("   Key must start with 'wsec_'")
    sys.exit(1)

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

def test_elevenlabs_hmac():
    """Test with correct ElevenLabs signature format"""
    
    # Test payload with required metadata structure
    test_payload = {
        "conversation_id": "conv_test123",
        "agent_id": "agent_test456", 
        "call_successful": True,
        "call_duration": 45,
        "transcript": "Hello, I need help with my account. Thank you for the assistance.",
        "transcript_with_timestamps": [
            {"speaker": "user", "text": "Hello, I need help with my account", "timestamp": "2025-09-30T13:00:00Z"},
            {"speaker": "agent", "text": "I'd be happy to help you with your account", "timestamp": "2025-09-30T13:00:15Z"}
        ],
        "metadata": {
            "caller_id": "+16129782029"
        }
    }
    
    payload_json = json.dumps(test_payload, separators=(',', ':'))
    current_timestamp = str(int(time.time()))
    
    print("=== ElevenLabs HMAC Authentication Test ===\n")
    
    # Test 1: Valid ElevenLabs signature format
    print("Test 1: Valid ElevenLabs signature format")
    elevenlabs_signature = generate_elevenlabs_signature(payload_json, current_timestamp, TEST_HMAC_KEY)
    
    headers = {
        "Content-Type": "application/json",
        "ElevenLabs-Signature": elevenlabs_signature
    }
    
    print(f"Signature: {elevenlabs_signature}")
    print(f"Payload: {payload_json}")
    print(f"Timestamp: {current_timestamp}")
    
    try:
        response = requests.post(WEBHOOK_URL, json=test_payload, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 2: Invalid signature  
    print("Test 2: Invalid signature")
    invalid_signature = "t=1234567890,v0=invalid_signature_hash"
    
    headers_invalid = {
        "Content-Type": "application/json", 
        "ElevenLabs-Signature": invalid_signature
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=test_payload, headers=headers_invalid, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 3: Old timestamp (should be rejected)
    print("Test 3: Old timestamp (should be rejected)")
    old_timestamp = str(int(time.time()) - 2000)  # 33+ minutes ago
    old_signature = generate_elevenlabs_signature(payload_json, old_timestamp, TEST_HMAC_KEY)
    
    headers_old = {
        "Content-Type": "application/json",
        "ElevenLabs-Signature": old_signature
    }
    
    print(f"Old signature: {old_signature}")
    
    try:
        response = requests.post(WEBHOOK_URL, json=test_payload, headers=headers_old, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_elevenlabs_hmac()