#!/usr/bin/env python3
"""
Test S3 storage functionality for post-call webhooks.

This script:
1. Sends a test post-call payload to the PostCall endpoint
2. Verifies JSON file is created in S3
3. Verifies MP3 file is created in S3 (if audio present)
4. Displays S3 file metadata
"""

import os
import sys
import json
import requests
import hmac
import hashlib
import time
import boto3
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Configuration
POST_CALL_URL = os.getenv("ELEVENLABS_POST_CALL_URL")
HMAC_KEY = os.getenv("ELEVENLABS_HMAC_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "elevenlabs-agentic-memory-424875385161-us-east-1")

# Test payload path
TEST_PAYLOAD_PATH = project_root / "test_data" / "conv_01jxd5y165f62a0v7gtr6bkg56.json"

def generate_hmac_signature(body: str) -> str:
    """Generate HMAC signature for webhook payload."""
    timestamp = str(int(time.time()))
    full_payload = f"{timestamp}.{body}"
    
    mac = hmac.new(
        key=HMAC_KEY.encode('utf-8'),
        msg=full_payload.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    
    signature = f"t={timestamp},v0={mac.hexdigest()}"
    return signature

def send_webhook(payload: dict) -> bool:
    """Send webhook to PostCall endpoint with HMAC signature."""
    body = json.dumps(payload)
    signature = generate_hmac_signature(body)
    
    headers = {
        'Content-Type': 'application/json',
        'ElevenLabs-Signature': signature
    }
    
    print(f"\n🚀 Sending webhook to: {POST_CALL_URL}")
    print(f"📦 Payload size: {len(body)} bytes")
    print(f"🔐 HMAC signature: {signature[:50]}...")
    
    response = requests.post(POST_CALL_URL, json=payload, headers=headers)
    
    print(f"📨 Response status: {response.status_code}")
    print(f"📝 Response body: {response.text}")
    
    return response.status_code == 200

def check_s3_files(external_number: str, conversation_id: str) -> dict:
    """Check if JSON and MP3 files exist in S3."""
    s3_client = boto3.client('s3')
    
    # Sanitize phone number
    sanitized_number = external_number.lstrip('+')
    
    json_key = f"{sanitized_number}/{conversation_id}.json"
    mp3_key = f"{sanitized_number}/{conversation_id}.mp3"
    
    results = {
        'json': None,
        'mp3': None
    }
    
    # Check JSON file
    try:
        print(f"\n🔍 Checking S3 for JSON: s3://{S3_BUCKET_NAME}/{json_key}")
        response = s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=json_key)
        results['json'] = {
            'exists': True,
            'size': response['ContentLength'],
            'content_type': response['ContentType'],
            'last_modified': response['LastModified'],
            'metadata': response.get('Metadata', {})
        }
        print(f"✅ JSON file found: {results['json']['size']} bytes")
        print(f"   Content-Type: {results['json']['content_type']}")
        print(f"   Last Modified: {results['json']['last_modified']}")
        print(f"   Metadata: {results['json']['metadata']}")
    except s3_client.exceptions.NoSuchKey:
        print(f"❌ JSON file not found")
        results['json'] = {'exists': False}
    except Exception as e:
        print(f"⚠️  Error checking JSON: {str(e)}")
        results['json'] = {'exists': False, 'error': str(e)}
    
    # Check MP3 file
    try:
        print(f"\n🔍 Checking S3 for MP3: s3://{S3_BUCKET_NAME}/{mp3_key}")
        response = s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=mp3_key)
        results['mp3'] = {
            'exists': True,
            'size': response['ContentLength'],
            'content_type': response['ContentType'],
            'last_modified': response['LastModified'],
            'metadata': response.get('Metadata', {})
        }
        print(f"✅ MP3 file found: {results['mp3']['size']} bytes")
        print(f"   Content-Type: {results['mp3']['content_type']}")
        print(f"   Last Modified: {results['mp3']['last_modified']}")
        print(f"   Metadata: {results['mp3']['metadata']}")
    except s3_client.exceptions.NoSuchKey:
        print(f"❌ MP3 file not found (may not be present in test payload)")
        results['mp3'] = {'exists': False}
    except Exception as e:
        print(f"⚠️  Error checking MP3: {str(e)}")
        results['mp3'] = {'exists': False, 'error': str(e)}
    
    return results

def main():
    """Main test function."""
    print("=" * 70)
    print("S3 STORAGE TEST - Post-Call Webhook")
    print("=" * 70)
    
    # Validate configuration
    if not POST_CALL_URL:
        print("❌ Error: ELEVENLABS_POST_CALL_URL not set in .env")
        return False
    
    if not HMAC_KEY:
        print("❌ Error: ELEVENLABS_HMAC_KEY not set in .env")
        return False
    
    # Load test payload
    if not TEST_PAYLOAD_PATH.exists():
        print(f"❌ Error: Test payload not found at {TEST_PAYLOAD_PATH}")
        return False
    
    print(f"📂 Loading test payload: {TEST_PAYLOAD_PATH}")
    with open(TEST_PAYLOAD_PATH, 'r') as f:
        payload = json.load(f)
    
    # Extract metadata from payload
    conversation_id = payload.get('conversation_id', 'unknown')
    metadata = payload.get('metadata', {})
    external_number = None
    
    if 'phone_call' in metadata:
        external_number = metadata['phone_call'].get('external_number')
    
    print(f"📞 Conversation ID: {conversation_id}")
    print(f"📱 External Number: {external_number}")
    
    if not external_number:
        print("⚠️  Warning: No external_number found in payload")
        print("   Using default: +15074595005")
        external_number = "+15074595005"
        # Add to payload
        if 'metadata' not in payload:
            payload['metadata'] = {}
        if 'phone_call' not in payload['metadata']:
            payload['metadata']['phone_call'] = {}
        payload['metadata']['phone_call']['external_number'] = external_number
    
    # Check if payload has audio
    has_audio = 'full_audio' in payload
    print(f"🎵 Audio present: {'Yes' if has_audio else 'No'}")
    
    # Send webhook
    print("\n" + "=" * 70)
    print("STEP 1: Send webhook to PostCall endpoint")
    print("=" * 70)
    
    success = send_webhook(payload)
    
    if not success:
        print("\n❌ Webhook failed. Cannot proceed with S3 verification.")
        return False
    
    # Wait for async processing
    print("\n⏳ Waiting 5 seconds for async S3 processing...")
    time.sleep(5)
    
    # Check S3 files
    print("\n" + "=" * 70)
    print("STEP 2: Verify files in S3")
    print("=" * 70)
    
    results = check_s3_files(external_number, conversation_id)
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    json_success = results['json'] and results['json'].get('exists', False)
    mp3_success = results['mp3'] and results['mp3'].get('exists', False)
    
    print(f"✅ Webhook sent: Success")
    print(f"{'✅' if json_success else '❌'} JSON file in S3: {'Success' if json_success else 'Failed'}")
    print(f"{'✅' if mp3_success else '⚠️ '} MP3 file in S3: {'Success' if mp3_success else 'Not found (may not be in test payload)'}")
    
    if json_success:
        print(f"\n📂 S3 Location:")
        sanitized_number = external_number.lstrip('+')
        print(f"   Bucket: {S3_BUCKET_NAME}")
        print(f"   JSON: {sanitized_number}/{conversation_id}.json")
        if mp3_success:
            print(f"   MP3:  {sanitized_number}/{conversation_id}.mp3")
    
    print("\n" + "=" * 70)
    
    return json_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
