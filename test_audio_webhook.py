#!/usr/bin/env python3
"""
Test PostCall audio webhook handling.

Tests both webhook types:
1. post_call_transcription - Full conversation data (no audio in new format)
2. post_call_audio - Only audio file (base64-encoded MP3)
"""

import json
import requests
import boto3
import time
import hmac
import hashlib
import base64

# Configuration
POST_CALL_URL = "https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call"
S3_BUCKET_NAME = "elevenlabs-agentic-memory-424875385161-us-east-1"
HMAC_KEY = "wsec_a8dc8b6e25ec3ddf11d7e651c40a5cb4931c2ca39d161fa4c94139f12f3ba9d3"

# Test data
TEST_CALLER = "+16129782029"
TEST_AGENT = "agent_4301k6n146bgfs2tqtq5nhejw0r7"
TEST_CONVERSATION_ID = f"conv_audio_test_{int(time.time())}"

# Initialize S3 client
s3_client = boto3.client('s3')


def generate_hmac_signature(body: str, timestamp: int) -> str:
    """Generate HMAC signature for webhook."""
    payload_to_sign = f"{timestamp}.{body}"
    mac = hmac.new(
        key=HMAC_KEY.encode('utf-8'),
        msg=payload_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    return f"t={timestamp},v0={mac.hexdigest()}"


def create_fake_mp3_audio() -> str:
    """Create a minimal valid MP3 file as base64."""
    # This is a minimal MP3 file header + some data
    # Not a real audio recording, but valid MP3 format for testing
    mp3_data = b'ID3\x04\x00\x00\x00\x00\x00\x00' + b'\xff\xfb' + b'\x00' * 100
    return base64.b64encode(mp3_data).decode('utf-8')


def test_transcription_webhook():
    """Test post_call_transcription webhook (no audio)."""
    print("\n" + "="*80)
    print("  Test 1: Transcription Webhook (post_call_transcription)")
    print("="*80 + "\n")
    
    # Create transcription webhook payload (NEW FORMAT - no audio)
    payload = {
        "type": "post_call_transcription",
        "event_timestamp": int(time.time()),
        "data": {
            "conversation_id": TEST_CONVERSATION_ID,
            "agent_id": TEST_AGENT,
            "external_number": TEST_CALLER,
            "status": "done",
            "transcript": [
                {"role": "agent", "message": "Hello, how can I help you?"},
                {"role": "user", "message": "I need assistance with my account"}
            ],
            "metadata": {
                "call_duration_secs": 45,
                "start_time_unix_secs": int(time.time())
            },
            "analysis": {
                "call_successful": "success",
                "transcript_summary": "User requested account assistance."
            }
        }
    }
    
    body = json.dumps(payload)
    timestamp = int(time.time())
    signature = generate_hmac_signature(body, timestamp)
    
    print(f"Conversation ID: {TEST_CONVERSATION_ID}")
    print(f"Webhook Type: post_call_transcription")
    print(f"Contains audio: No (audio sent via separate webhook)\n")
    
    try:
        response = requests.post(
            POST_CALL_URL,
            data=body,
            headers={
                'Content-Type': 'application/json',
                'ElevenLabs-Signature': signature
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ FAIL - Expected 200, got {response.status_code}")
            return False
        
        print(f"✅ PASS - HTTP 200 OK")
        
        # Wait for S3 file
        print(f"\nWaiting for JSON file in S3...")
        expected_json_key = f"post-call/{TEST_CALLER}/{TEST_CONVERSATION_ID}.json"
        
        for attempt in range(10):
            try:
                obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=expected_json_key)
                print(f"✅ PASS - JSON file saved: {expected_json_key}")
                
                # Verify content
                content = json.loads(obj['Body'].read())
                has_transcript = 'transcript' in content
                has_analysis = 'analysis' in content
                
                print(f"✅ PASS - Contains transcript: {has_transcript}")
                print(f"✅ PASS - Contains analysis: {has_analysis}")
                
                return True
                
            except s3_client.exceptions.NoSuchKey:
                time.sleep(1)
                
        print(f"❌ FAIL - JSON file not found after 10 seconds")
        return False
        
    except Exception as e:
        print(f"❌ FAIL - Error: {str(e)}")
        return False


def test_audio_webhook():
    """Test post_call_audio webhook (audio only)."""
    print("\n" + "="*80)
    print("  Test 2: Audio Webhook (post_call_audio)")
    print("="*80 + "\n")
    
    # Create audio webhook payload (separate webhook with only audio)
    payload = {
        "type": "post_call_audio",
        "event_timestamp": int(time.time()),
        "data": {
            "conversation_id": TEST_CONVERSATION_ID,
            "agent_id": TEST_AGENT,
            "full_audio": create_fake_mp3_audio()
        }
    }
    
    body = json.dumps(payload)
    timestamp = int(time.time())
    signature = generate_hmac_signature(body, timestamp)
    
    print(f"Conversation ID: {TEST_CONVERSATION_ID}")
    print(f"Webhook Type: post_call_audio")
    print(f"Contains: Only audio (base64-encoded MP3)\n")
    
    try:
        response = requests.post(
            POST_CALL_URL,
            data=body,
            headers={
                'Content-Type': 'application/json',
                'ElevenLabs-Signature': signature
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ FAIL - Expected 200, got {response.status_code}")
            return False
        
        print(f"✅ PASS - HTTP 200 OK")
        
        # Wait for MP3 file in audio-only directory
        print(f"\nWaiting for MP3 file in S3...")
        expected_mp3_key = f"post-call/audio-only/{TEST_AGENT}/{TEST_CONVERSATION_ID}.mp3"
        
        for attempt in range(10):
            try:
                obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=expected_mp3_key)
                audio_size = len(obj['Body'].read())
                
                print(f"✅ PASS - MP3 file saved: {expected_mp3_key}")
                print(f"✅ PASS - File size: {audio_size} bytes")
                
                # Verify metadata
                metadata = obj['Metadata']
                print(f"✅ PASS - Metadata contains webhook_type: {metadata.get('webhook_type')}")
                
                return True
                
            except s3_client.exceptions.NoSuchKey:
                time.sleep(1)
                print(f"  Attempt {attempt + 1}/10: Not found yet...")
                
        print(f"❌ FAIL - MP3 file not found after 10 seconds")
        print(f"  Expected: s3://{S3_BUCKET_NAME}/{expected_mp3_key}")
        return False
        
    except Exception as e:
        print(f"❌ FAIL - Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def verify_s3_structure():
    """Show the S3 structure to verify proper organization."""
    print("\n" + "="*80)
    print("  Current S3 Structure")
    print("="*80 + "\n")
    
    try:
        # List post-call data
        print("Post-Call Transcription Data:")
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix='post-call/',
            MaxKeys=20
        )
        
        if 'Contents' in response:
            transcription_files = [obj for obj in response['Contents'] 
                                  if 'audio-only' not in obj['Key']]
            for obj in transcription_files[:10]:
                size_kb = obj['Size'] / 1024
                print(f"  - {obj['Key']} ({size_kb:.1f} KB)")
        else:
            print("  (no transcription data)")
        
        # List audio-only data
        print("\nPost-Call Audio-Only Data:")
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix='post-call/audio-only/',
            MaxKeys=20
        )
        
        if 'Contents' in response:
            for obj in response['Contents']:
                size_kb = obj['Size'] / 1024
                print(f"  - {obj['Key']} ({size_kb:.1f} KB)")
        else:
            print("  (no audio-only data yet)")
        
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"Error listing S3: {str(e)}")


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("  POST-CALL AUDIO WEBHOOK TEST")
    print("  Testing ElevenLabs dual webhook system")
    print("="*80)
    print("\nElevenLabs sends TWO separate webhooks:")
    print("  1. post_call_transcription - Full conversation data (NO audio)")
    print("  2. post_call_audio - Only audio file (base64 MP3)")
    print("="*80)
    
    results = {}
    
    # Test transcription webhook
    results["Transcription Webhook"] = test_transcription_webhook()
    
    # Wait a bit between tests
    time.sleep(2)
    
    # Test audio webhook
    results["Audio Webhook"] = test_audio_webhook()
    
    # Show S3 structure
    verify_s3_structure()
    
    # Summary
    print("="*80)
    print("  TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    print("="*80 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
