"""
AgenticMemoriesPostCall Lambda Handler

Handles ElevenLabs Post-Call webhook asynchronously.
Stores factual and semantic memories in Mem0 after call completion.
Saves conversation JSON and audio MP3 to S3.
"""

import json
import os
import logging
import hmac
import hashlib
import time
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime

import boto3
from mem0 import MemoryClient

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Mem0 client outside handler for reuse across invocations
client = MemoryClient(
    api_key=os.environ['MEM0_API_KEY'],
    org_id=os.environ['MEM0_ORG_ID'],
    project_id=os.environ['MEM0_PROJECT_ID']
)

# Initialize S3 client outside handler for reuse
s3_client = boto3.client('s3')

HMAC_KEY = os.environ['ELEVENLABS_HMAC_KEY']
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']


def verify_hmac_signature(body: str, signature_header: str) -> bool:
    """
    Verify HMAC signature from ElevenLabs webhook.

    Format: t=timestamp,v0=hash
    The hash is the hex encoded sha256 HMAC signature of timestamp.request_body

    Args:
        body: Raw request body
        signature_header: ElevenLabs-Signature header value (format: t=timestamp,v0=hash)

    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Parse signature header: t=timestamp,v0=hash
        parts = signature_header.split(',')
        if len(parts) != 2:
            logger.error("Invalid signature format")
            return False

        timestamp = parts[0].split('=')[1]
        hmac_signature = parts[1]  # v0=hash

        # Validate timestamp (reject if older than 30 minutes)
        tolerance = int(time.time()) - 30 * 60
        if int(timestamp) < tolerance:
            logger.error("Signature timestamp too old")
            return False

        # Validate signature
        full_payload_to_sign = f"{timestamp}.{body}"
        mac = hmac.new(
            key=HMAC_KEY.encode('utf-8'),
            msg=full_payload_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        )
        expected_signature = 'v0=' + mac.hexdigest()

        return hmac.compare_digest(hmac_signature, expected_signature)

    except Exception as e:
        logger.error(f"Error verifying HMAC: {str(e)}", exc_info=True)
        return False


def save_to_s3(external_number: str, conversation_id: str, payload: Dict[str, Any]) -> None:
    """
    Save conversation JSON and audio MP3 to S3.

    Directory structure: {external_number}/{conversation_id}.json and .mp3

    Args:
        external_number: Caller's phone number (e.g., +15074595005)
        conversation_id: ElevenLabs conversation ID (e.g., conv_01jxd5y165f62a0v7gtr6bkg56)
        payload: Full webhook payload
    """
    try:
        # Sanitize external_number for S3 key (remove + prefix if present)
        sanitized_number = external_number.lstrip('+')
        
        # Save JSON payload
        json_key = f"{sanitized_number}/{conversation_id}.json"
        logger.info(f"Saving JSON to S3: s3://{S3_BUCKET_NAME}/{json_key}")
        
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=json_key,
            Body=json.dumps(payload, indent=2),
            ContentType='application/json',
            Metadata={
                'external_number': external_number,
                'conversation_id': conversation_id,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        logger.info(f"Successfully saved JSON for conversation {conversation_id}")

        # Save MP3 audio if present
        full_audio_base64 = payload.get('full_audio')
        if full_audio_base64:
            try:
                # Decode base64 audio to binary
                audio_binary = base64.b64decode(full_audio_base64)
                
                mp3_key = f"{sanitized_number}/{conversation_id}.mp3"
                logger.info(f"Saving MP3 to S3: s3://{S3_BUCKET_NAME}/{mp3_key} ({len(audio_binary)} bytes)")
                
                s3_client.put_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=mp3_key,
                    Body=audio_binary,
                    ContentType='audio/mpeg',
                    Metadata={
                        'external_number': external_number,
                        'conversation_id': conversation_id,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                )
                logger.info(f"Successfully saved MP3 for conversation {conversation_id}")
            except Exception as e:
                logger.error(f"Error saving MP3 to S3: {str(e)}", exc_info=True)
        else:
            logger.warning(f"No full_audio field found in payload for conversation {conversation_id}")

    except Exception as e:
        logger.error(f"Error saving to S3: {str(e)}", exc_info=True)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle ElevenLabs Post-Call webhook asynchronously.

    Args:
        event: API Gateway event with call payload
        context: Lambda context

    Returns:
        Immediate 200 OK response
    """
    # Return 200 OK immediately
    response = {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'status': 'ok'})
    }

    # Process asynchronously (errors are logged but don't affect response)
    try:
        # Get raw body for HMAC verification
        raw_body = event.get('body', '{}')
        headers = event.get('headers', {})
        signature_header = headers.get('elevenlabs-signature') or headers.get('ElevenLabs-Signature')

        # Verify HMAC signature
        if not signature_header:
            logger.error("Missing ElevenLabs-Signature header")
            return response

        if not verify_hmac_signature(raw_body, signature_header):
            logger.error("Invalid HMAC signature")
            return response

        # Parse payload
        payload = json.loads(raw_body)
        
        # Handle ElevenLabs formats:
        # Format 1 (array): [{"type": "post_call_transcription", "data": {...}}]
        # Format 2 (object): {"type": "post_call_transcription", "event_timestamp": ..., "data": {...}}
        if isinstance(payload, list) and len(payload) > 0:
            if 'data' in payload[0]:
                logger.info("Detected ElevenLabs array format, extracting data")
                payload = payload[0]['data']
        elif isinstance(payload, dict) and 'data' in payload and 'type' in payload:
            # Single object with type and data fields
            logger.info(f"Detected ElevenLabs object format (type={payload.get('type')}), extracting data")
            payload = payload['data']

        # Extract required fields
        conversation_id = payload.get('conversation_id', 'unknown')
        agent_id = payload.get('agent_id', 'unknown')
        
        # Get metadata - handle both formats
        metadata = payload.get('metadata', {})
        call_duration = metadata.get('call_duration_secs', payload.get('call_duration', 0))
        
        # Get transcript
        transcript = payload.get('transcript', [])
        
        # Get analysis - handle both formats
        analysis = payload.get('analysis', {})
        
        # Extract caller_id from multiple possible locations
        caller_id = None
        
        # 1. Try metadata.caller_id (direct format)
        caller_id = metadata.get('caller_id')
        
        # 2. Try metadata.phone_call.external_number (ElevenLabs format)
        if not caller_id and 'phone_call' in metadata:
            caller_id = metadata['phone_call'].get('external_number')
            logger.info(f"Extracted caller_id from metadata.phone_call.external_number: {caller_id}")
        
        # 3. Try conversation_initiation_client_data.dynamic_variables.system__caller_id
        if not caller_id and 'conversation_initiation_client_data' in payload:
            conv_init = payload['conversation_initiation_client_data']
            dvars = conv_init.get('dynamic_variables', {})
            caller_id = dvars.get('system__caller_id')
            if caller_id:
                logger.info(f"Extracted caller_id from conversation_initiation_client_data: {caller_id}")

        if not caller_id:
            logger.error("Missing caller_id in all expected locations")
            logger.error(f"Payload keys: {list(payload.keys())}")
            logger.error(f"Metadata keys: {list(metadata.keys())}")
            return response

        logger.info(f"Processing post-call data for user_id: {caller_id}")

        # Save to S3 (JSON and MP3)
        try:
            save_to_s3(caller_id, conversation_id, payload)
        except Exception as e:
            logger.error(f"Error saving to S3: {str(e)}", exc_info=True)
            # Continue processing - S3 failure shouldn't block memory storage

        # Prepare timestamp
        timestamp = datetime.utcnow().isoformat()

        # Prepare common metadata
        common_metadata = {
            'agent_id': agent_id,
            'conversation_id': conversation_id,
            'call_duration': call_duration,
            'timestamp': timestamp
        }

        # Store Factual Memory (summary + evaluation)
        try:
            # Handle both 'summary' and 'transcript_summary' fields
            summary = analysis.get('summary') or analysis.get('transcript_summary', '')
            
            # Handle both 'evaluation' and 'evaluation_criteria_results' fields
            evaluation = analysis.get('evaluation') or analysis.get('evaluation_criteria_results', {})

            # Combine summary and evaluation rationale
            factual_content = summary
            if evaluation:
                # Handle both formats: direct rationale or criteria results
                if isinstance(evaluation, dict):
                    # ElevenLabs format: evaluation_criteria_results with multiple criteria
                    if 'rationale' in evaluation:
                        # Direct format
                        rationale = evaluation.get('rationale', '')
                        if rationale:
                            factual_content += f"\n\nEvaluation: {rationale}"
                    else:
                        # Criteria results format
                        eval_summary = []
                        for criteria_name, criteria_data in evaluation.items():
                            if isinstance(criteria_data, dict):
                                result = criteria_data.get('result', 'unknown')
                                rationale = criteria_data.get('rationale', '')
                                if rationale:
                                    eval_summary.append(f"{criteria_name}: {result} - {rationale}")
                        if eval_summary:
                            factual_content += f"\n\nEvaluation:\n" + "\n".join(eval_summary)

            if factual_content:
                factual_metadata = {**common_metadata, 'type': 'factual'}

                client.add(
                    messages=[{'role': 'assistant', 'content': factual_content}],
                    user_id=caller_id,
                    metadata=factual_metadata,
                    version="v2"
                )
                logger.info(f"Stored factual memory for {caller_id}")
        except Exception as e:
            logger.error(f"Error storing factual memory: {str(e)}", exc_info=True)

        # Store Semantic Memory (full transcript)
        try:
            if transcript and len(transcript) > 0:
                # Transform ElevenLabs transcript format to Mem0 format
                # ElevenLabs: {"role": "agent"/"user", "message": "..."}
                # Mem0: {"role": "assistant"/"user", "content": "..."}
                transformed_transcript = []
                for msg in transcript:
                    if isinstance(msg, dict):
                        role = msg.get('role', 'user')
                        # Map 'agent' to 'assistant' for Mem0
                        if role == 'agent':
                            role = 'assistant'
                        
                        # Get message content from either 'message' or 'content' field
                        content = msg.get('message') or msg.get('content', '')
                        
                        if content:  # Only add messages with content
                            transformed_transcript.append({
                                'role': role,
                                'content': content
                            })
                
                if transformed_transcript:
                    semantic_metadata = {**common_metadata, 'type': 'semantic'}

                    client.add(
                        messages=transformed_transcript,
                        user_id=caller_id,
                        metadata=semantic_metadata,
                        version="v2"
                    )
                    logger.info(f"Stored semantic memory for {caller_id} ({len(transformed_transcript)} messages)")
                else:
                    logger.warning(f"No valid messages found in transcript for {caller_id}")
        except Exception as e:
            logger.error(f"Error storing semantic memory: {str(e)}", exc_info=True)

        logger.info(f"Successfully processed post-call data for {caller_id}")

    except Exception as e:
        logger.error(f"Error processing post-call webhook: {str(e)}", exc_info=True)

    return response