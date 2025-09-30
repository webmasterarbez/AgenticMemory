"""
AgenticMemoriesClientData Lambda Handler

Handles ElevenLabs Conversation Initiation webhook.
Returns personalized data by retrieving all memories for the caller's phone number.
"""

import json
import os
import logging
from typing import Dict, Any

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

WORKSPACE_KEY = os.environ['ELEVENLABS_WORKSPACE_KEY']


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle ElevenLabs Conversation Initiation webhook.

    Args:
        event: API Gateway event with caller information
        context: Lambda context

    Returns:
        Personalized data with memories for the caller
    """
    try:
        # Validate workspace key authentication
        headers = event.get('headers', {})
        workspace_key = headers.get('x-workspace-key') or headers.get('X-Workspace-Key')

        if workspace_key != WORKSPACE_KEY:
            logger.error("Invalid workspace key")
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Unauthorized'})
            }

        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Support both caller_id and system__caller_id (ElevenLabs variations)
        caller_id = body.get('caller_id') or body.get('system__caller_id')

        if not caller_id:
            logger.error("Missing caller_id or system__caller_id in request")
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing caller_id'})
            }

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

        if factual_memories:
            context_parts.append("CALLER CONTEXT:")
            context_parts.append(f"This caller has {len(memories)} previous interactions.")
            context_parts.append("Known information:")
            for fact in factual_memories[:5]:
                context_parts.append(f"- {fact}")

        if semantic_memories:
            context_parts.append("Previous conversation highlights:")
            for conv in semantic_memories[:3]:
                context_parts.append(f"- {conv}")

        if context_parts:
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

        # Build response with ElevenLabs conversation_initiation_client_data format
        response_data = {
            "type": "conversation_initiation_client_data",
            "dynamic_variables": {
                "caller_id": caller_id,
                "memory_count": str(memory_count),
                "memory_summary": memory_summary,
                "returning_caller": "yes" if memory_count > 0 else "no"
            },
            "conversation_config_override": {
                "agent": {
                    "prompt": {
                        "prompt": f"The caller {caller_id} is a {'returning' if memory_count > 0 else 'new'} customer. {memory_summary if memory_summary else 'No previous interaction history.'} You have access to {memory_count} previous memories about this caller."
                    }
                }
            }
        }

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