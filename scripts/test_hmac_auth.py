#!/usr/bin/env python3
"""
Test script for HMAC authentication of the post-call webhook
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

def generate_hmac_signature(payload, timestamp, secret_key):
    """Generate HMAC signature for ElevenLabs webhook"""
    # Create the string to sign: timestamp + method + path + body
    method = "POST"
    path = "/Prod/post-call"
    message = f"{timestamp}{method}{path}{payload}"
    
    # Generate HMAC-SHA256 signature
    signature = hmac.new(
        key=secret_key.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return signature

def test_hmac_authentication():
    """Test various HMAC authentication scenarios"""
    
    # Test payload - minimal valid post-call data
    test_payload = {
        "conversation_id": "conv_test123",
        "user_id": "+16129782029",
        "agent_id": "agent_test456",
        "call_successful": True,
        "call_duration_seconds": 45,
        "transcript": "Hello, I need help with my account. Thank you for the assistance.",
        "transcript_with_timestamps": [
            {"speaker": "user", "text": "Hello, I need help with my account", "timestamp": "2025-09-30T13:00:00Z"},
            {"speaker": "agent", "text": "I'd be happy to help you with your account", "timestamp": "2025-09-30T13:00:15Z"},
            {"speaker": "user", "text": "Thank you for the assistance", "timestamp": "2025-09-30T13:00:30Z"}
        ]
    }
    
    payload_json = json.dumps(test_payload, separators=(',', ':'))
    current_timestamp = str(int(time.time()))
    
    print("=== HMAC Authentication Tests ===\n")
    
    # Test 1: Valid HMAC signature
    print("Test 1: Valid HMAC signature (should return 200)")
    valid_signature = generate_hmac_signature(payload_json, current_timestamp, TEST_HMAC_KEY)
    
    headers = {
        "Content-Type": "application/json",
        "xi-signature": valid_signature,
        "xi-timestamp": current_timestamp
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=test_payload, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Missing signature
    print("Test 2: Missing HMAC signature (should return 401)")
    headers_no_sig = {
        "Content-Type": "application/json",
        "xi-timestamp": current_timestamp
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=test_payload, headers=headers_no_sig, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Invalid signature
    print("Test 3: Invalid HMAC signature (should return 401)")
    invalid_signature = "invalid_signature_123456789"
    
    headers_invalid = {
        "Content-Type": "application/json",
        "xi-signature": invalid_signature,
        "xi-timestamp": current_timestamp
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=test_payload, headers=headers_invalid, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 4: Old timestamp (should return 401)
    print("Test 4: Old timestamp - 10 minutes ago (should return 401)")
    old_timestamp = str(int(time.time()) - 600)  # 10 minutes ago
    old_signature = generate_hmac_signature(payload_json, old_timestamp, TEST_HMAC_KEY)
    
    headers_old = {
        "Content-Type": "application/json",
        "xi-signature": old_signature,
        "xi-timestamp": old_timestamp
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=test_payload, headers=headers_old, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    print("=== Test Information ===")
    print(f"Test HMAC Key: {TEST_HMAC_KEY}")
    print(f"Webhook URL: {WEBHOOK_URL}")
    print(f"Timestamp: {current_timestamp}")
    print(f"Valid Signature: {valid_signature}")
    print(f"Payload: {payload_json}")

if __name__ == "__main__":
    test_hmac_authentication()