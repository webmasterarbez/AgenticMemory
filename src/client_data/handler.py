"""
AgenticMemoriesClientData Lambda Handler

Handles ElevenLabs Conversation Initiation webhook.
Returns personalized data by retrieving all memories for the caller's phone number.
"""

import json
import os
import logging
import re
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
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', '')


def extract_caller_name(all_memories: List[str]) -> Optional[str]:
    """
    Extract caller's name from memories using multiple patterns.
    
    Args:
        all_memories: List of memory strings (factual and semantic)
        
    Returns:
        Extracted name or None if not found
    """
    name_patterns = [
        # Direct name patterns
        r"(?:name is|called|goes by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"(?:user(?:'s)?\s+name:?\s*)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"(?:customer name:?\s*)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"(?:my name is|i am|i'm)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        # More flexible patterns  
        r"user\s+name\s+is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+is\s+(?:the\s+)?(?:user|customer|caller)",
        # Semantic memory patterns
        r"user\s+([A-Z][a-z]+)",
        r"customer\s+([A-Z][a-z]+)",
    ]
    
    for memory in all_memories:
        for pattern in name_patterns:
            match = re.search(pattern, memory, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Basic validation - should be 1-3 words, only letters and spaces
                if re.match(r"^[A-Za-z\s]{2,30}$", name) and len(name.split()) <= 3:
                    # Additional validation - exclude common non-names
                    excluded_words = {'wants', 'needs', 'help', 'account', 'update', 'email', 'phone', 'address', 'user', 'customer'}
                    if name.lower() not in excluded_words:
                        return name.title()  # Proper case
    
    return None


def generate_personalized_greeting(
    caller_name: Optional[str],
    is_returning: bool,
    account_status: Optional[str] = None,
    last_interaction: Optional[str] = None,
    preferences: List[str] = None
) -> str:
    """
    Generate a personalized greeting based on caller information.
    
    Args:
        caller_name: Extracted caller name
        is_returning: Whether this is a returning caller
        account_status: Account status information
        last_interaction: Information about last interaction
        preferences: List of caller preferences
        
    Returns:
        Personalized greeting message
    """
    if preferences is None:
        preferences = []
    
    if not is_returning:
        # New caller - simple greeting
        return "Hello! How may I help you today?"
    
    # Returning caller
    if caller_name:
        greeting = f"Hello {caller_name}!"
        
        # Add contextual information
        context_parts = []
        
        if account_status:
            # Extract account type
            if 'premium' in account_status.lower():
                context_parts.append("I see you're a premium customer")
            elif 'vip' in account_status.lower():
                context_parts.append("thank you for being a VIP member")
            elif any(tier in account_status.lower() for tier in ['gold', 'silver']):
                context_parts.append(f"I see you have {account_status.lower()} status")
        
        if last_interaction:
            if 'inquiry' in last_interaction.lower() or 'question' in last_interaction.lower():
                context_parts.append("following up on your recent inquiry")
            elif 'issue' in last_interaction.lower() or 'problem' in last_interaction.lower():
                context_parts.append("I hope we resolved your previous concern")
        
        if preferences and len(context_parts) < 2:
            pref_text = preferences[0].lower()
            if 'email' in pref_text:
                context_parts.append("I know you prefer email updates")
            elif 'phone' in pref_text:
                context_parts.append("I know you prefer phone communication")
        
        if context_parts:
            if len(context_parts) == 1:
                greeting += f" {context_parts[0]}."
            else:
                greeting += f" {context_parts[0]}, and {context_parts[1]}."
        
        greeting += " How can I assist you today?"
        
    else:
        # Returning caller but no name found
        greeting = "Hello! I see you've called before, but I don't have your name on file. Could you please tell me your name so I can better assist you?"
    
    return greeting


def save_client_data_to_s3(
    caller_id: str,
    agent_id: str,
    call_sid: str,
    received_payload: Dict[str, Any],
    response_payload: Dict[str, Any]
) -> None:
    """
    Save received webhook payload and sent response payload to S3.
    
    Directory structure: client-data/{sanitized_caller_id}/{timestamp}_{call_sid}/
    Files: received.json and response.json
    
    Args:
        caller_id: Caller's phone number (e.g., +16129782029)
        agent_id: ElevenLabs agent ID
        call_sid: Twilio call SID
        received_payload: The incoming webhook payload from ElevenLabs
        response_payload: The response we sent back to ElevenLabs
    """
    if not S3_BUCKET_NAME:
        logger.warning("S3_BUCKET_NAME not configured, skipping S3 save")
        return
        
    try:
        # Sanitize caller_id for S3 key (remove + prefix if present)
        sanitized_caller_id = caller_id.lstrip('+')
        
        # Create timestamp for unique directory
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        # Build S3 key prefix
        key_prefix = f"client-data/{sanitized_caller_id}/{timestamp}_{call_sid}"
        
        # Save received payload
        received_key = f"{key_prefix}/received.json"
        logger.info(f"Saving received payload to S3: s3://{S3_BUCKET_NAME}/{received_key}")
        
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=received_key,
            Body=json.dumps(received_payload, indent=2),
            ContentType='application/json',
            Metadata={
                'caller_id': caller_id,
                'agent_id': agent_id,
                'call_sid': call_sid,
                'timestamp': datetime.utcnow().isoformat(),
                'payload_type': 'received'
            }
        )
        logger.info(f"Successfully saved received payload for call {call_sid}")
        
        # Save response payload
        response_key = f"{key_prefix}/response.json"
        logger.info(f"Saving response payload to S3: s3://{S3_BUCKET_NAME}/{response_key}")
        
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=response_key,
            Body=json.dumps(response_payload, indent=2),
            ContentType='application/json',
            Metadata={
                'caller_id': caller_id,
                'agent_id': agent_id,
                'call_sid': call_sid,
                'timestamp': datetime.utcnow().isoformat(),
                'payload_type': 'response'
            }
        )
        logger.info(f"Successfully saved response payload for call {call_sid}")
        
    except Exception as e:
        logger.error(f"Error saving client data to S3: {str(e)}", exc_info=True)
        # Don't raise - S3 save failure shouldn't block the webhook response


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle ElevenLabs Conversation Initiation webhook.

    Args:
        event: API Gateway event with caller information
        context: Lambda context

    Returns:
        Personalized data with memories for the caller
    
    Note: 
        ElevenLabs Conversation Initiation webhooks do NOT include authentication headers.
        Security is based on keeping the webhook URL secret (URL obscurity).
        This is different from PostCall webhooks which use HMAC signatures.
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Extract parameters from ElevenLabs webhook payload
        # Official format: {"caller_id": "+1234567890", "agent_id": "agent_xyz", "called_number": "+1987654321", "call_sid": "CAxx..."}
        caller_id = body.get('caller_id') or body.get('system__caller_id')
        agent_id = body.get('agent_id')
        called_number = body.get('called_number')
        call_sid = body.get('call_sid')
        
        # Log incoming webhook parameters for debugging
        logger.info(f"Webhook received - caller_id: {caller_id}, agent_id: {agent_id}, called_number: {called_number}, call_sid: {call_sid}")

        if not caller_id:
            logger.error(f"Missing caller_id in request. Body received: {json.dumps(body)}")
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing caller_id parameter in request body'})
            }

        logger.info(f"Conversation initiation - caller_id: {caller_id}, agent_id: {agent_id}, called_number: {called_number}, call_sid: {call_sid}")
        logger.info(f"Retrieving memories for user_id: {caller_id}")

        # Retrieve all memories for the caller
        result = client.get_all(user_id=caller_id)

        # Extract memories from result (format: {"results": [...]})
        memories = result.get('results', []) if isinstance(result, dict) else result

        logger.info(f"Retrieved {len(memories) if memories else 0} memories for {caller_id}")

        # Separate factual and semantic memories
        factual_memories = []
        semantic_memories = []

        if memories:
            for mem in memories:
                if isinstance(mem, dict):
                    metadata = mem.get('metadata', {})
                    mem_type = metadata.get('type', 'unknown')
                    memory_text = mem.get('memory', '')

                    if memory_text:
                        if mem_type == 'factual':
                            factual_memories.append(memory_text)
                        elif mem_type == 'semantic':
                            semantic_memories.append(memory_text)
                        else:
                            factual_memories.append(memory_text)

        # Build simple context string for prompt override (no complex templating)
        context_parts = []
        
        # Extract caller name from both factual and semantic memories
        caller_name = None
        all_memories_for_name = factual_memories + semantic_memories
        if all_memories_for_name:
            caller_name = extract_caller_name(all_memories_for_name)
        
        # Determine if this is a new or returning caller
        is_returning_caller = len(memories) > 0
        
        # Build contextual information for greeting
        contextual_info = []
        account_status = None
        last_interaction = None
        preferences = []
        
        if factual_memories:
            context_parts.append("CALLER CONTEXT:")
            context_parts.append(f"This caller has {len(memories)} previous interactions.")
            context_parts.append("Known information:")
            
            # Extract contextual information for greeting
            for fact in factual_memories[:5]:
                context_parts.append(f"- {fact}")
                
                # Extract account status
                if any(word in fact.lower() for word in ['premium', 'gold', 'silver', 'basic', 'vip']):
                    account_status = fact
                
                # Extract preferences
                if any(word in fact.lower() for word in ['prefer', 'likes', 'wants', 'needs']):
                    preferences.append(fact)

        if semantic_memories:
            context_parts.append("Previous conversation highlights:")
            for conv in semantic_memories[:3]:
                context_parts.append(f"- {conv}")
                
                # Extract last interaction info
                if not last_interaction and any(word in conv.lower() for word in ['last time', 'previous', 'inquiry', 'issue', 'request']):
                    last_interaction = conv

        # Generate personalized first message
        first_message = generate_personalized_greeting(
            caller_name=caller_name,
            is_returning=is_returning_caller,
            account_status=account_status,
            last_interaction=last_interaction,
            preferences=preferences
        )

        if context_parts:
            context_parts.append(f"\nFirst Message Override: {first_message}")
            context_parts.append("\nInstructions: Use this context to personalize your responses. Reference past conversations naturally.")
        else:
            context_parts.append("NEW CALLER: This is their first interaction. Focus on building rapport and gathering information.")

        memory_context = "\n".join(context_parts)

        # Simple memory summary for dynamic variables
        memory_count = len(memories) if memories else 0
        memory_summary = ""
        if factual_memories:
            memory_summary = factual_memories[0]  # Just the first/most important fact
        else:
            memory_summary = "New caller"

        # Add caller name to dynamic variables if found
        dynamic_vars = {
            "caller_id": caller_id,
            "memory_count": str(memory_count),
            "memory_summary": memory_summary,
            "returning_caller": "yes" if memory_count > 0 else "no"
        }
        
        if caller_name:
            dynamic_vars["caller_name"] = caller_name

        # Build response with ElevenLabs conversation_initiation_client_data format
        # Official format per ElevenLabs docs:
        # {
        #   "type": "conversation_initiation_client_data",
        #   "dynamic_variables": { ... all agent dynamic variables ... },
        #   "conversation_config_override": { "agent": { "prompt": {...}, "first_message": "..." }, "tts": {...} }
        # }
        response_data = {
            "type": "conversation_initiation_client_data",
            "dynamic_variables": dynamic_vars,
            "conversation_config_override": {
                "agent": {
                    "prompt": {
                        "prompt": memory_context
                    },
                    "first_message": first_message
                }
            }
        }
        
        # Save received and response payloads to S3 (async, non-blocking)
        try:
            save_client_data_to_s3(
                caller_id=caller_id,
                agent_id=agent_id or 'unknown',
                call_sid=call_sid or 'unknown',
                received_payload=body,
                response_payload=response_data
            )
        except Exception as e:
            logger.error(f"Failed to save to S3, but continuing: {str(e)}")

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Workspace-Key',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps(response_data)
        }

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }