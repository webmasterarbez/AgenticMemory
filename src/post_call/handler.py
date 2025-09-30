"""
AgenticMemoriesPostCall Lambda Handler

Handles ElevenLabs Post-Call webhook asynchronously.
Stores factual and semantic memories in Mem0 after call completion.
"""

import json
import os
import logging
import hmac
import hashlib
import time
from typing import Dict, Any, List
from datetime import datetime

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

HMAC_KEY = os.environ['ELEVENLABS_HMAC_KEY']


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

        # Extract required fields
        conversation_id = payload.get('conversation_id', 'unknown')
        agent_id = payload.get('agent_id', 'unknown')
        call_duration = payload.get('call_duration', 0)
        transcript = payload.get('transcript', [])
        analysis = payload.get('analysis', {})
        metadata = payload.get('metadata', {})
        caller_id = metadata.get('caller_id')

        if not caller_id:
            logger.error("Missing caller_id in metadata")
            return response

        logger.info(f"Processing post-call data for user_id: {caller_id}")

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
            summary = analysis.get('summary', '')
            evaluation = analysis.get('evaluation', {})

            # Combine summary and evaluation rationale
            factual_content = summary
            if evaluation:
                rationale = evaluation.get('rationale', '')
                if rationale:
                    factual_content += f"\n\nEvaluation: {rationale}"

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
                semantic_metadata = {**common_metadata, 'type': 'semantic'}

                client.add(
                    messages=transcript,
                    user_id=caller_id,
                    metadata=semantic_metadata,
                    version="v2"
                )
                logger.info(f"Stored semantic memory for {caller_id} ({len(transcript)} messages)")
        except Exception as e:
            logger.error(f"Error storing semantic memory: {str(e)}", exc_info=True)

        logger.info(f"Successfully processed post-call data for {caller_id}")

    except Exception as e:
        logger.error(f"Error processing post-call webhook: {str(e)}", exc_info=True)

    return response