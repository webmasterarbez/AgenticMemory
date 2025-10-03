# AgenticMemory Generalization Recommendations

**Version:** 1.0  
**Date:** October 3, 2025  
**Purpose:** Transform current ElevenLabs-specific system into a general agentic memory platform

---

## Executive Summary

Your current AgenticMemory system is well-architected but tightly coupled to ElevenLabs' specific data formats and use cases. This document provides a comprehensive roadmap to generalize it into a platform-agnostic agentic memory system that can serve any ElevenLabs agent while maintaining backward compatibility.

## Current State Analysis

### Strengths
✅ **Solid Architecture**: Clean separation of concerns (ClientData, Retrieve, PostCall)  
✅ **Production Ready**: Proper security, monitoring, and deployment  
✅ **Scalable Design**: Serverless, async processing, S3 storage  
✅ **Good Documentation**: Comprehensive setup and usage guides  

### Current Limitations
❌ **ElevenLabs-Specific**: Hardcoded payload formats and field mappings  
❌ **Single Memory Model**: Only supports factual/semantic memory types  
❌ **Fixed Authentication**: Only supports ElevenLabs workspace/HMAC auth  
❌ **Limited Flexibility**: No configuration for different agent types  
❌ **Monolithic Design**: All agents share the same memory behavior  

---

## Generalization Strategy

### Phase 1: Configuration-Driven Architecture
**Goal:** Make the system configurable without code changes

### Phase 2: Multi-Provider Support  
**Goal:** Support different voice AI platforms beyond ElevenLabs

### Phase 3: Advanced Memory Management
**Goal:** Enhanced memory types, retention policies, and analytics

---

## Phase 1: Configuration-Driven Architecture

### 1.1 Agent Configuration System

Create a flexible agent configuration system that defines how each agent type processes memories.

**New File: `config/agent_types.json`**
```json
{
  "elevenlabs_customer_support": {
    "name": "ElevenLabs Customer Support Agent",
    "description": "Standard customer support with memory",
    "authentication": {
      "type": "workspace_key",
      "header": "X-Workspace-Key"
    },
    "webhooks": {
      "conversation_initiation": {
        "enabled": true,
        "endpoint": "/client-data",
        "required_fields": ["caller_id"],
        "field_mappings": {
          "caller_id": ["caller_id", "system__caller_id"],
          "agent_id": ["agent_id", "system__agent_id"]
        }
      },
      "post_call": {
        "enabled": true,
        "endpoint": "/post-call",
        "authentication": "hmac",
        "hmac_header": "ElevenLabs-Signature",
        "payload_format": "elevenlabs_v1"
      }
    },
    "memory_config": {
      "types": ["factual", "semantic"],
      "retention_days": 365,
      "search_limit": 3,
      "auto_extract": ["name", "preferences", "account_status"]
    },
    "response_format": "elevenlabs_v1"
  },
  "elevenlabs_sales_agent": {
    "name": "ElevenLabs Sales Agent",
    "description": "Sales-focused memory with lead tracking",
    "authentication": {
      "type": "workspace_key",
      "header": "X-Workspace-Key"
    },
    "memory_config": {
      "types": ["factual", "semantic", "lead"],
      "retention_days": 730,
      "search_limit": 5,
      "auto_extract": ["name", "budget", "timeline", "interests", "objections"]
    },
    "response_format": "elevenlabs_v1"
  },
  "generic_voice_agent": {
    "name": "Generic Voice Agent",
    "description": "Platform-agnostic voice agent",
    "authentication": {
      "type": "api_key",
      "header": "X-API-Key"
    },
    "webhooks": {
      "conversation_initiation": {
        "enabled": true,
        "endpoint": "/client-data",
        "required_fields": ["user_id"],
        "field_mappings": {
          "user_id": ["user_id", "caller_id", "customer_id"]
        }
      },
      "post_call": {
        "enabled": true,
        "endpoint": "/post-call",
        "authentication": "api_key",
        "payload_format": "generic_v1"
      }
    },
    "memory_config": {
      "types": ["factual", "semantic"],
      "retention_days": 180,
      "search_limit": 3,
      "auto_extract": ["name", "preferences"]
    },
    "response_format": "generic_v1"
  }
}
```

### 1.2 Dynamic Configuration Loading

**New File: `src/shared/config_loader.py`**
```python
"""
Dynamic configuration loader for agent types and memory settings.
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Loads and manages agent configurations."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 
            '../../config/agent_types.json'
        )
        self._configs = {}
        self._load_configs()
    
    def _load_configs(self):
        """Load all agent configurations."""
        try:
            with open(self.config_path, 'r') as f:
                self._configs = json.load(f)
            logger.info(f"Loaded {len(self._configs)} agent configurations")
        except Exception as e:
            logger.error(f"Failed to load configurations: {e}")
            self._configs = {}
    
    def get_agent_config(self, agent_type: str) -> Dict[str, Any]:
        """Get configuration for a specific agent type."""
        config = self._configs.get(agent_type)
        if not config:
            logger.warning(f"Unknown agent type: {agent_type}, using default")
            config = self._configs.get('generic_voice_agent', {})
        return config
    
    def get_memory_config(self, agent_type: str) -> Dict[str, Any]:
        """Get memory configuration for an agent type."""
        agent_config = self.get_agent_config(agent_type)
        return agent_config.get('memory_config', {})
    
    def get_authentication_config(self, agent_type: str) -> Dict[str, Any]:
        """Get authentication configuration for an agent type."""
        agent_config = self.get_agent_config(agent_type)
        return agent_config.get('authentication', {})
    
    def list_agent_types(self) -> list:
        """List all available agent types."""
        return list(self._configs.keys())
```

### 1.3 Universal Field Mapper

**New File: `src/shared/field_mapper.py`**
```python
"""
Universal field mapping system for different payload formats.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class FieldMapper:
    """Maps fields from various payload formats to standardized internal format."""
    
    def __init__(self, agent_config: Dict[str, Any]):
        self.agent_config = agent_config
        self.field_mappings = self._extract_field_mappings()
    
    def _extract_field_mappings(self) -> Dict[str, List[str]]:
        """Extract field mappings from agent configuration."""
        mappings = {}
        
        # Extract from conversation_initiation
        conv_init = self.agent_config.get('webhooks', {}).get('conversation_initiation', {})
        if 'field_mappings' in conv_init:
            mappings.update(conv_init['field_mappings'])
        
        # Add default mappings
        default_mappings = {
            'user_id': ['user_id', 'caller_id', 'customer_id', 'system__caller_id'],
            'agent_id': ['agent_id', 'system__agent_id', 'assistant_id'],
            'conversation_id': ['conversation_id', 'call_id', 'session_id'],
            'transcript': ['transcript', 'messages', 'conversation'],
            'timestamp': ['timestamp', 'created_at', 'event_timestamp']
        }
        
        # Merge with defaults (defaults take precedence)
        for field, paths in default_mappings.items():
            if field not in mappings:
                mappings[field] = paths
        
        return mappings
    
    def extract_field(self, payload: Dict[str, Any], field_name: str) -> Optional[Any]:
        """Extract a field from payload using configured mappings."""
        possible_paths = self.field_mappings.get(field_name, [field_name])
        
        for path in possible_paths:
            value = self._get_nested_value(payload, path)
            if value is not None:
                logger.debug(f"Found {field_name} at path: {path}")
                return value
        
        logger.debug(f"Field {field_name} not found in payload")
        return None
    
    def _get_nested_value(self, obj: Dict[str, Any], path: str) -> Any:
        """Get nested value from dictionary using dot notation or direct key."""
        # Try direct key first
        if path in obj:
            return obj[path]
        
        # Try dot notation
        if '.' in path:
            keys = path.split('.')
            current = obj
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            return current
        
        return None
    
    def standardize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Convert payload to standardized internal format."""
        standardized = {
            'user_id': self.extract_field(payload, 'user_id'),
            'agent_id': self.extract_field(payload, 'agent_id'),
            'conversation_id': self.extract_field(payload, 'conversation_id'),
            'transcript': self.extract_field(payload, 'transcript'),
            'timestamp': self.extract_field(payload, 'timestamp'),
            'metadata': payload.get('metadata', {}),
            'raw_payload': payload  # Keep original for debugging
        }
        
        # Extract additional fields based on payload format
        if self.agent_config.get('webhooks', {}).get('post_call', {}).get('payload_format') == 'elevenlabs_v1':
            standardized.update(self._process_elevenlabs_format(payload))
        else:
            standardized.update(self._process_generic_format(payload))
        
        return standardized
    
    def _process_elevenlabs_format(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process ElevenLabs-specific payload format."""
        result = {}
        
        # Extract analysis data
        if 'analysis' in payload:
            analysis = payload['analysis']
            result['summary'] = analysis.get('transcript_summary') or analysis.get('summary')
            result['evaluation'] = analysis.get('evaluation') or analysis.get('evaluation_criteria_results')
        
        # Extract phone call metadata
        metadata = payload.get('metadata', {})
        if 'phone_call' in metadata:
            phone_call = metadata['phone_call']
            result['call_duration'] = phone_call.get('call_duration_secs')
            result['phone_number'] = phone_call.get('external_number')
        
        return result
    
    def _process_generic_format(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process generic payload format."""
        result = {}
        
        # Common fields that might exist in generic formats
        if 'summary' in payload:
            result['summary'] = payload['summary']
        if 'duration' in payload:
            result['call_duration'] = payload['duration']
        if 'analysis' in payload:
            result['evaluation'] = payload['analysis']
        
        return result
```

### 1.4 Enhanced Memory Types

**New File: `src/shared/memory_manager.py`**
```python
"""
Enhanced memory management with support for multiple memory types.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from mem0 import MemoryClient

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages different types of memories with configurable retention and processing."""
    
    def __init__(self, mem0_client: MemoryClient, memory_config: Dict[str, Any]):
        self.client = mem0_client
        self.memory_config = memory_config
        self.supported_types = memory_config.get('types', ['factual', 'semantic'])
        self.retention_days = memory_config.get('retention_days', 365)
        self.search_limit = memory_config.get('search_limit', 3)
        self.auto_extract_fields = memory_config.get('auto_extract', [])
    
    def add_memory(self, 
                   content: str, 
                   user_id: str, 
                   memory_type: str = 'factual',
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a memory with specified type and metadata."""
        try:
            if memory_type not in self.supported_types:
                logger.warning(f"Unsupported memory type: {memory_type}, using 'factual'")
                memory_type = 'factual'
            
            # Prepare metadata
            memory_metadata = {
                'type': memory_type,
                'timestamp': datetime.utcnow().isoformat(),
                'retention_until': (datetime.utcnow() + timedelta(days=self.retention_days)).isoformat(),
                **(metadata or {})
            }
            
            # Add to Mem0
            self.client.add(
                messages=[{'role': 'assistant', 'content': content}],
                user_id=user_id,
                metadata=memory_metadata,
                version="v2"
            )
            
            logger.info(f"Added {memory_type} memory for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return False
    
    def search_memories(self, 
                       query: str, 
                       user_id: str, 
                       memory_types: Optional[List[str]] = None,
                       limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search memories with optional type filtering."""
        try:
            limit = limit or self.search_limit
            
            # Perform search
            result = self.client.search(
                query=query,
                user_id=user_id,
                limit=limit * 2  # Get more to filter by type
            )
            
            memories = result.get('results', []) if isinstance(result, dict) else result
            
            # Filter by memory type if specified
            if memory_types:
                filtered_memories = []
                for memory in memories:
                    if isinstance(memory, dict):
                        metadata = memory.get('metadata', {})
                        mem_type = metadata.get('type', 'factual')
                        if mem_type in memory_types:
                            filtered_memories.append(memory)
                memories = filtered_memories
            
            # Return only requested limit
            return memories[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    def get_all_memories(self, user_id: str, memory_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get all memories for a user, optionally filtered by type."""
        try:
            result = self.client.get_all(user_id=user_id)
            memories = result.get('results', []) if isinstance(result, dict) else result
            
            # Filter by memory type if specified
            if memory_types:
                filtered_memories = []
                for memory in memories:
                    if isinstance(memory, dict):
                        metadata = memory.get('metadata', {})
                        mem_type = metadata.get('type', 'factual')
                        if mem_type in memory_types:
                            filtered_memories.append(memory)
                memories = filtered_memories
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to get memories: {e}")
            return []
    
    def extract_auto_fields(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract automatically configured fields from memories."""
        extracted = {}
        
        for field in self.auto_extract_fields:
            value = self._extract_field_from_memories(memories, field)
            if value:
                extracted[field] = value
        
        return extracted
    
    def _extract_field_from_memories(self, memories: List[Dict[str, Any]], field: str) -> Optional[Any]:
        """Extract a specific field from memories using pattern matching."""
        import re
        
        patterns = {
            'name': [
                r'(?:name is|called|goes by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                r'(?:user(?:'s)?\s+name:?\s*)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+is\s+(?:the\s+)?(?:user|customer|caller)'
            ],
            'preferences': [
                r'(?:prefer|likes|wants)\s+([^\.!?]+)',
                r'(?:interested in)\s+([^\.!?]+)',
                r'(?:would like)\s+([^\.!?]+)'
            ],
            'budget': [
                r'(?:budget|price|cost)\s+(?:of\s+)?(\$?\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(?:willing to pay|can spend)\s+(\$?\d+(?:,\d{3})*(?:\.\d{2})?)'
            ],
            'timeline': [
                r'(?:timeline|deadline|when)\s+(?:is\s+)?([^\.!?]+)',
                r'(?:need by|want it)\s+([^\.!?]+)'
            ],
            'interests': [
                r'(?:interested in|looking for)\s+([^\.!?]+)',
                r'(?:want to|would like to)\s+([^\.!?]+)'
            ]
        }
        
        field_patterns = patterns.get(field, [])
        
        for memory in memories:
            memory_text = memory.get('memory', '') if isinstance(memory, dict) else str(memory)
            
            for pattern in field_patterns:
                match = re.search(pattern, memory_text, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        return None
```

---

## Phase 2: Multi-Provider Support

### 2.1 Provider Abstraction Layer

**New File: `src/shared/provider_adapter.py`**
```python
"""
Provider abstraction layer for supporting different voice AI platforms.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .field_mapper import FieldMapper
from .config_loader import ConfigLoader

logger = logging.getLogger(__name__)

class ProviderAdapter(ABC):
    """Abstract base class for voice AI platform adapters."""
    
    def __init__(self, agent_config: Dict[str, Any]):
        self.agent_config = agent_config
        self.field_mapper = FieldMapper(agent_config)
    
    @abstractmethod
    def authenticate_request(self, event: Dict[str, Any]) -> bool:
        """Authenticate incoming request."""
        pass
    
    @abstractmethod
    def process_conversation_initiation(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process conversation initiation webhook."""
        pass
    
    @abstractmethod
    def process_post_call(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process post-call webhook."""
        pass
    
    @abstractmethod
    def format_response(self, data: Dict[str, Any], response_type: str) -> Dict[str, Any]:
        """Format response for the specific platform."""
        pass

class ElevenLabsAdapter(ProviderAdapter):
    """Adapter for ElevenLabs platform."""
    
    def __init__(self, agent_config: Dict[str, Any]):
        super().__init__(agent_config)
        self.workspace_key = os.environ.get('ELEVENLABS_WORKSPACE_KEY')
        self.hmac_key = os.environ.get('ELEVENLABS_HMAC_KEY')
    
    def authenticate_request(self, event: Dict[str, Any]) -> bool:
        """Authenticate ElevenLabs request."""
        headers = event.get('headers', {})
        
        # Check workspace key for conversation initiation
        workspace_key = headers.get('x-workspace-key') or headers.get('X-Workspace-Key')
        if workspace_key and workspace_key == self.workspace_key:
            return True
        
        # Check HMAC signature for post-call
        signature_header = headers.get('elevenlabs-signature') or headers.get('ElevenLabs-Signature')
        if signature_header:
            return self._verify_hmac_signature(
                event.get('body', '{}'),
                signature_header
            )
        
        return False
    
    def _verify_hmac_signature(self, body: str, signature_header: str) -> bool:
        """Verify ElevenLabs HMAC signature."""
        # Implementation from existing post_call handler
        import hmac
        import hashlib
        import time
        
        try:
            parts = signature_header.split(',')
            if len(parts) != 2:
                return False
            
            timestamp = parts[0].split('=')[1]
            hmac_signature = parts[1]
            
            # Validate timestamp
            tolerance = int(time.time()) - 30 * 60
            if int(timestamp) < tolerance:
                return False
            
            # Validate signature
            full_payload_to_sign = f"{timestamp}.{body}"
            mac = hmac.new(
                key=self.hmac_key.encode('utf-8'),
                msg=full_payload_to_sign.encode('utf-8'),
                digestmod=hashlib.sha256
            )
            expected_signature = 'v0=' + mac.hexdigest()
            
            return hmac.compare_digest(hmac_signature, expected_signature)
            
        except Exception as e:
            logger.error(f"HMAC verification error: {e}")
            return False
    
    def process_conversation_initiation(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process ElevenLabs conversation initiation."""
        body = json.loads(event.get('body', '{}'))
        standardized = self.field_mapper.standardize_payload(body)
        
        # Add ElevenLabs-specific processing
        return standardized
    
    def process_post_call(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process ElevenLabs post-call webhook."""
        raw_body = event.get('body', '{}')
        payload = json.loads(raw_body)
        
        # Handle ElevenLabs array format
        if isinstance(payload, list) and len(payload) > 0:
            if 'data' in payload[0]:
                payload = payload[0]['data']
        elif isinstance(payload, dict) and 'data' in payload:
            payload = payload['data']
        
        standardized = self.field_mapper.standardize_payload(payload)
        return standardized
    
    def format_response(self, data: Dict[str, Any], response_type: str) -> Dict[str, Any]:
        """Format response for ElevenLabs platform."""
        if response_type == 'conversation_initiation':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Workspace-Key',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps(data)
            }
        elif response_type == 'post_call':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'status': 'ok'})
            }
        else:  # retrieve
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(data)
            }

class GenericAdapter(ProviderAdapter):
    """Adapter for generic voice AI platforms."""
    
    def __init__(self, agent_config: Dict[str, Any]):
        super().__init__(agent_config)
        self.api_key = os.environ.get('GENERIC_API_KEY')
    
    def authenticate_request(self, event: Dict[str, Any]) -> bool:
        """Authenticate generic request using API key."""
        headers = event.get('headers', {})
        api_key = headers.get('x-api-key') or headers.get('X-API-Key')
        return api_key == self.api_key
    
    def process_conversation_initiation(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process generic conversation initiation."""
        body = json.loads(event.get('body', '{}'))
        return self.field_mapper.standardize_payload(body)
    
    def process_post_call(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process generic post-call webhook."""
        body = json.loads(event.get('body', '{}'))
        return self.field_mapper.standardize_payload(body)
    
    def format_response(self, data: Dict[str, Any], response_type: str) -> Dict[str, Any]:
        """Format generic response."""
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(data)
        }

class ProviderFactory:
    """Factory for creating provider adapters."""
    
    @staticmethod
    def create_adapter(provider_type: str, agent_config: Dict[str, Any]) -> ProviderAdapter:
        """Create appropriate adapter for provider type."""
        if provider_type == 'elevenlabs':
            return ElevenLabsAdapter(agent_config)
        elif provider_type == 'generic':
            return GenericAdapter(agent_config)
        else:
            logger.warning(f"Unknown provider type: {provider_type}, using generic")
            return GenericAdapter(agent_config)
```

### 2.2 Updated Lambda Handlers

**Updated: `src/client_data/handler.py`**
```python
"""
Generic Client Data Lambda Handler

Handles conversation initiation webhooks for multiple voice AI platforms.
Returns personalized data by retrieving memories for the user.
"""

import json
import os
import logging
from typing import Dict, Any

from mem0 import MemoryClient
from .shared.config_loader import ConfigLoader
from .shared.provider_adapter import ProviderFactory
from .shared.memory_manager import MemoryManager

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize shared components
mem0_client = MemoryClient(
    api_key=os.environ['MEM0_API_KEY'],
    org_id=os.environ['MEM0_ORG_ID'],
    project_id=os.environ['MEM0_PROJECT_ID']
)

config_loader = ConfigLoader()

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle conversation initiation webhook for any voice AI platform.

    Args:
        event: API Gateway event
        context: Lambda context

    Returns:
        Personalized data with memories for the caller
    """
    try:
        # Determine agent type from headers or path
        headers = event.get('headers', {})
        agent_type = headers.get('x-agent-type') or headers.get('X-Agent-Type') or 'elevenlabs_customer_support'
        
        logger.info(f"Processing request for agent type: {agent_type}")
        
        # Get agent configuration
        agent_config = config_loader.get_agent_config(agent_type)
        
        # Create provider adapter
        provider_type = agent_config.get('provider', 'elevenlabs')
        adapter = ProviderFactory.create_adapter(provider_type, agent_config)
        
        # Authenticate request
        if not adapter.authenticate_request(event):
            logger.error("Authentication failed")
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Unauthorized'})
            }
        
        # Process request
        standardized_data = adapter.process_conversation_initiation(event)
        user_id = standardized_data.get('user_id')
        
        if not user_id:
            logger.error("Missing user_id in processed data")
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing user_id'})
            }
        
        # Initialize memory manager
        memory_config = config_loader.get_memory_config(agent_type)
        memory_manager = MemoryManager(mem0_client, memory_config)
        
        # Retrieve memories
        memories = memory_manager.get_all_memories(user_id)
        
        # Extract auto-configured fields
        extracted_fields = memory_manager.extract_auto_fields(memories)
        
        # Generate response based on agent configuration
        response_data = generate_response(
            agent_config, 
            user_id, 
            memories, 
            extracted_fields,
            standardized_data
        )
        
        # Format response for platform
        return adapter.format_response(response_data, 'conversation_initiation')
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

def generate_response(agent_config: Dict[str, Any], 
                     user_id: str, 
                     memories: list, 
                     extracted_fields: Dict[str, Any],
                     standardized_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate response based on agent configuration and memories."""
    
    response_format = agent_config.get('response_format', 'elevenlabs_v1')
    
    if response_format == 'elevenlabs_v1':
        return generate_elevenlabs_response(
            user_id, memories, extracted_fields, standardized_data
        )
    else:
        return generate_generic_response(
            user_id, memories, extracted_fields, standardized_data
        )

def generate_elevenlabs_response(user_id: str, 
                               memories: list, 
                               extracted_fields: Dict[str, Any],
                               standardized_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate ElevenLabs-format response."""
    
    # Build dynamic variables
    dynamic_vars = {
        "caller_id": user_id,
        "memory_count": str(len(memories)),
        "returning_caller": "yes" if memories else "no"
    }
    
    # Add extracted fields
    dynamic_vars.update(extracted_fields)
    
    # Generate memory summary
    if memories:
        factual_memories = [m for m in memories if isinstance(m, dict) and 
                           m.get('metadata', {}).get('type') == 'factual']
        if factual_memories:
            dynamic_vars["memory_summary"] = factual_memories[0].get('memory', 'No previous history')
        else:
            dynamic_vars["memory_summary"] = "New caller"
    else:
        dynamic_vars["memory_summary"] = "New caller"
    
    # Generate personalized greeting
    caller_name = extracted_fields.get('name')
    if caller_name:
        first_message = f"Hello {caller_name}! How can I assist you today?"
    elif memories:
        first_message = "Hello! I see you've called before. How can I help you today?"
    else:
        first_message = "Hello! How may I help you today?"
    
    # Build memory context
    context_parts = []
    if memories:
        context_parts.append("CALLER CONTEXT:")
        context_parts.append(f"This caller has {len(memories)} previous interactions.")
        context_parts.append("Known information:")
        
        for memory in memories[:5]:
            if isinstance(memory, dict):
                memory_text = memory.get('memory', '')
                if memory_text:
                    context_parts.append(f"- {memory_text}")
        
        context_parts.append(f"\nFirst Message Override: {first_message}")
        context_parts.append("\nInstructions: Use this context to personalize your responses.")
    else:
        context_parts.append("NEW CALLER: This is their first interaction.")
    
    memory_context = "\n".join(context_parts)
    
    return {
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

def generate_generic_response(user_id: str, 
                            memories: list, 
                            extracted_fields: Dict[str, Any],
                            standardized_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate generic response format."""
    
    return {
        "user_id": user_id,
        "memory_count": len(memories),
        "is_returning_user": len(memories) > 0,
        "extracted_fields": extracted_fields,
        "memories": memories[:5],  # Return top 5 memories
        "context": {
            "summary": f"User has {len(memories)} previous interactions" if memories else "New user",
            "personalized_greeting": f"Hello {extracted_fields.get('name', 'there')}!" if extracted_fields.get('name') else "Hello!"
        }
    }
```

---

## Phase 3: Advanced Memory Management

### 3.1 Memory Analytics and Insights

**New File: `src/analytics/handler.py`**
```python
"""
Memory Analytics Lambda Handler

Provides insights and analytics about stored memories.
"""

import json
import os
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from mem0 import MemoryClient
from ..shared.config_loader import ConfigLoader
from ..shared.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class MemoryAnalytics:
    """Analytics engine for memory data."""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
    
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about a specific user's memories."""
        memories = self.memory_manager.get_all_memories(user_id)
        
        if not memories:
            return {
                "user_id": user_id,
                "total_memories": 0,
                "insights": "No memories found"
            }
        
        # Analyze memory types
        type_counts = Counter()
        timeline = []
        topics = []
        
        for memory in memories:
            if isinstance(memory, dict):
                # Count by type
                metadata = memory.get('metadata', {})
                mem_type = metadata.get('type', 'factual')
                type_counts[mem_type] += 1
                
                # Extract timeline
                timestamp = metadata.get('timestamp')
                if timestamp:
                    timeline.append(timestamp)
                
                # Extract topics (simple keyword extraction)
                memory_text = memory.get('memory', '').lower()
                topics.extend(self._extract_topics(memory_text))
        
        # Generate insights
        insights = {
            "user_id": user_id,
            "total_memories": len(memories),
            "memory_types": dict(type_counts),
            "date_range": self._calculate_date_range(timeline),
            "top_topics": Counter(topics).most_common(5),
            "engagement_level": self._calculate_engagement_level(memories),
            "last_interaction": self._get_last_interaction(timeline),
            "trend": self._calculate_trend(memories)
        }
        
        return insights
    
    def get_agent_analytics(self, agent_type: str, days: int = 30) -> Dict[str, Any]:
        """Get analytics for a specific agent type."""
        # This would require Mem0 to support querying by metadata
        # For now, return a placeholder implementation
        return {
            "agent_type": agent_type,
            "period_days": days,
            "total_users": 0,  # Would need to be calculated
            "total_memories": 0,  # Would need to be calculated
            "avg_memories_per_user": 0,
            "most_active_users": [],
            "common_topics": [],
            "growth_trend": []
        }
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from memory text using simple keyword matching."""
        # Simple keyword-based topic extraction
        topic_keywords = {
            'billing': ['bill', 'payment', 'charge', 'cost', 'price', 'invoice'],
            'technical': ['issue', 'problem', 'error', 'bug', 'broken', 'not working'],
            'account': ['account', 'login', 'password', 'profile', 'settings'],
            'product': ['product', 'service', 'feature', 'order', 'purchase'],
            'support': ['help', 'support', 'assist', 'question', 'contact']
        }
        
        topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _calculate_date_range(self, timestamps: List[str]) -> Dict[str, str]:
        """Calculate date range from timestamps."""
        if not timestamps:
            return {"start": None, "end": None}
        
        dates = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps if ts]
        if not dates:
            return {"start": None, "end": None}
        
        return {
            "start": min(dates).isoformat(),
            "end": max(dates).isoformat()
        }
    
    def _calculate_engagement_level(self, memories: List[Dict[str, Any]]) -> str:
        """Calculate engagement level based on memory count and recency."""
        memory_count = len(memories)
        
        if memory_count == 0:
            return "none"
        elif memory_count < 5:
            return "low"
        elif memory_count < 15:
            return "medium"
        else:
            return "high"
    
    def _get_last_interaction(self, timestamps: List[str]) -> str:
        """Get the most recent interaction timestamp."""
        if not timestamps:
            return None
        
        dates = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps if ts]
        if not dates:
            return None
        
        return max(dates).isoformat()
    
    def _calculate_trend(self, memories: List[Dict[str, Any]]) -> str:
        """Calculate interaction trend based on recent vs older memories."""
        if len(memories) < 2:
            return "insufficient_data"
        
        # Simple trend calculation based on last 30 days vs previous 30 days
        now = datetime.utcnow()
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)
        
        recent_count = 0
        older_count = 0
        
        for memory in memories:
            if isinstance(memory, dict):
                timestamp = memory.get('metadata', {}).get('timestamp')
                if timestamp:
                    mem_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    if mem_date >= thirty_days_ago:
                        recent_count += 1
                    elif mem_date >= sixty_days_ago:
                        older_count += 1
        
        if recent_count > older_count:
            return "increasing"
        elif recent_count < older_count:
            return "decreasing"
        else:
            return "stable"

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle analytics requests.

    Args:
        event: API Gateway event
        context: Lambda context

    Returns:
        Analytics data
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        request_type = body.get('type', 'user_insights')
        agent_type = body.get('agent_type', 'elevenlabs_customer_support')
        
        # Initialize components
        config_loader = ConfigLoader()
        memory_config = config_loader.get_memory_config(agent_type)
        mem0_client = MemoryClient(
            api_key=os.environ['MEM0_API_KEY'],
            org_id=os.environ['MEM0_ORG_ID'],
            project_id=os.environ['MEM0_PROJECT_ID']
        )
        memory_manager = MemoryManager(mem0_client, memory_config)
        analytics = MemoryAnalytics(memory_manager)
        
        # Process request
        if request_type == 'user_insights':
            user_id = body.get('user_id')
            if not user_id:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Missing user_id'})
                }
            
            result = analytics.get_user_insights(user_id)
        
        elif request_type == 'agent_analytics':
            days = body.get('days', 30)
            result = analytics.get_agent_analytics(agent_type, days)
        
        else:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f'Unknown request type: {request_type}'})
            }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Error processing analytics request: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
```

---

## Implementation Roadmap

### Week 1-2: Foundation
- [ ] Create configuration system (`config/agent_types.json`)
- [ ] Implement `ConfigLoader` and `FieldMapper`
- [ ] Create `MemoryManager` with enhanced memory types
- [ ] Set up unit tests for new components

### Week 3-4: Provider Abstraction
- [ ] Implement `ProviderAdapter` abstract class
- [ ] Create `ElevenLabsAdapter` (refactor existing logic)
- [ ] Create `GenericAdapter` for platform-agnostic support
- [ ] Implement `ProviderFactory`

### Week 5-6: Handler Updates
- [ ] Update all three Lambda handlers to use new architecture
- [ ] Maintain backward compatibility with existing ElevenLabs integration
- [ ] Add comprehensive error handling and logging
- [ ] Update deployment templates

### Week 7-8: Analytics & Advanced Features
- [ ] Implement analytics Lambda function
- [ ] Add memory retention policies
- [ ] Create admin API for configuration management
- [ ] Add monitoring and alerting

### Week 9-10: Testing & Documentation
- [ ] Comprehensive integration testing
- [ ] Performance testing and optimization
- [ ] Update all documentation
- [ ] Create migration guide for existing users

---

## Migration Strategy

### Backward Compatibility
1. **Existing Deployments**: Continue working without changes
2. **Configuration Migration**: Auto-generate config from current setup
3. **Gradual Rollout**: Feature flags for new functionality
4. **Fallback Support**: Default to current behavior if config missing

### Configuration Migration Script
```python
# scripts/migrate_to_generic.py
"""
Migrate existing ElevenLabs-specific deployment to generic configuration.
"""

import json
import os

def generate_config_from_env():
    """Generate agent_types.json from current environment variables."""
    
    config = {
        "elevenlabs_customer_support": {
            "name": "ElevenLabs Customer Support Agent",
            "description": "Migrated from existing deployment",
            "provider": "elevenlabs",
            "authentication": {
                "type": "workspace_key",
                "header": "X-Workspace-Key"
            },
            "webhooks": {
                "conversation_initiation": {
                    "enabled": True,
                    "endpoint": "/client-data",
                    "required_fields": ["caller_id"],
                    "field_mappings": {
                        "caller_id": ["caller_id", "system__caller_id"],
                        "agent_id": ["agent_id", "system__agent_id"]
                    }
                },
                "post_call": {
                    "enabled": True,
                    "endpoint": "/post-call",
                    "authentication": "hmac",
                    "hmac_header": "ElevenLabs-Signature",
                    "payload_format": "elevenlabs_v1"
                }
            },
            "memory_config": {
                "types": ["factual", "semantic"],
                "retention_days": 365,
                "search_limit": int(os.getenv('MEM0_SEARCH_LIMIT', '3')),
                "auto_extract": ["name", "preferences", "account_status"]
            },
            "response_format": "elevenlabs_v1"
        }
    }
    
    return config

if __name__ == "__main__":
    config = generate_config_from_env()
    
    # Create config directory
    os.makedirs('config', exist_ok=True)
    
    # Write configuration
    with open('config/agent_types.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Generated config/agent_types.json")
    print("📝 Review and customize as needed")
```

---

## Benefits of Generalization

### 1. **Multi-Platform Support**
- Support for ElevenLabs, Vapi, Retell, and custom platforms
- Easy addition of new providers without code changes
- Consistent memory management across platforms

### 2. **Flexible Memory Types**
- Support for factual, semantic, lead, and custom memory types
- Configurable retention policies
- Advanced field extraction and analytics

### 3. **Configuration-Driven**
- No code changes needed for new agent types
- A/B testing of different memory strategies
- Easy customization for different use cases

### 4. **Enhanced Analytics**
- User engagement insights
- Topic trend analysis
- Agent performance metrics

### 5. **Future-Proof Architecture**
- Easy addition of new features
- Plugin system for custom processors
- Scalable for enterprise use

---

## Next Steps

1. **Review and Approve**: Go through this roadmap and provide feedback
2. **Start Implementation**: Begin with Phase 1 (Configuration System)
3. **Testing Strategy**: Set up comprehensive testing for each phase
4. **Documentation**: Keep documentation updated throughout implementation
5. **Community Feedback**: Share progress and gather user feedback

This transformation will position your AgenticMemory system as the leading memory platform for voice AI agents, supporting any ElevenLabs agent while maintaining the reliability and performance of your current implementation.
