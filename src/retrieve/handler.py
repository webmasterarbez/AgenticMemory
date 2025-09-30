"""
AgenticMemoriesRetrieve Lambda Handler

Handles in-call semantic memory retrieval.
Returns relevant memories based on query and user_id.
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

SEARCH_LIMIT = int(os.environ.get('MEM0_SEARCH_LIMIT', '3'))
TIMEOUT = int(os.environ.get('MEM0_TIMEOUT', '5'))


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle semantic memory search during active call.

    Args:
        event: API Gateway event with query and user_id
        context: Lambda context

    Returns:
        Top N relevant memories based on semantic search
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        query = body.get('query')
        user_id = body.get('user_id')

        if not query:
            logger.error("Missing query in request")
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing query'})
            }

        if not user_id:
            logger.error("Missing user_id in request")
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing user_id'})
            }

        logger.info(f"Searching memories for user_id: {user_id}, query: {query}")

        # Perform semantic search
        result = client.search(
            query=query,
            user_id=user_id,
            limit=SEARCH_LIMIT
        )

        # Extract memories from result (format: {"results": [...]})
        memories = result.get('results', []) if isinstance(result, dict) else result

        logger.info(f"Found {len(memories) if memories else 0} memories for query")

        # Return search results
        response_data = {
            'memories': memories or []
        }

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response_data)
        }

    except Exception as e:
        logger.error(f"Error processing search: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }