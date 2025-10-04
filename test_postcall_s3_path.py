#!/usr/bin/env python3
"""
Test PostCall S3 path structure update.

Verifies that post-call data is saved to:
s3://elevenlabs-agentic-memory-{account}-{region}/post-call/{caller_id}/{conversation_id}.json
"""

import json
import requests
import boto3
import time
import hmac
import hashlib

# Configuration
POST_CALL_URL = "https://knh457q7q7.execute-api.us-east-1.amazonaws.com/Prod/post-call"
S3_BUCKET_NAME = "elevenlabs-agentic-memory-424875385161-us-east-1"
HMAC_KEY = "wsec_a8dc8b6e25ec3ddf11d7e651c40a5cb4931c2ca39d161fa4c94139f12f3ba9d3"

# Test data
TEST_CALLER = "+16129782029"
TEST_CONVERSATION_ID = f"conv_test_{int(time.time())}"

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


def test_post_call_s3_path():
    """Test that PostCall saves to correct S3 path."""
    print("\n" + "="*80)
    print("  Testing PostCall S3 Path Structure")
    print("="*80 + "\n")
    
    # Create test payload
    payload = {
        "conversation_id": TEST_CONVERSATION_ID,
        "external_number": TEST_CALLER,
        "agent_id": "agent_4301k6n146bgfs2tqtq5nhejw0r7",
        "analysis": {
            "call_successful": True,
            "transcript_summary": "Test conversation for S3 path validation"
        },
        "transcript": [
            {"role": "agent", "message": "Hello, this is a test"},
            {"role": "user", "message": "Testing S3 path structure"}
        ],
        "metadata": {
            "duration_seconds": 30,
            "ended_reason": "user_hangup"
        }
    }
    
    body = json.dumps(payload)
    timestamp = int(time.time())
    signature = generate_hmac_signature(body, timestamp)
    
    print(f"Test Caller: {TEST_CALLER}")
    print(f"Conversation ID: {TEST_CONVERSATION_ID}")
    print(f"Expected S3 Path: post-call/{TEST_CALLER}/{TEST_CONVERSATION_ID}.json")
    print(f"\nSending POST request...")
    
    try:
        # Send request
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
            print(f"Response: {response.text}")
            return False
        
        print(f"✅ PASS - HTTP 200 OK")
        
        # Wait for S3 file to be created (async processing)
        print(f"\nWaiting for S3 file creation (max 15 seconds)...")
        
        expected_json_key = f"post-call/{TEST_CALLER}/{TEST_CONVERSATION_ID}.json"
        
        for attempt in range(15):
            try:
                # Try to get the object
                obj = s3_client.get_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=expected_json_key
                )
                
                # File found!
                print(f"✅ PASS - File found in S3")
                print(f"✅ PASS - Correct path: s3://{S3_BUCKET_NAME}/{expected_json_key}")
                
                # Verify content
                content = json.loads(obj['Body'].read())
                
                checks = [
                    (content.get('conversation_id') == TEST_CONVERSATION_ID, "Conversation ID matches"),
                    (content.get('external_number') == TEST_CALLER, "External number matches"),
                    ('transcript' in content, "Transcript present"),
                    ('analysis' in content, "Analysis present"),
                ]
                
                print("\nVerifying file content:")
                all_passed = True
                for check, description in checks:
                    status = "✅ PASS" if check else "❌ FAIL"
                    print(f"{status} - {description}")
                    if not check:
                        all_passed = False
                
                # Check metadata
                metadata = obj['Metadata']
                print(f"\nS3 Object Metadata:")
                print(f"  - external_number: {metadata.get('external_number')}")
                print(f"  - conversation_id: {metadata.get('conversation_id')}")
                print(f"  - timestamp: {metadata.get('timestamp')}")
                
                # Verify old path doesn't exist (without post-call/ prefix)
                old_json_key = f"{TEST_CALLER.lstrip('+')}/{TEST_CONVERSATION_ID}.json"
                try:
                    s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=old_json_key)
                    print(f"\n⚠️  WARNING - Old path still exists: {old_json_key}")
                except:
                    print(f"\n✅ PASS - Old path doesn't exist (as expected)")
                
                print("\n" + "="*80)
                print(f"  Test Summary: {'✅ ALL CHECKS PASSED' if all_passed else '❌ SOME CHECKS FAILED'}")
                print("="*80 + "\n")
                
                return all_passed
                
            except s3_client.exceptions.NoSuchKey:
                # File not found yet, wait and retry
                time.sleep(1)
                print(f"  Attempt {attempt + 1}/15: Not found yet, waiting...")
            except Exception as e:
                print(f"  Error checking S3: {str(e)}")
                time.sleep(1)
        
        # File not found after max attempts
        print(f"\n❌ FAIL - File not found after 15 seconds")
        print(f"Expected path: s3://{S3_BUCKET_NAME}/{expected_json_key}")
        
        # List what files exist for debugging
        print(f"\nListing files in post-call/{TEST_CALLER}/:")
        try:
            response = s3_client.list_objects_v2(
                Bucket=S3_BUCKET_NAME,
                Prefix=f"post-call/{TEST_CALLER}/"
            )
            if 'Contents' in response:
                for obj in response['Contents']:
                    print(f"  - {obj['Key']}")
            else:
                print(f"  (no files found)")
        except Exception as e:
            print(f"  Error listing: {str(e)}")
        
        return False
        
    except Exception as e:
        print(f"❌ FAIL - Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def list_s3_structure():
    """List current S3 structure to show the new organization."""
    print("\n" + "="*80)
    print("  Current S3 Structure")
    print("="*80 + "\n")
    
    try:
        # List post-call entries
        print("Post-Call Data:")
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix='post-call/',
            MaxKeys=10
        )
        
        if 'Contents' in response:
            for obj in response['Contents']:
                size_kb = obj['Size'] / 1024
                print(f"  - {obj['Key']} ({size_kb:.1f} KB)")
        else:
            print("  (no post-call data yet)")
        
        # List client-data entries for comparison
        print("\nClient-Data (for comparison):")
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix='client-data/',
            MaxKeys=10
        )
        
        if 'Contents' in response:
            for obj in response['Contents']:
                size_kb = obj['Size'] / 1024
                print(f"  - {obj['Key']} ({size_kb:.1f} KB)")
        else:
            print("  (no client-data yet)")
        
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"Error listing S3: {str(e)}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("  POST-CALL S3 PATH STRUCTURE TEST")
    print("  Testing new path: post-call/{caller_id}/{conversation_id}.json")
    print("="*80)
    
    success = test_post_call_s3_path()
    list_s3_structure()
    
    exit(0 if success else 1)
