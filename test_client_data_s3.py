#!/usr/bin/env python3
"""
Test script for ClientData Lambda function with S3 storage verification.

Tests:
1. Webhook payload handling
2. Memory retrieval for known caller
3. Memory retrieval for new caller
4. Personalized greeting generation
5. S3 storage of received and response payloads
6. Error handling
"""

import json
import requests
import boto3
import time
from datetime import datetime

# Configuration
CLIENT_DATA_URL = "https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data"
S3_BUCKET_NAME = "elevenlabs-agentic-memory-424875385161-us-east-1"

# Test data
KNOWN_CALLER = "+16129782029"  # Stefan - has existing memories
NEW_CALLER = "+15555551234"    # No memories
AGENT_ID = "agent_4301k6n146bgfs2tqtq5nhejw0r7"
CALLED_NUMBER = "+17205752470"

# Initialize S3 client
s3_client = boto3.client('s3')


def print_header(text):
    """Print formatted test header."""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")


def print_result(test_name, passed, details=""):
    """Print test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"    {details}")


def verify_s3_files(caller_id, call_sid, max_wait=10):
    """
    Verify that both received.json and response.json were saved to S3.
    
    Args:
        caller_id: Caller phone number
        call_sid: Call SID
        max_wait: Maximum seconds to wait for files
        
    Returns:
        tuple: (success, received_content, response_content)
    """
    sanitized_caller = caller_id.lstrip('+')
    prefix = f"client-data/{sanitized_caller}/"
    
    # Wait for files to appear (S3 eventual consistency)
    for attempt in range(max_wait):
        try:
            # List objects with the call_sid in the path
            response = s3_client.list_objects_v2(
                Bucket=S3_BUCKET_NAME,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                time.sleep(1)
                continue
            
            # Find the directory with this call_sid
            received_key = None
            response_key = None
            
            for obj in response['Contents']:
                key = obj['Key']
                if call_sid in key:
                    if key.endswith('received.json'):
                        received_key = key
                    elif key.endswith('response.json'):
                        response_key = key
            
            # If both files found, download and return
            if received_key and response_key:
                received_obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=received_key)
                received_content = json.loads(received_obj['Body'].read())
                
                response_obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=response_key)
                response_content = json.loads(response_obj['Body'].read())
                
                print(f"    Found S3 files:")
                print(f"    - {received_key}")
                print(f"    - {response_key}")
                
                return True, received_content, response_content
            
            time.sleep(1)
            
        except Exception as e:
            print(f"    Error checking S3: {str(e)}")
            time.sleep(1)
    
    return False, None, None


def test_known_caller():
    """Test webhook with known caller (Stefan)."""
    print_header("Test 1: Known Caller with Memories")
    
    call_sid = f"CA_test_known_{int(time.time())}"
    payload = {
        "caller_id": KNOWN_CALLER,
        "agent_id": AGENT_ID,
        "called_number": CALLED_NUMBER,
        "call_sid": call_sid
    }
    
    print(f"Sending request for known caller: {KNOWN_CALLER}")
    print(f"Call SID: {call_sid}")
    
    try:
        response = requests.post(
            CLIENT_DATA_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print_result("HTTP Status", False, f"Expected 200, got {response.status_code}")
            return False
        
        print_result("HTTP Status", True, "200 OK")
        
        # Parse response
        data = response.json()
        
        # Verify response structure
        print("\nVerifying response structure...")
        
        checks = [
            (data.get('type') == 'conversation_initiation_client_data', "Response type"),
            ('dynamic_variables' in data, "Dynamic variables present"),
            ('conversation_config_override' in data, "Config override present"),
            (data['dynamic_variables'].get('caller_id') == KNOWN_CALLER, "Caller ID matches"),
            (int(data['dynamic_variables'].get('memory_count', 0)) > 0, "Has memories"),
            (data['dynamic_variables'].get('returning_caller') == 'yes', "Recognized as returning caller"),
            ('caller_name' in data['dynamic_variables'], "Caller name extracted"),
            ('first_message' in data['conversation_config_override']['agent'], "First message present"),
        ]
        
        all_passed = True
        for check, description in checks:
            print_result(description, check)
            if not check:
                all_passed = False
        
        # Check for personalized greeting
        first_message = data['conversation_config_override']['agent'].get('first_message', '')
        caller_name = data['dynamic_variables'].get('caller_name', '')
        
        if caller_name and caller_name in first_message:
            print_result("Personalized greeting", True, f"Greeting includes name: {caller_name}")
        else:
            print_result("Personalized greeting", False, f"Name '{caller_name}' not in greeting")
            all_passed = False
        
        # Verify S3 storage
        print("\nVerifying S3 storage...")
        s3_success, received_s3, response_s3 = verify_s3_files(KNOWN_CALLER, call_sid)
        
        if s3_success:
            print_result("S3 Storage", True, "Both files saved successfully")
            
            # Verify received payload matches what we sent
            received_matches = (
                received_s3.get('caller_id') == payload['caller_id'] and
                received_s3.get('call_sid') == payload['call_sid']
            )
            print_result("S3 received.json content", received_matches, 
                        "Payload matches request" if received_matches else "Payload mismatch")
            
            # Verify response payload matches what we received
            response_matches = (
                response_s3.get('type') == data['type'] and
                response_s3.get('dynamic_variables') == data['dynamic_variables']
            )
            print_result("S3 response.json content", response_matches,
                        "Payload matches response" if response_matches else "Payload mismatch")
        else:
            print_result("S3 Storage", False, "Files not found in S3")
            all_passed = False
        
        print(f"\n{'='*80}")
        print(f"Test 1 Summary: {'✅ PASSED' if all_passed else '❌ FAILED'}")
        print(f"{'='*80}\n")
        
        return all_passed
        
    except Exception as e:
        print_result("Request", False, f"Error: {str(e)}")
        return False


def test_new_caller():
    """Test webhook with new caller (no memories)."""
    print_header("Test 2: New Caller without Memories")
    
    call_sid = f"CA_test_new_{int(time.time())}"
    payload = {
        "caller_id": NEW_CALLER,
        "agent_id": AGENT_ID,
        "called_number": CALLED_NUMBER,
        "call_sid": call_sid
    }
    
    print(f"Sending request for new caller: {NEW_CALLER}")
    print(f"Call SID: {call_sid}")
    
    try:
        response = requests.post(
            CLIENT_DATA_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print_result("HTTP Status", False, f"Expected 200, got {response.status_code}")
            return False
        
        print_result("HTTP Status", True, "200 OK")
        
        # Parse response
        data = response.json()
        
        # Verify response for new caller
        print("\nVerifying response structure...")
        
        checks = [
            (data.get('type') == 'conversation_initiation_client_data', "Response type"),
            (data['dynamic_variables'].get('memory_count') == '0', "Memory count is 0"),
            (data['dynamic_variables'].get('returning_caller') == 'no', "Recognized as new caller"),
            ('caller_name' not in data['dynamic_variables'] or data['dynamic_variables']['caller_name'] == '', 
             "No caller name (new caller)"),
        ]
        
        all_passed = True
        for check, description in checks:
            print_result(description, check)
            if not check:
                all_passed = False
        
        # Check for generic greeting
        first_message = data['conversation_config_override']['agent'].get('first_message', '')
        is_generic = 'welcome' in first_message.lower() or 'hello' in first_message.lower()
        print_result("Generic greeting", is_generic, 
                    "Generic greeting for new caller" if is_generic else "Greeting not generic")
        
        # Verify S3 storage
        print("\nVerifying S3 storage...")
        s3_success, received_s3, response_s3 = verify_s3_files(NEW_CALLER, call_sid)
        
        if s3_success:
            print_result("S3 Storage", True, "Both files saved successfully")
        else:
            print_result("S3 Storage", False, "Files not found in S3")
            all_passed = False
        
        print(f"\n{'='*80}")
        print(f"Test 2 Summary: {'✅ PASSED' if all_passed else '❌ FAILED'}")
        print(f"{'='*80}\n")
        
        return all_passed
        
    except Exception as e:
        print_result("Request", False, f"Error: {str(e)}")
        return False


def test_missing_caller_id():
    """Test error handling for missing caller_id."""
    print_header("Test 3: Error Handling - Missing caller_id")
    
    payload = {
        "agent_id": AGENT_ID,
        "called_number": CALLED_NUMBER,
        "call_sid": "CA_test_error"
    }
    
    print("Sending request without caller_id...")
    
    try:
        response = requests.post(
            CLIENT_DATA_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        # Should return 400 Bad Request
        if response.status_code == 400:
            print_result("Error Status Code", True, "400 Bad Request as expected")
            
            data = response.json()
            has_error = 'error' in data
            print_result("Error Message Present", has_error, 
                        f"Error: {data.get('error', 'N/A')}" if has_error else "No error message")
            
            print(f"\n{'='*80}")
            print(f"Test 3 Summary: ✅ PASSED")
            print(f"{'='*80}\n")
            return True
        else:
            print_result("Error Status Code", False, f"Expected 400, got {response.status_code}")
            print(f"\n{'='*80}")
            print(f"Test 3 Summary: ❌ FAILED")
            print(f"{'='*80}\n")
            return False
        
    except Exception as e:
        print_result("Request", False, f"Error: {str(e)}")
        return False


def test_s3_listing():
    """Test S3 listing functionality."""
    print_header("Test 4: S3 Bucket Listing")
    
    try:
        # List recent client-data entries
        print(f"Listing recent entries in s3://{S3_BUCKET_NAME}/client-data/")
        
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix='client-data/',
            MaxKeys=20
        )
        
        if 'Contents' not in response:
            print_result("S3 Listing", False, "No objects found")
            return False
        
        print_result("S3 Listing", True, f"Found {len(response['Contents'])} objects")
        
        # Group by caller
        callers = {}
        for obj in response['Contents']:
            key = obj['Key']
            parts = key.split('/')
            if len(parts) >= 2:
                caller = parts[1]
                if caller not in callers:
                    callers[caller] = []
                callers[caller].append(key)
        
        print(f"\nFound data for {len(callers)} caller(s):")
        for caller, files in callers.items():
            print(f"\n  Caller: {caller}")
            print(f"  Files: {len(files)}")
            for file in files[:4]:  # Show first 4 files
                print(f"    - {file}")
            if len(files) > 4:
                print(f"    ... and {len(files) - 4} more")
        
        print(f"\n{'='*80}")
        print(f"Test 4 Summary: ✅ PASSED")
        print(f"{'='*80}\n")
        return True
        
    except Exception as e:
        print_result("S3 Listing", False, f"Error: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("  CLIENT DATA ENDPOINT TEST SUITE")
    print("  Testing webhook handling, memory retrieval, and S3 storage")
    print("="*80)
    
    start_time = time.time()
    
    results = {
        "Known Caller Test": test_known_caller(),
        "New Caller Test": test_new_caller(),
        "Error Handling Test": test_missing_caller_id(),
        "S3 Listing Test": test_s3_listing(),
    }
    
    elapsed = time.time() - start_time
    
    # Final summary
    print("\n" + "="*80)
    print("  FINAL SUMMARY")
    print("="*80)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*80}")
    print(f"  Tests Passed: {passed}/{total}")
    print(f"  Success Rate: {(passed/total)*100:.1f}%")
    print(f"  Duration: {elapsed:.2f}s")
    print(f"{'='*80}\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
