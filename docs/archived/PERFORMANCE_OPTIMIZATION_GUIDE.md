# AgenticMemory Performance Optimization Guide

**Version:** 1.0  
**Date:** October 3, 2025  
**Purpose:** Comprehensive performance optimization strategy for AgenticMemory system supporting multiple ElevenLabs agent types

---

## Executive Summary

This guide provides a detailed roadmap for optimizing your AgenticMemory system to support different types of ElevenLabs agents while maximizing performance and minimizing costs. The optimization strategy focuses on four key areas:

1. **Lambda Performance Optimization** - Reducing cold starts and execution time
2. **Agent Type Specialization** - Tailoring memory behavior for different agent types
3. **Intelligent Caching** - Reducing redundant API calls and improving response times
4. **Advanced Monitoring** - Real-time performance tracking and optimization

**Target Performance Goals:**
- Cold start latency: <500ms (from current 3-5 seconds)
- Warm call latency: <200ms (from current 500ms)
- 99th percentile latency: <400ms
- Cost optimization: 20-30% reduction per call
- Support for 10+ concurrent calls with consistent performance

---

## Current System Analysis

### Baseline Architecture

Your current AgenticMemory system consists of:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ClientData    │    │    Retrieve     │    │    PostCall     │
│   Lambda        │    │    Lambda       │    │    Lambda       │
│   (256MB)       │    │   (256MB)       │    │   (256MB)       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │   HTTP API Gateways      │
                    │   (3 separate endpoints) │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      Mem0 Cloud          │
                    │   (External API calls)   │
                    └───────────────────────────┘
```

### Current Performance Characteristics

**Lambda Configuration:**
- Memory: 256MB
- Timeout: 30s (ClientData/Retrieve), 120s (PostCall)
- Runtime: Python 3.12
- Cold starts: 3-5 seconds
- Warm execution: 300-500ms

**Cost Structure (Current - ~10K calls/month):**
- Lambda Compute: $5-8
- Lambda Requests: $0.20
- API Gateway: $1-2
- CloudWatch Logs: $0.50
- Data Transfer: $0.10
- **Total: ~$7-11/month**

### Identified Bottlenecks

1. **Cold Start Latency** (3-5 seconds)
   - Lambda initialization overhead
   - Mem0 client initialization
   - Layer loading time

2. **Memory Constraints** (256MB)
   - Limited CPU allocation
   - Potential memory pressure with large responses
   - Garbage collection overhead

3. **API Call Overhead**
   - Multiple Mem0 API calls per request
   - No connection pooling
   - No caching of frequent queries

4. **Single Configuration**
   - One-size-fits-all memory behavior
   - No agent-specific optimizations
   - Fixed search limits and retention

---

## Phase 1: Immediate Performance Wins

### 1.1 Lambda Memory Optimization

**What:** Increase Lambda memory allocation from 256MB to 512MB

**Why:** 
- AWS Lambda allocates CPU proportionally to memory
- 512MB provides ~2x CPU power for only ~2x cost
- Better performance for Mem0 API calls and JSON processing
- Reduced garbage collection overhead

**Implementation:**

```yaml
# template.yaml - Update all three functions
Globals:
  Function:
    Runtime: python3.12
    MemorySize: 512  # Changed from 256
    Timeout: 30
    Architectures:
      - x86_64
```

**Expected Impact:**
- 20-30% reduction in execution time
- Better handling of large memory responses
- Cost increase: ~$0.000000208 per GB-second (minimal for small scale)

**Code Example - Memory Usage Monitoring:**

```python
# src/shared/performance_monitor.py
import psutil
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor Lambda performance metrics."""
    
    @staticmethod
    def log_memory_usage(context: str = ""):
        """Log current memory usage."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            logger.info(f"[{context}] Memory usage: {memory_mb:.1f}MB")
            
            # Alert if using >80% of allocated memory
            if memory_mb > 400:  # 80% of 512MB
                logger.warning(f"[{context}] High memory usage: {memory_mb:.1f}MB")
                
        except Exception as e:
            logger.error(f"Failed to monitor memory: {e}")
    
    @staticmethod
    def log_execution_time(start_time: float, operation: str):
        """Log operation execution time."""
        duration = (time.time() - start_time) * 1000
        logger.info(f"{operation} completed in {duration:.1f}ms")
        
        # Alert if operation is slow
        if duration > 1000:
            logger.warning(f"Slow operation: {operation} took {duration:.1f}ms")
```

### 1.2 Connection Pooling for Mem0

**What:** Implement HTTP connection pooling for Mem0 API calls

**Why:**
- Eliminates TCP handshake overhead for each API call
- Reuses connections across multiple invocations
- Reduces latency by 50-100ms per API call
- Better resource utilization

**Implementation:**

```python
# src/shared/mem0_client.py
import requests
import requests.adapters
from urllib3.util.retry import Retry
from mem0 import MemoryClient
import logging

logger = logging.getLogger(__name__)

class OptimizedMemoryClient:
    """Optimized Mem0 client with connection pooling."""
    
    def __init__(self, api_key: str, org_id: str, project_id: str):
        self.api_key = api_key
        self.org_id = org_id
        self.project_id = project_id
        
        # Create session with connection pooling
        self.session = self._create_optimized_session()
        
        # Initialize Mem0 client with custom session
        self.client = MemoryClient(
            api_key=api_key,
            org_id=org_id,
            project_id=project_id
        )
        
        # Override the default session
        self.client.session = self.session
        
        logger.info("Optimized Mem0 client initialized with connection pooling")
    
    def _create_optimized_session(self) -> requests.Session:
        """Create HTTP session with optimal settings for Lambda."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # Configure HTTP adapter with connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,  # Max connections to keep
            pool_maxsize=20,      # Max connections per pool
            max_retries=retry_strategy
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set timeouts
        session.timeout = (3.05, 10)  # (connect, read)
        
        return session
    
    def add_memory(self, messages: list, user_id: str, metadata: dict = None):
        """Add memory with optimized client."""
        start_time = time.time()
        try:
            result = self.client.add(
                messages=messages,
                user_id=user_id,
                metadata=metadata or {},
                version="v2"
            )
            
            duration = (time.time() - start_time) * 1000
            logger.info(f"Memory added in {duration:.1f}ms for user {user_id}")
            return result
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"Failed to add memory after {duration:.1f}ms: {e}")
            raise
    
    def search_memories(self, query: str, user_id: str, limit: int = 3):
        """Search memories with optimized client."""
        start_time = time.time()
        try:
            result = self.client.search(
                query=query,
                user_id=user_id,
                limit=limit
            )
            
            duration = (time.time() - start_time) * 1000
            logger.info(f"Memory search completed in {duration:.1f}ms for user {user_id}")
            return result
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"Memory search failed after {duration:.1f}ms: {e}")
            raise

# Global client instance (reused across invocations)
_mem0_client = None

def get_mem0_client() -> OptimizedMemoryClient:
    """Get or create optimized Mem0 client."""
    global _mem0_client
    if _mem0_client is None:
        _mem0_client = OptimizedMemoryClient(
            api_key=os.environ['MEM0_API_KEY'],
            org_id=os.environ['MEM0_ORG_ID'],
            project_id=os.environ['MEM0_PROJECT_ID']
        )
    return _mem0_client
```

### 1.3 Provisioned Concurrency

**What:** Enable Provisioned Concurrency for Lambda functions

**Why:**
- Eliminates cold starts completely
- Consistent sub-100ms response times
- Better user experience for time-sensitive voice interactions
- Predictable performance

**Implementation:**

```yaml
# template.yaml - Add to each Lambda function
AgenticMemoriesClientData:
  Type: AWS::Serverless::Function
  Properties:
    FunctionName: elevenlabs-agentic-memory-lambda-function-client-data
    CodeUri: src/client_data/
    Handler: handler.lambda_handler
    Role: !GetAtt AgenticMemoriesLambdaRole.Arn
    Layers:
      - !Ref AgenticMemoriesLambdaLayer
    MemorySize: 512
    Timeout: 30
    ProvisionedConcurrencyConfig:
      ProvisionedConcurrencyEnabled: true
      ProvisionedConcurrency: 2  # Start with 2, scale as needed
    Environment:
      Variables:
        MEM0_API_KEY: !Ref Mem0ApiKey
        MEM0_ORG_ID: !Ref Mem0OrgId
        MEM0_PROJECT_ID: !Ref Mem0ProjectId
        MEM0_DIR: /tmp/.mem0
        ELEVENLABS_WORKSPACE_KEY: !Ref ElevenLabsWorkspaceKey
```

**Cost Analysis:**
```
Provisioned Concurrency Cost (2 instances):
- Compute: $0.0000041667 per GB-second
- Memory: 512MB = 0.5GB
- Monthly: 0.5GB * 0.0000041667 * 2,592,000 seconds = $5.40
- Additional: ~$5-7/month

Total with Provisioned Concurrency: ~$12-18/month
Performance benefit: Eliminates 3-5 second cold starts
```

**Scaling Strategy:**
```yaml
# Auto-scaling configuration
AutoScalingConfiguration:
  MinCapacity: 2
  MaxCapacity: 10
  TargetUtilization: 70
```

### 1.4 Response Compression

**What:** Enable gzip compression for API Gateway responses

**Why:**
- Reduces payload size by 60-80%
- Faster transfer times
- Lower data transfer costs
- Better performance for memory-heavy responses

**Implementation:**

```yaml
# template.yaml - Add to HTTP API definitions
AgenticMemoriesClientDataHttpApi:
  Type: AWS::Serverless::HttpApi
  Properties:
    Name: elevenlabs-agentic-memory-api-gateway-client-data
    StageName: Prod
    Tags:
      Project: AgenticMemories
      Endpoint: ClientData
    # Enable compression
    DefinitionBody:
      openapi: 3.0.1
      info:
        title: ClientData API
      paths:
        /client-data:
          post:
            responses:
              '200':
                content:
                  application/json:
                    schema:
                      type: object
    # CloudFormation for compression
    CorsConfiguration:
      AllowOrigins: ["*"]
      AllowHeaders: ["*"]
      AllowMethods: ["*"]
```

**Lambda Handler with Compression:**

```python
# src/shared/compression.py
import gzip
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def compress_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Compress response data if beneficial."""
    try:
        json_str = json.dumps(data)
        
        # Only compress if >1KB
        if len(json_str) > 1024:
            compressed = gzip.compress(json_str.encode('utf-8'))
            
            # Only use compression if it reduces size
            if len(compressed) < len(json_str):
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Content-Encoding': 'gzip',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': compressed.decode('utf-8')
                }
        
        # Return uncompressed for small responses
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json_str
        }
        
    except Exception as e:
        logger.error(f"Compression failed: {e}")
        # Fallback to uncompressed
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(data)
        }
```

---

## Phase 2: Agent Type Specialization

### 2.1 Agent Configuration System

**What:** Create configuration-driven system for different ElevenLabs agent types

**Why:**
- Different agents have different memory requirements
- Sales agents need lead tracking, support agents need issue history
- Optimized memory extraction per agent type
- Better performance through specialized configurations

**Implementation:**

```json
// config/agent_types.json
{
  "elevenlabs_customer_support": {
    "name": "ElevenLabs Customer Support Agent",
    "description": "Customer support with issue tracking and resolution history",
    "memory_config": {
      "types": ["factual", "semantic", "issue"],
      "retention_days": 365,
      "search_limit": 5,
      "auto_extract": ["name", "account_status", "contact_preference", "issue_type", "resolution_pattern"],
      "priority_fields": ["issue_type", "resolution", "satisfaction"],
      "search_weights": {
        "issue": 2.0,
        "resolution": 1.8,
        "account": 1.5,
        "preference": 1.2
      }
    },
    "response_config": {
      "max_memories_in_context": 3,
      "summarize_after": 5,
      "focus_on_recent": true,
      "recent_days": 30
    },
    "performance_config": {
      "cache_duration": 300,
      "batch_size": 3,
      "timeout_override": 25
    }
  },
  "elevenlabs_sales_agent": {
    "name": "ElevenLabs Sales Agent",
    "description": "Sales agent with lead tracking and conversion history",
    "memory_config": {
      "types": ["factual", "semantic", "lead", "conversion"],
      "retention_days": 730,
      "search_limit": 8,
      "auto_extract": ["name", "budget", "timeline", "interests", "objections", "decision_maker", "company"],
      "priority_fields": ["budget", "timeline", "interests", "objections"],
      "search_weights": {
        "lead": 2.5,
        "budget": 2.0,
        "timeline": 1.8,
        "objections": 1.5
      }
    },
    "response_config": {
      "max_memories_in_context": 5,
      "summarize_after": 8,
      "focus_on_conversion": true,
      "pipeline_stages": ["prospect", "qualified", "proposal", "negotiation", "closed"]
    },
    "performance_config": {
      "cache_duration": 600,
      "batch_size": 5,
      "timeout_override": 30
    }
  },
  "elevenlabs_technical_support": {
    "name": "ElevenLabs Technical Support Agent",
    "description": "Technical support with issue resolution and knowledge base",
    "memory_config": {
      "types": ["factual", "semantic", "technical", "resolution"],
      "retention_days": 540,
      "search_limit": 6,
      "auto_extract": ["name", "technical_skill", "issue_category", "resolution_steps", "escalation_level"],
      "priority_fields": ["issue_category", "resolution", "technical_details"],
      "search_weights": {
        "technical": 2.2,
        "resolution": 2.0,
        "issue_category": 1.8,
        "escalation": 1.5
      }
    },
    "response_config": {
      "max_memories_in_context": 4,
      "summarize_after": 6,
      "focus_on_technical": true,
      "knowledge_base_integration": true
    },
    "performance_config": {
      "cache_duration": 900,
      "batch_size": 4,
      "timeout_override": 35
    }
  }
}
```

### 2.2 Dynamic Configuration Loader

```python
# src/shared/agent_config.py
import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class AgentConfigManager:
    """Manages agent-specific configurations."""
    
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
            config = self._configs.get('elevenlabs_customer_support', {})
        return config
    
    def get_memory_config(self, agent_type: str) -> Dict[str, Any]:
        """Get memory configuration for an agent type."""
        agent_config = self.get_agent_config(agent_type)
        return agent_config.get('memory_config', {})
    
    def get_performance_config(self, agent_type: str) -> Dict[str, Any]:
        """Get performance configuration for an agent type."""
        agent_config = self.get_agent_config(agent_type)
        return agent_config.get('performance_config', {})
    
    def get_response_config(self, agent_type: str) -> Dict[str, Any]:
        """Get response configuration for an agent type."""
        agent_config = self.get_agent_config(agent_type)
        return agent_config.get('response_config', {})

# Global instance
_config_manager = None

def get_config_manager() -> AgentConfigManager:
    """Get global configuration manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = AgentConfigManager()
    return _config_manager
```

### 2.3 Specialized Memory Manager

```python
# src/shared/specialized_memory_manager.py
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .mem0_client import get_mem0_client
from .agent_config import get_config_manager

logger = logging.getLogger(__name__)

class SpecializedMemoryManager:
    """Memory manager specialized for different agent types."""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.config_manager = get_config_manager()
        self.mem0_client = get_mem0_client()
        
        # Load configurations
        self.memory_config = self.config_manager.get_memory_config(agent_type)
        self.response_config = self.config_manager.get_response_config(agent_type)
        self.performance_config = self.config_manager.get_performance_config(agent_type)
        
        # Extract settings
        self.search_limit = self.memory_config.get('search_limit', 3)
        self.auto_extract_fields = self.memory_config.get('auto_extract', [])
        self.search_weights = self.memory_config.get('search_weights', {})
        self.cache_duration = self.performance_config.get('cache_duration', 300)
    
    def add_specialized_memory(self, 
                              content: str, 
                              user_id: str, 
                              memory_type: str = 'factual',
                              metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add memory with agent-specific processing."""
        try:
            # Enhanced metadata based on agent type
            enhanced_metadata = {
                'agent_type': self.agent_type,
                'memory_type': memory_type,
                'timestamp': datetime.utcnow().isoformat(),
                'retention_until': (datetime.utcnow() + timedelta(
                    days=self.memory_config.get('retention_days', 365)
                )).isoformat(),
                **(metadata or {})
            }
            
            # Add agent-specific field extraction
            extracted_fields = self.extract_agent_fields(content)
            enhanced_metadata.update(extracted_fields)
            
            # Add to Mem0
            self.mem0_client.add_memory(
                messages=[{'role': 'assistant', 'content': content}],
                user_id=user_id,
                metadata=enhanced_metadata
            )
            
            logger.info(f"Added {memory_type} memory for {self.agent_type} agent, user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add specialized memory: {e}")
            return False
    
    def search_specialized_memories(self, 
                                   query: str, 
                                   user_id: str,
                                   memory_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search memories with agent-specific weighting."""
        try:
            # Perform search with higher limit for filtering
            result = self.mem0_client.search_memories(
                query=query,
                user_id=user_id,
                limit=self.search_limit * 2
            )
            
            memories = result.get('results', []) if isinstance(result, dict) else result
            
            # Filter and rank by agent type
            filtered_memories = self._filter_and_rank_memories(memories, memory_types)
            
            return filtered_memories[:self.search_limit]
            
        except Exception as e:
            logger.error(f"Failed to search specialized memories: {e}")
            return []
    
    def _filter_and_rank_memories(self, 
                                 memories: List[Dict[str, Any]], 
                                 memory_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Filter and rank memories based on agent configuration."""
        filtered = []
        
        for memory in memories:
            if not isinstance(memory, dict):
                continue
                
            metadata = memory.get('metadata', {})
            
            # Filter by memory type if specified
            if memory_types:
                mem_type = metadata.get('memory_type', 'factual')
                if mem_type not in memory_types:
                    continue
            
            # Calculate relevance score based on agent weights
            score = self._calculate_memory_score(memory)
            memory['_relevance_score'] = score
            filtered.append(memory)
        
        # Sort by relevance score
        filtered.sort(key=lambda x: x.get('_relevance_score', 0), reverse=True)
        return filtered
    
    def _calculate_memory_score(self, memory: Dict[str, Any]) -> float:
        """Calculate relevance score for memory based on agent type."""
        base_score = 1.0
        metadata = memory.get('metadata', {})
        
        # Boost based on memory type weights
        memory_type = metadata.get('memory_type', 'factual')
        type_weight = self.search_weights.get(memory_type, 1.0)
        base_score *= type_weight
        
        # Boost recent memories
        timestamp = metadata.get('timestamp')
        if timestamp:
            try:
                mem_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                days_old = (datetime.utcnow() - mem_date.replace(tzinfo=None)).days
                
                if days_old < 7:
                    base_score *= 1.5  # Recent memories
                elif days_old < 30:
                    base_score *= 1.2  # Somewhat recent
            except:
                pass
        
        # Boost memories with priority fields
        for field in self.memory_config.get('priority_fields', []):
            if field in metadata and metadata[field]:
                base_score *= 1.1
        
        return base_score
    
    def extract_agent_fields(self, content: str) -> Dict[str, Any]:
        """Extract agent-specific fields from content."""
        extracted = {}
        
        if self.agent_type == 'elevenlabs_sales_agent':
            extracted.update(self._extract_sales_fields(content))
        elif self.agent_type == 'elevenlabs_technical_support':
            extracted.update(self._extract_technical_fields(content))
        elif self.agent_type == 'elevenlabs_customer_support':
            extracted.update(self._extract_support_fields(content))
        
        # Common extractions
        extracted.update(self._extract_common_fields(content))
        
        return extracted
    
    def _extract_sales_fields(self, content: str) -> Dict[str, Any]:
        """Extract sales-specific fields."""
        fields = {}
        
        # Budget extraction
        budget_patterns = [
            r'(?:budget|price|cost)\s+(?:of\s+)?(\$?\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(?:willing to pay|can spend)\s+(\$?\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(?:looking at|around)\s+(\$?\d+(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields['budget'] = match.group(1)
                break
        
        # Timeline extraction
        timeline_patterns = [
            r'(?:timeline|deadline|when)\s+(?:is\s+)?([^\.!?]+)',
            r'(?:need by|want it)\s+([^\.!?]+)',
            r'(?:in the next|within)\s+(\d+)\s+(days|weeks|months)'
        ]
        
        for pattern in timeline_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields['timeline'] = match.group(1) if len(match.groups()) == 1 else f"{match.group(1)} {match.group(2)}"
                break
        
        # Interest extraction
        interest_patterns = [
            r'(?:interested in|looking for)\s+([^\.!?]+)',
            r'(?:want to|would like to)\s+([^\.!?]+)',
            r'(?:need help with)\s+([^\.!?]+)'
        ]
        
        for pattern in interest_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields['interests'] = match.group(1)
                break
        
        return fields
    
    def _extract_technical_fields(self, content: str) -> Dict[str, Any]:
        """Extract technical support fields."""
        fields = {}
        
        # Issue category
        technical_keywords = {
            'login': ['login', 'password', 'authentication', 'sign in'],
            'connectivity': ['connection', 'network', 'wifi', 'internet'],
            'performance': ['slow', 'lag', 'performance', 'speed'],
            'error': ['error', 'crash', 'bug', 'exception'],
            'feature': ['feature', 'functionality', 'how to', 'tutorial']
        }
        
        content_lower = content.lower()
        for category, keywords in technical_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                fields['issue_category'] = category
                break
        
        # Escalation level
        escalation_indicators = ['urgent', 'emergency', 'critical', 'production down', 'blocked']
        if any(indicator in content_lower for indicator in escalation_indicators):
            fields['escalation_level'] = 'high'
        elif any(indicator in content_lower for indicator in ['frustrated', 'angry', 'upset']):
            fields['escalation_level'] = 'medium'
        else:
            fields['escalation_level'] = 'low'
        
        return fields
    
    def _extract_support_fields(self, content: str) -> Dict[str, Any]:
        """Extract customer support fields."""
        fields = {}
        
        # Account status
        account_patterns = [
            r'(?:premium|gold|silver|bronze|basic|free)\s+(?:account|plan|member)',
            r'(?:customer|client|user)\s+(?:since|from)\s+(\d{4})',
            r'(?:subscribed|signed up)\s+(?:in|on)\s+(\w+\s+\d{4})'
        ]
        
        for pattern in account_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields['account_status'] = match.group(0)
                break
        
        # Contact preference
        contact_patterns = [
            r'(?:prefer|like)\s+(?:email|phone|call|text)',
            r'(?:contact me|reach me)\s+(?:via|by)\s+(email|phone|call|text)',
            r'(?:send|email)\s+(?:me|to)\s+([^@\s]+@[^@\s]+)'
        ]
        
        for pattern in contact_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields['contact_preference'] = match.group(1) if len(match.groups()) == 1 else match.group(0)
                break
        
        return fields
    
    def _extract_common_fields(self, content: str) -> Dict[str, Any]:
        """Extract fields common to all agent types."""
        fields = {}
        
        # Name extraction
        name_patterns = [
            r'(?:name is|called|goes by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'(?:this is|I am)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+is\s+(?:the\s+)?(?:user|customer|caller)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, content)
            if match:
                fields['name'] = match.group(1)
                break
        
        return fields
```

### 2.4 Updated Lambda Handlers

```python
# src/client_data/handler.py - Updated with agent specialization
import json
import os
import time
import logging
from typing import Dict, Any

from .shared.mem0_client import get_mem0_client
from .shared.agent_config import get_config_manager
from .shared.specialized_memory_manager import SpecializedMemoryManager
from .shared.performance_monitor import PerformanceMonitor
from .shared.compression import compress_response

logger = logging.getLogger(__name__)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Enhanced ClientData handler with agent type specialization.
    """
    start_time = time.time()
    
    try:
        # Performance monitoring
        PerformanceMonitor.log_memory_usage("client_data_start")
        
        # Determine agent type from headers or default
        headers = event.get('headers', {})
        agent_type = headers.get('x-agent-type') or headers.get('X-Agent-Type') or 'elevenlabs_customer_support'
        
        logger.info(f"Processing ClientData request for agent type: {agent_type}")
        
        # Authenticate request
        if not _authenticate_request(event, agent_type):
            logger.error("Authentication failed")
            return compress_response({'error': 'Unauthorized'})
        
        # Parse request
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('caller_id') or body.get('user_id')
        
        if not user_id:
            logger.error("Missing user_id in request")
            return compress_response({'error': 'Missing user_id'})
        
        # Initialize specialized memory manager
        memory_manager = SpecializedMemoryManager(agent_type)
        
        # Retrieve memories with agent-specific logic
        memories = memory_manager.search_specialized_memories(
            query="recent interactions and preferences",
            user_id=user_id
        )
        
        # Generate agent-specific response
        response_data = _generate_agent_response(
            agent_type, user_id, memories, memory_manager
        )
        
        PerformanceMonitor.log_execution_time(start_time, "client_data_total")
        PerformanceMonitor.log_memory_usage("client_data_end")
        
        # Return compressed response
        return compress_response(response_data)
        
    except Exception as e:
        logger.error(f"Error in ClientData handler: {str(e)}", exc_info=True)
        PerformanceMonitor.log_execution_time(start_time, "client_data_error")
        return compress_response({'error': str(e)})

def _authenticate_request(event: Dict[str, Any], agent_type: str) -> bool:
    """Authenticate request based on agent type."""
    headers = event.get('headers', {})
    
    # Get authentication config
    config_manager = get_config_manager()
    agent_config = config_manager.get_agent_config(agent_type)
    auth_config = agent_config.get('authentication', {})
    
    auth_type = auth_config.get('type', 'workspace_key')
    header_name = auth_config.get('header', 'X-Workspace-Key')
    
    if auth_type == 'workspace_key':
        workspace_key = headers.get(header_name.lower()) or headers.get(header_name)
        expected_key = os.environ.get('ELEVENLABS_WORKSPACE_KEY')
        return workspace_key == expected_key
    
    return False

def _generate_agent_response(agent_type: str, 
                            user_id: str, 
                            memories: list, 
                            memory_manager: SpecializedMemoryManager) -> Dict[str, Any]:
    """Generate agent-specific response."""
    
    config_manager = get_config_manager()
    response_config = config_manager.get_response_config(agent_type)
    
    # Extract agent-specific fields
    extracted_fields = {}
    for memory in memories:
        if isinstance(memory, dict):
            metadata = memory.get('metadata', {})
            for field in memory_manager.auto_extract_fields:
                if field in metadata and field not in extracted_fields:
                    extracted_fields[field] = metadata[field]
    
    # Build dynamic variables
    dynamic_vars = {
        "caller_id": user_id,
        "memory_count": str(len(memories)),
        "returning_caller": "yes" if memories else "no"
    }
    dynamic_vars.update(extracted_fields)
    
    # Generate memory summary based on agent type
    memory_summary = _generate_memory_summary(agent_type, memories, response_config)
    dynamic_vars["memory_summary"] = memory_summary
    
    # Generate personalized greeting
    greeting = _generate_personalized_greeting(agent_type, extracted_fields, memories)
    
    # Build memory context
    memory_context = _build_memory_context(agent_type, memories, greeting, response_config)
    
    return {
        "type": "conversation_initiation_client_data",
        "dynamic_variables": dynamic_vars,
        "conversation_config_override": {
            "agent": {
                "prompt": {
                    "prompt": memory_context
                },
                "first_message": greeting
            }
        }
    }

def _generate_memory_summary(agent_type: str, memories: list, response_config: Dict[str, Any]) -> str:
    """Generate agent-specific memory summary."""
    
    if not memories:
        return "New caller"
    
    if agent_type == 'elevenlabs_sales_agent':
        # Focus on sales-related memories
        sales_memories = [m for m in memories if isinstance(m, dict) and 
                         m.get('metadata', {}).get('memory_type') in ['lead', 'conversion']]
        
        if sales_memories:
            latest = sales_memories[0]
            metadata = latest.get('metadata', {})
            budget = metadata.get('budget', 'not discussed')
            timeline = metadata.get('timeline', 'not discussed')
            return f"Lead with budget: {budget}, timeline: {timeline}"
    
    elif agent_type == 'elevenlabs_technical_support':
        # Focus on technical issues
        tech_memories = [m for m in memories if isinstance(m, dict) and 
                        m.get('metadata', {}).get('memory_type') in ['technical', 'resolution']]
        
        if tech_memories:
            latest = tech_memories[0]
            metadata = latest.get('metadata', {})
            category = metadata.get('issue_category', 'general')
            escalation = metadata.get('escalation_level', 'low')
            return f"Previous {category} issue ({escalation} priority)"
    
    else:  # customer support
        # General summary
        latest = memories[0] if memories else None
        if latest and isinstance(latest, dict):
            memory_text = latest.get('memory', '')
            return memory_text[:100] + "..." if len(memory_text) > 100 else memory_text
    
    return f"Customer with {len(memories)} previous interactions"

def _generate_personalized_greeting(agent_type: str, 
                                   extracted_fields: Dict[str, Any], 
                                   memories: list) -> str:
    """Generate agent-specific personalized greeting."""
    
    caller_name = extracted_fields.get('name')
    
    if agent_type == 'elevenlabs_sales_agent':
        if caller_name:
            if memories:
                return f"Hi {caller_name}! Great to hear from you again. I see you've been exploring our solutions."
            else:
                return f"Hi {caller_name}! Welcome! I'm excited to learn about your needs and see how we can help."
        else:
            return "Hello! I'm here to help you find the perfect solution for your needs."
    
    elif agent_type == 'elevenlabs_technical_support':
        if caller_name:
            if memories:
                return f"Hi {caller_name}! I'm here to help with any technical issues you're experiencing."
            else:
                return f"Hi {caller_name}! Welcome to technical support. How can I assist you today?"
        else:
            return "Hello! Technical support here. What challenge can I help you solve today?"
    
    else:  # customer support
        if caller_name:
            if memories:
                return f"Hello {caller_name}! It's great to hear from you again. How can I assist you today?"
            else:
                return f"Hello {caller_name}! Welcome! How may I help you today?"
        else:
            return "Hello! How may I help you today?"

def _build_memory_context(agent_type: str, 
                         memories: list, 
                         greeting: str, 
                         response_config: Dict[str, Any]) -> str:
    """Build agent-specific memory context."""
    
    max_memories = response_config.get('max_memories_in_context', 3)
    focus_recent = response_config.get('focus_on_recent', True)
    recent_days = response_config.get('recent_days', 30)
    
    context_parts = []
    
    if memories:
        context_parts.append("CALLER CONTEXT:")
        context_parts.append(f"This caller has {len(memories)} previous interactions.")
        context_parts.append("Relevant information:")
        
        # Filter memories based on configuration
        relevant_memories = memories[:max_memories]
        
        for memory in relevant_memories:
            if isinstance(memory, dict):
                memory_text = memory.get('memory', '')
                metadata = memory.get('metadata', {})
                
                # Add agent-specific context
                if agent_type == 'elevenlabs_sales_agent':
                    budget = metadata.get('budget')
                    timeline = metadata.get('timeline')
                    if budget or timeline:
                        memory_text += f" (Budget: {budget or 'N/A'}, Timeline: {timeline or 'N/A'})"
                
                elif agent_type == 'elevenlabs_technical_support':
                    category = metadata.get('issue_category')
                    escalation = metadata.get('escalation_level')
                    if category or escalation:
                        memory_text += f" (Category: {category or 'N/A'}, Priority: {escalation or 'N/A'})"
                
                context_parts.append(f"- {memory_text}")
        
        context_parts.append(f"\nFirst Message Override: {greeting}")
        
        # Add agent-specific instructions
        if agent_type == 'elevenlabs_sales_agent':
            context_parts.append("\nSales Instructions: Focus on understanding their needs, budget, and timeline. Reference previous conversations naturally.")
        elif agent_type == 'elevenlabs_technical_support':
            context_parts.append("\nTechnical Support Instructions: Focus on understanding the technical issue and providing clear solutions. Reference previous technical issues.")
        else:
            context_parts.append("\nInstructions: Use this context to personalize your responses and provide excellent service.")
    
    else:
        if agent_type == 'elevenlabs_sales_agent':
            context_parts.append("NEW PROSPECT: This is their first interaction. Focus on discovery and building rapport.")
        elif agent_type == 'elevenlabs_technical_support':
            context_parts.append("NEW USER: This is their first technical support request. Focus on thorough problem understanding.")
        else:
            context_parts.append("NEW CALLER: This is their first interaction. Provide excellent first impression service.")
    
    return "\n".join(context_parts)
```

---

## Phase 3: Advanced Performance Optimizations

### 3.1 Intelligent Caching Layer

**What:** Implement multi-level caching for frequently accessed data

**Why:**
- Reduces Mem0 API calls by 60-80%
- Improves response times for repeated queries
- Lower costs and better user experience
- Reduces load on external services

**Implementation:**

```python
# src/shared/cache_manager.py
import json
import time
import hashlib
import logging
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    """Multi-level caching system for Lambda functions."""
    
    def __init__(self):
        # In-memory cache (persists across invocations in same execution context)
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'memory_misses': 0
        }
    
    def get(self, key: str, cache_type: str = 'memory') -> Optional[Any]:
        """Get value from cache."""
        if cache_type == 'memory':
            return self._get_from_memory(key)
        else:
            logger.warning(f"Unknown cache type: {cache_type}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300, cache_type: str = 'memory'):
        """Set value in cache."""
        if cache_type == 'memory':
            self._set_in_memory(key, value, ttl)
        else:
            logger.warning(f"Unknown cache type: {cache_type}")
    
    def _get_from_memory(self, key: str) -> Optional[Any]:
        """Get value from in-memory cache."""
        cache_entry = self.memory_cache.get(key)
        
        if cache_entry is None:
            self.cache_stats['memory_misses'] += 1
            self.cache_stats['misses'] += 1
            return None
        
        # Check TTL
        if time.time() > cache_entry['expires']:
            del self.memory_cache[key]
            self.cache_stats['memory_misses'] += 1
            self.cache_stats['misses'] += 1
            return None
        
        self.cache_stats['memory_hits'] += 1
        self.cache_stats['hits'] += 1
        
        logger.debug(f"Cache hit for key: {key}")
        return cache_entry['value']
    
    def _set_in_memory(self, key: str, value: Any, ttl: int):
        """Set value in in-memory cache."""
        expires = time.time() + ttl
        self.memory_cache[key] = {
            'value': value,
            'expires': expires,
            'created': time.time()
        }
        
        # Cleanup expired entries
        self._cleanup_expired()
    
    def _cleanup_expired(self):
        """Remove expired entries from memory cache."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if current_time > entry['expires']
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_requests': total_requests,
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'hit_rate_percent': round(hit_rate, 2),
            'memory_cache_size': len(self.memory_cache),
            'memory_hits': self.cache_stats['memory_hits'],
            'memory_misses': self.cache_stats['memory_misses']
        }
    
    def clear(self):
        """Clear all cache entries."""
        self.memory_cache.clear()
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'memory_misses': 0
        }
        logger.info("Cache cleared")

# Global cache instance
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """Get global cache manager."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

class CachedMemoryClient:
    """Memory client with intelligent caching."""
    
    def __init__(self, memory_client, cache_manager: CacheManager):
        self.memory_client = memory_client
        self.cache = cache_manager
    
    def search_memories(self, query: str, user_id: str, limit: int = 3, use_cache: bool = True) -> list:
        """Search memories with caching."""
        if not use_cache:
            return self.memory_client.search_memories(query, user_id, limit)
        
        # Generate cache key
        cache_key = self.cache.get_cache_key('search', query, user_id, limit)
        
        # Try to get from cache
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Cache hit for memory search: {query[:50]}...")
            return cached_result
        
        # Cache miss - call actual API
        result = self.memory_client.search_memories(query, user_id, limit)
        
        # Cache the result (shorter TTL for search results)
        ttl = 180  # 3 minutes for search results
        self.cache.set(cache_key, result, ttl)
        
        logger.info(f"Cached memory search result: {query[:50]}...")
        return result
    
    def add_memory(self, messages: list, user_id: str, metadata: dict = None) -> bool:
        """Add memory and invalidate relevant cache entries."""
        result = self.memory_client.add_memory(messages, user_id, metadata)
        
        # Invalidate cache entries for this user
        self._invalidate_user_cache(user_id)
        
        return result
    
    def _invalidate_user_cache(self, user_id: str):
        """Invalidate cache entries for a specific user."""
        # This is a simple implementation - in production, you might want
        # more sophisticated cache invalidation
        cache_keys_to_remove = []
        
        for key in self.cache.memory_cache.keys():
            if isinstance(key, str) and user_id in key:
                cache_keys_to_remove.append(key)
        
        for key in cache_keys_to_remove:
            del self.cache.memory_cache[key]
        
        if cache_keys_to_remove:
            logger.info(f"Invalidated {len(cache_keys_to_remove)} cache entries for user {user_id}")
```

### 3.2 Batch Processing Optimization

```python
# src/shared/batch_processor.py
import asyncio
import time
import logging
from typing import List, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BatchItem:
    """Item to be processed in batch."""
    id: str
    data: Dict[str, Any]
    callback: Callable
    timestamp: float

class BatchProcessor:
    """Efficient batch processing for memory operations."""
    
    def __init__(self, batch_size: int = 5, max_wait_time: float = 1.0):
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.pending_items = []
        self.processing = False
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    def add_item(self, item_id: str, data: Dict[str, Any], callback: Callable):
        """Add item to batch processing queue."""
        item = BatchItem(
            id=item_id,
            data=data,
            callback=callback,
            timestamp=time.time()
        )
        
        self.pending_items.append(item)
        
        # Process batch if conditions met
        if len(self.pending_items) >= self.batch_size:
            self._process_batch()
        else:
            # Schedule processing if max wait time reached
            asyncio.create_task(self._schedule_processing())
    
    async def _schedule_processing(self):
        """Schedule batch processing if wait time exceeded."""
        await asyncio.sleep(self.max_wait_time)
        
        if self.pending_items and not self.processing:
            self._process_batch()
    
    def _process_batch(self):
        """Process current batch of items."""
        if not self.pending_items or self.processing:
            return
        
        self.processing = True
        current_batch = self.pending_items.copy()
        self.pending_items.clear()
        
        try:
            # Process batch in thread pool
            future = self.executor.submit(self._process_batch_sync, current_batch)
            
            # Don't wait for completion - fire and forget
            # In production, you might want better error handling
            
        except Exception as e:
            logger.error(f"Failed to process batch: {e}")
            # Re-queue items on error
            self.pending_items.extend(current_batch)
        finally:
            self.processing = False
    
    def _process_batch_sync(self, batch: List[BatchItem]):
        """Process batch synchronously."""
        start_time = time.time()
        
        try:
            # Group by operation type
            search_items = []
            add_items = []
            
            for item in batch:
                operation = item.data.get('operation')
                if operation == 'search':
                    search_items.append(item)
                elif operation == 'add':
                    add_items.append(item)
            
            # Process searches in parallel
            if search_items:
                self._process_search_batch(search_items)
            
            # Process adds sequentially (Mem0 might not support batch adds)
            if add_items:
                self._process_add_batch(add_items)
            
            duration = (time.time() - start_time) * 1000
            logger.info(f"Processed batch of {len(batch)} items in {duration:.1f}ms")
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            
            # Call callbacks with error
            for item in batch:
                try:
                    item.callback(None, error=str(e))
                except:
                    logger.error(f"Callback failed for item {item.id}")
    
    def _process_search_batch(self, search_items: List[BatchItem]):
        """Process multiple search items efficiently."""
        # For now, process individually - Mem0 doesn't support batch search
        # In the future, you might implement a more sophisticated solution
        
        for item in search_items:
            try:
                query = item.data.get('query')
                user_id = item.data.get('user_id')
                limit = item.data.get('limit', 3)
                
                # Call the actual search function
                result = self.memory_client.search_memories(query, user_id, limit)
                item.callback(result, None)
                
            except Exception as e:
                logger.error(f"Search failed for item {item.id}: {e}")
                item.callback(None, error=str(e))
    
    def _process_add_batch(self, add_items: List[BatchItem]):
        """Process multiple add items."""
        for item in add_items:
            try:
                messages = item.data.get('messages')
                user_id = item.data.get('user_id')
                metadata = item.data.get('metadata')
                
                result = self.memory_client.add_memory(messages, user_id, metadata)
                item.callback(result, None)
                
            except Exception as e:
                logger.error(f"Add failed for item {item.id}: {e}")
                item.callback(None, error=str(e))
    
    def flush(self):
        """Process any remaining items."""
        if self.pending_items:
            self._process_batch()
```

### 3.3 Async Processing Enhancement

```python
# src/post_call/handler.py - Enhanced with async processing
import json
import os
import time
import asyncio
import logging
from typing import Dict, Any
import boto3

from .shared.mem0_client import get_mem0_client
from .shared.agent_config import get_config_manager
from .shared.specialized_memory_manager import SpecializedMemoryManager
from .shared.performance_monitor import PerformanceMonitor
from .shared.s3_storage import S3StorageManager

logger = logging.getLogger(__name__)

# Initialize S3 and SQS clients
s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Enhanced PostCall handler with async processing and SQS queue.
    """
    start_time = time.time()
    
    try:
        PerformanceMonitor.log_memory_usage("post_call_start")
        
        # Quick authentication
        if not _authenticate_request(event):
            logger.error("Authentication failed")
            return {'statusCode': 401, 'body': json.dumps({'error': 'Unauthorized'})}
        
        # Parse request
        raw_body = event.get('body', '{}')
        payload = json.loads(raw_body)
        
        # Handle ElevenLabs array format
        if isinstance(payload, list) and len(payload) > 0:
            if 'data' in payload[0]:
                payload = payload[0]['data']
        elif isinstance(payload, dict) and 'data' in payload:
            payload = payload['data']
        
        # Extract metadata
        headers = event.get('headers', {})
        agent_type = headers.get('x-agent-type', 'elevenlabs_customer_support')
        
        # Store raw data in S3 for processing
        s3_key = _store_raw_data(payload, context.aws_request_id)
        
        # Send to SQS for async processing
        _send_to_async_queue({
            's3_key': s3_key,
            'agent_type': agent_type,
            'request_id': context.aws_request_id,
            'timestamp': time.time()
        })
        
        PerformanceMonitor.log_execution_time(start_time, "post_call_queue")
        
        # Immediate response
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'queued', 'request_id': context.aws_request_id})
        }
        
    except Exception as e:
        logger.error(f"Error in PostCall handler: {str(e)}", exc_info=True)
        PerformanceMonitor.log_execution_time(start_time, "post_call_error")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

def _store_raw_data(payload: Dict[str, Any], request_id: str) -> str:
    """Store raw payload in S3."""
    bucket_name = os.environ['S3_BUCKET_NAME']
    s3_key = f"post-call/{request_id}/{int(time.time())}.json"
    
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json.dumps(payload, default=str),
            ContentType='application/json',
            Metadata={
                'request_id': request_id,
                'timestamp': str(int(time.time()))
            }
        )
        
        logger.info(f"Stored raw data in S3: {s3_key}")
        return s3_key
        
    except Exception as e:
        logger.error(f"Failed to store data in S3: {e}")
        raise

def _send_to_async_queue(message: Dict[str, Any]):
    """Send message to SQS for async processing."""
    queue_url = os.environ.get('ASYNC_PROCESSING_QUEUE_URL')
    
    if not queue_url:
        # Fallback to synchronous processing
        logger.warning("No SQS queue configured, processing synchronously")
        _process_memory_async(message)
        return
    
    try:
        sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message),
            MessageGroupId='post-call-processing',  # For FIFO queue
            MessageDeduplicationId=message.get('request_id')
        )
        
        logger.info(f"Sent to async queue: {message.get('request_id')}")
        
    except Exception as e:
        logger.error(f"Failed to send to SQS: {e}")
        # Fallback to synchronous processing
        _process_memory_async(message)

def _process_memory_async(message: Dict[str, Any]):
    """Process memory storage asynchronously."""
    try:
        s3_key = message.get('s3_key')
        agent_type = message.get('agent_type')
        request_id = message.get('request_id')
        
        # Retrieve data from S3
        bucket_name = os.environ['S3_BUCKET_NAME']
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        payload = json.loads(response['Body'].read())
        
        # Process memories
        memory_manager = SpecializedMemoryManager(agent_type)
        
        # Extract different types of memories
        memories_added = 0
        
        # Factual memory from transcript
        transcript = payload.get('transcript', '')
        if transcript:
            success = memory_manager.add_specialized_memory(
                content=transcript,
                user_id=_extract_user_id(payload),
                memory_type='factual',
                metadata={
                    'source': 'post_call',
                    'conversation_id': payload.get('conversation_id'),
                    'agent_id': payload.get('agent_id'),
                    'call_duration': payload.get('call_duration')
                }
            )
            if success:
                memories_added += 1
        
        # Semantic memory from analysis
        analysis = payload.get('analysis', {})
        if analysis:
            summary = analysis.get('transcript_summary') or analysis.get('summary')
            if summary:
                success = memory_manager.add_specialized_memory(
                    content=summary,
                    user_id=_extract_user_id(payload),
                    memory_type='semantic',
                    metadata={
                        'source': 'analysis',
                        'conversation_id': payload.get('conversation_id'),
                        'analysis_type': 'summary'
                    }
                )
                if success:
                    memories_added += 1
        
        logger.info(f"Processed {memories_added} memories for request {request_id}")
        
        # Store processing result
        _store_processing_result(request_id, {
            'status': 'completed',
            'memories_added': memories_added,
            'processing_time': time.time() - message.get('timestamp', time.time())
        })
        
    except Exception as e:
        logger.error(f"Async processing failed for {message.get('request_id')}: {e}")
        _store_processing_result(message.get('request_id'), {
            'status': 'failed',
            'error': str(e)
        })

def _extract_user_id(payload: Dict[str, Any]) -> str:
    """Extract user ID from payload."""
    metadata = payload.get('metadata', {})
    phone_call = metadata.get('phone_call', {})
    
    return (phone_call.get('external_number') or 
            metadata.get('caller_id') or 
            payload.get('caller_id') or 
            'unknown')

def _store_processing_result(request_id: str, result: Dict[str, Any]):
    """Store processing result in S3."""
    bucket_name = os.environ['S3_BUCKET_NAME']
    s3_key = f"post-call-results/{request_id}.json"
    
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json.dumps(result, default=str),
            ContentType='application/json'
        )
        
        logger.info(f"Stored processing result: {s3_key}")
        
    except Exception as e:
        logger.error(f"Failed to store processing result: {e}")

def _authenticate_request(event: Dict[str, Any]) -> bool:
    """Authenticate ElevenLabs webhook."""
    headers = event.get('headers', {})
    signature_header = headers.get('elevenlabs-signature') or headers.get('ElevenLabs-Signature')
    
    if not signature_header:
        return False
    
    # HMAC verification (existing implementation)
    import hmac
    import hashlib
    
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
        raw_body = event.get('body', '{}')
        full_payload_to_sign = f"{timestamp}.{raw_body}"
        
        hmac_key = os.environ.get('ELEVENLABS_HMAC_KEY')
        mac = hmac.new(
            key=hmac_key.encode('utf-8'),
            msg=full_payload_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        )
        expected_signature = 'v0=' + mac.hexdigest()
        
        return hmac.compare_digest(hmac_signature, expected_signature)
        
    except Exception as e:
        logger.error(f"HMAC verification error: {e}")
        return False
```

---

## Phase 4: Monitoring & Analytics

### 4.1 Performance Monitoring Dashboard

```python
# src/monitoring/performance_monitor.py
import time
import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import boto3

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    timestamp: float
    function_name: str
    execution_time_ms: float
    memory_used_mb: float
    cold_start: bool
    agent_type: str
    operation_type: str
    user_id: str
    api_calls_count: int
    cache_hit_rate: float
    error_occurred: bool
    error_message: str = ""

class PerformanceCollector:
    """Collects and analyzes performance metrics."""
    
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.metrics_buffer = []
        self.buffer_size = 50
    
    def record_metrics(self, metrics: PerformanceMetrics):
        """Record performance metrics."""
        self.metrics_buffer.append(metrics)
        
        # Flush buffer if full
        if len(self.metrics_buffer) >= self.buffer_size:
            self.flush_metrics()
    
    def flush_metrics(self):
        """Send metrics to CloudWatch."""
        if not self.metrics_buffer:
            return
        
        try:
            # Group metrics by function and agent type
            grouped_metrics = {}
            
            for metric in self.metrics_buffer:
                key = f"{metric.function_name}_{metric.agent_type}"
                if key not in grouped_metrics:
                    grouped_metrics[key] = []
                grouped_metrics[key].append(metric)
            
            # Send CloudWatch metrics
            for group_key, metrics_list in grouped_metrics.items():
                self._send_cloudwatch_metrics(group_key, metrics_list)
            
            # Clear buffer
            self.metrics_buffer.clear()
            
            logger.info(f"Flushed {len(metrics_list)} performance metrics to CloudWatch")
            
        except Exception as e:
            logger.error(f"Failed to flush metrics: {e}")
    
    def _send_cloudwatch_metrics(self, group_key: str, metrics: List[PerformanceMetrics]):
        """Send metrics to CloudWatch."""
        function_name, agent_type = group_key.split('_', 1)
        
        # Calculate aggregates
        execution_times = [m.execution_time_ms for m in metrics]
        memory_usage = [m.memory_used_mb for m in metrics]
        cache_hit_rates = [m.cache_hit_rate for m in metrics if m.cache_hit_rate > 0]
        cold_starts = sum(1 for m in metrics if m.cold_start)
        errors = sum(1 for m in metrics if m.error_occurred)
        
        # Prepare metric data
        metric_data = [
            {
                'MetricName': 'ExecutionTime',
                'Value': sum(execution_times) / len(execution_times),
                'Unit': 'Milliseconds',
                'Dimensions': [
                    {'Name': 'FunctionName', 'Value': function_name},
                    {'Name': 'AgentType', 'Value': agent_type}
                ]
            },
            {
                'MetricName': 'MemoryUsage',
                'Value': sum(memory_usage) / len(memory_usage),
                'Unit': 'Megabytes',
                'Dimensions': [
                    {'Name': 'FunctionName', 'Value': function_name},
                    {'Name': 'AgentType', 'Value': agent_type}
                ]
            },
            {
                'MetricName': 'ColdStartCount',
                'Value': cold_starts,
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'FunctionName', 'Value': function_name},
                    {'Name': 'AgentType', 'Value': agent_type}
                ]
            },
            {
                'MetricName': 'ErrorCount',
                'Value': errors,
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'FunctionName', 'Value': function_name},
                    {'Name': 'AgentType', 'Value': agent_type}
                ]
            }
        ]
        
        # Add cache hit rate if available
        if cache_hit_rates:
            metric_data.append({
                'MetricName': 'CacheHitRate',
                'Value': sum(cache_hit_rates) / len(cache_hit_rates),
                'Unit': 'Percent',
                'Dimensions': [
                    {'Name': 'FunctionName', 'Value': function_name},
                    {'Name': 'AgentType', 'Value': agent_type}
                ]
            })
        
        # Send to CloudWatch
        self.cloudwatch.put_metric_data(
            Namespace='AgenticMemory/Performance',
            MetricData=metric_data
        )

class PerformanceAnalyzer:
    """Analyzes performance data and provides insights."""
    
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
    
    def get_performance_summary(self, 
                              function_name: str = None,
                              agent_type: str = None,
                              hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the specified period."""
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Build dimensions
        dimensions = []
        if function_name:
            dimensions.append({'Name': 'FunctionName', 'Value': function_name})
        if agent_type:
            dimensions.append({'Name': 'AgentType', 'Value': agent_type})
        
        # Get metrics
        metrics = {}
        
        metric_queries = [
            {'id': 'exec_time', 'label': 'ExecutionTime'},
            {'id': 'memory', 'label': 'MemoryUsage'},
            {'id': 'cold_starts', 'label': 'ColdStartCount'},
            {'id': 'errors', 'label': 'ErrorCount'},
            {'id': 'cache_hit_rate', 'label': 'CacheHitRate'}
        ]
        
        for query in metric_queries:
            try:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AgenticMemory/Performance',
                    MetricName=query['label'],
                    Dimensions=dimensions,
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,  # 1-hour periods
                    Statistics=['Average', 'Sum', 'Maximum']
                )
                
                if response['Datapoints']:
                    latest = max(response['Datapoints'], key=lambda x: x['Timestamp'])
                    metrics[query['id']] = {
                        'average': latest.get('Average', 0),
                        'maximum': latest.get('Maximum', 0),
                        'sum': latest.get('Sum', 0),
                        'timestamp': latest['Timestamp'].isoformat()
                    }
                
            except Exception as e:
                logger.error(f"Failed to get metric {query['label']}: {e}")
        
        # Calculate insights
        insights = self._generate_insights(metrics)
        
        return {
            'period_hours': hours,
            'dimensions': dimensions,
            'metrics': metrics,
            'insights': insights,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _generate_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate performance insights."""
        insights = []
        
        # Execution time insights
        if 'exec_time' in metrics:
            avg_time = metrics['exec_time']['average']
            max_time = metrics['exec_time']['maximum']
            
            if avg_time > 1000:
                insights.append(f"⚠️ High average execution time: {avg_time:.1f}ms")
            elif avg_time < 200:
                insights.append(f"✅ Excellent execution time: {avg_time:.1f}ms")
            
            if max_time > 3000:
                insights.append(f"🚨 Very slow execution detected: {max_time:.1f}ms")
        
        # Memory usage insights
        if 'memory' in metrics:
            avg_memory = metrics['memory']['average']
            
            if avg_memory > 400:
                insights.append(f"⚠️ High memory usage: {avg_memory:.1f}MB")
            elif avg_memory < 100:
                insights.append(f"✅ Efficient memory usage: {avg_memory:.1f}MB")
        
        # Cold start insights
        if 'cold_starts' in metrics:
            cold_starts = metrics['cold_starts']['sum']
            
            if cold_starts > 10:
                insights.append(f"🚨 High cold start count: {cold_starts}")
            elif cold_starts == 0:
                insights.append("✅ No cold starts detected")
        
        # Error rate insights
        if 'errors' in metrics and 'exec_time' in metrics:
            errors = metrics['errors']['sum']
            total_requests = metrics['exec_time'].get('sum', 0) / metrics['exec_time'].get('average', 1)
            
            if total_requests > 0:
                error_rate = (errors / total_requests) * 100
                if error_rate > 5:
                    insights.append(f"🚨 High error rate: {error_rate:.1f}%")
                elif error_rate < 1:
                    insights.append(f"✅ Low error rate: {error_rate:.1f}%")
        
        # Cache hit rate insights
        if 'cache_hit_rate' in metrics:
            hit_rate = metrics['cache_hit_rate']['average']
            
            if hit_rate > 70:
                insights.append(f"✅ Excellent cache hit rate: {hit_rate:.1f}%")
            elif hit_rate < 30:
                insights.append(f"⚠️ Low cache hit rate: {hit_rate:.1f}%")
        
        if not insights:
            insights.append("✅ All performance metrics look good")
        
        return insights

# Global instances
_performance_collector = None
_performance_analyzer = None

def get_performance_collector() -> PerformanceCollector:
    """Get global performance collector."""
    global _performance_collector
    if _performance_collector is None:
        _performance_collector = PerformanceCollector()
    return _performance_collector

def get_performance_analyzer() -> PerformanceAnalyzer:
    """Get global performance analyzer."""
    global _performance_analyzer
    if _performance_analyzer is None:
        _performance_analyzer = PerformanceAnalyzer()
    return _performance_analyzer
```

### 4.2 Cost Optimization Analytics

```python
# src/monitoring/cost_analyzer.py
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import boto3

logger = logging.getLogger(__name__)

class CostAnalyzer:
    """Analyzes costs and provides optimization recommendations."""
    
    def __init__(self):
        self.ce_client = boto3.client('ce')
        self.cloudwatch = boto3.client('cloudwatch')
    
    def get_cost_analysis(self, 
                         service: str = None,
                         hours: int = 24) -> Dict[str, Any]:
        """Get cost analysis for the specified period."""
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Get cost data
        cost_data = self._get_cost_data(start_time, end_time, service)
        
        # Get usage metrics
        usage_metrics = self._get_usage_metrics(start_time, end_time)
        
        # Calculate cost per call
        cost_per_call = self._calculate_cost_per_call(cost_data, usage_metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(cost_data, usage_metrics, cost_per_call)
        
        return {
            'period_hours': hours,
            'cost_data': cost_data,
            'usage_metrics': usage_metrics,
            'cost_per_call': cost_per_call,
            'recommendations': recommendations,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _get_cost_data(self, start_time: datetime, end_time: datetime, service: str = None) -> Dict[str, Any]:
        """Get cost data from AWS Cost Explorer."""
        try:
            filters = {}
            if service:
                filters['Service'] = [service]
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_time.strftime('%Y-%m-%d'),
                    'End': end_time.strftime('%Y-%m-%d')
                },
                Granularity='HOURLY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'OPERATION'}
                ],
                Filters=filters
            )
            
            # Process results
            cost_by_service = {}
            total_cost = 0
            
            for result in response.get('ResultsByTime', []):
                time_period = result['TimePeriod']['Start']
                
                for group in result.get('Groups', []):
                    service_name = group['Keys'][0]
                    operation = group['Keys'][1] if len(group['Keys']) > 1 else 'Total'
                    amount = float(group['Metrics']['BlendedCost']['Amount'])
                    
                    if service_name not in cost_by_service:
                        cost_by_service[service_name] = {}
                    
                    cost_by_service[service_name][operation] = amount
                    total_cost += amount
            
            return {
                'total_cost': total_cost,
                'by_service': cost_by_service,
                'currency': 'USD'
            }
            
        except Exception as e:
            logger.error(f"Failed to get cost data: {e}")
            return {'total_cost': 0, 'by_service': {}, 'currency': 'USD'}
    
    def _get_usage_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get usage metrics from CloudWatch."""
        try:
            # Get Lambda metrics
            lambda_metrics = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Invocations',
                Dimensions=[
                    {'Name': 'FunctionName', 'Value': 'elevenlabs-agentic-memory-lambda-function-client-data'}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            
            # Get API Gateway metrics
            api_metrics = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/ApiGateway',
                MetricName='Count',
                Dimensions=[
                    {'Name': 'ApiName', 'Value': 'elevenlabs-agentic-memory-api-gateway-client-data'}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            
            # Sum up invocations
            total_invocations = sum(
                dp['Sum'] for dp in lambda_metrics.get('Datapoints', [])
            )
            
            total_api_calls = sum(
                dp['Sum'] for dp in api_metrics.get('Datapoints', [])
            )
            
            return {
                'lambda_invocations': total_invocations,
                'api_calls': total_api_calls,
                'total_requests': max(total_invocations, total_api_calls)
            }
            
        except Exception as e:
            logger.error(f"Failed to get usage metrics: {e}")
            return {'lambda_invocations': 0, 'api_calls': 0, 'total_requests': 0}
    
    def _calculate_cost_per_call(self, cost_data: Dict[str, Any], usage_metrics: Dict[str, Any]) -> Dict[str, float]:
        """Calculate cost per call."""
        total_cost = cost_data.get('total_cost', 0)
        total_requests = usage_metrics.get('total_requests', 1)
        
        cost_per_call = total_cost / total_requests if total_requests > 0 else 0
        
        # Calculate cost by service
        cost_by_service = cost_data.get('by_service', {})
        service_costs = {}
        
        for service, operations in cost_by_service.items():
            service_total = sum(operations.values())
            service_costs[service] = service_total / total_requests if total_requests > 0 else 0
        
        return {
            'overall': cost_per_call,
            'by_service': service_costs
        }
    
    def _generate_recommendations(self, 
                                 cost_data: Dict[str, Any], 
                                 usage_metrics: Dict[str, Any],
                                 cost_per_call: Dict[str, float]) -> List[str]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        # Overall cost recommendations
        overall_cost_per_call = cost_per_call.get('overall', 0)
        
        if overall_cost_per_call > 0.01:  # $0.01 per call
            recommendations.append(
                f"💰 High cost per call: ${overall_cost_per_call:.4f}. "
                "Consider optimizing Lambda memory or enabling caching."
            )
        elif overall_cost_per_call < 0.002:  # $0.002 per call
            recommendations.append(
                f"✅ Excellent cost efficiency: ${overall_cost_per_call:.4f} per call"
            )
        
        # Lambda-specific recommendations
        lambda_cost = cost_per_call.get('by_service', {}).get('AWS Lambda', 0)
        if lambda_cost > 0.005:
            recommendations.append(
                "🔧 Consider reducing Lambda memory size or enabling Provisioned Concurrency "
                "to reduce Lambda costs."
            )
        
        # Usage-based recommendations
        total_requests = usage_metrics.get('total_requests', 0)
        if total_requests < 100:
            recommendations.append(
                "📈 Low usage volume. Consider using smaller Lambda instances or "
                "reducing Provisioned Concurrency."
            )
        elif total_requests > 10000:
            recommendations.append(
                "🚀 High usage volume. Consider implementing more aggressive caching "
                "and batch processing to optimize costs."
            )
        
        # API Gateway recommendations
        api_cost = cost_per_call.get('by_service', {}).get('Amazon API Gateway', 0)
        if api_cost > 0.003:
            recommendations.append(
                "🌐 Consider enabling response compression and caching to reduce API Gateway costs."
            )
        
        # General recommendations
        recommendations.extend([
            "📊 Monitor CloudWatch metrics regularly to identify optimization opportunities",
            "🔄 Review and adjust Lambda memory allocation based on actual usage",
            "💾 Implement caching to reduce external API calls",
            "⏰ Consider using scheduled Lambda functions for periodic maintenance tasks"
        ])
        
        return recommendations

# Global instance
_cost_analyzer = None

def get_cost_analyzer() -> CostAnalyzer:
    """Get global cost analyzer."""
    global _cost_analyzer
    if _cost_analyzer is None:
        _cost_analyzer = CostAnalyzer()
    return _cost_analyzer
```

---

## Implementation Roadmap

### Week 1: Foundation (Immediate Performance Wins)

**Day 1-2: Lambda Optimization**
- [ ] Update `template.yaml` with 512MB memory allocation
- [ ] Implement connection pooling in `mem0_client.py`
- [ ] Add performance monitoring to all handlers
- [ ] Test and validate memory usage improvements

**Day 3-4: Provisioned Concurrency**
- [ ] Add Provisioned Concurrency configuration
- [ ] Configure auto-scaling policies
- [ ] Test cold start elimination
- [ ] Monitor cost impact

**Day 5-7: Response Compression**
- [ ] Implement gzip compression
- [ ] Add compression logic to all handlers
- [ ] Test payload size reduction
- [ ] Validate performance improvement

### Week 2: Agent Specialization

**Day 8-9: Configuration System**
- [ ] Create `config/agent_types.json`
- [ ] Implement `AgentConfigManager`
- [ ] Add configuration validation
- [ ] Test configuration loading

**Day 10-12: Specialized Memory Manager**
- [ ] Implement `SpecializedMemoryManager`
- [ ] Add agent-specific field extraction
- [ ] Implement memory type weighting
- [ ] Test with different agent types

**Day 13-14: Handler Updates**
- [ ] Update all Lambda handlers with specialization
- [ ] Add agent type detection
- [ ] Implement agent-specific responses
- [ ] Test backward compatibility

### Week 3: Advanced Optimizations

**Day 15-17: Caching Layer**
- [ ] Implement `CacheManager`
- [ ] Add intelligent caching to memory operations
- [ ] Implement cache invalidation strategies
- [ ] Test cache hit rates and performance

**Day 18-19: Batch Processing**
- [ ] Implement `BatchProcessor`
- [ ] Add batch processing for memory operations
- [ ] Configure SQS queue for async processing
- [ ] Test batch processing efficiency

**Day 20-21: Async Processing**
- [ ] Enhance PostCall handler with async processing
- [ ] Implement S3 storage for raw data
- [ ] Add SQS queue integration
- [ ] Test async processing reliability

### Week 4: Monitoring & Analytics

**Day 22-24: Performance Monitoring**
- [ ] Implement `PerformanceCollector`
- [ ] Add CloudWatch metrics integration
- [ ] Create performance analysis tools
- [ ] Set up monitoring dashboards

**Day 25-26: Cost Analytics**
- [ ] Implement `CostAnalyzer`
- [ ] Add cost tracking and analysis
- [ ] Generate optimization recommendations
- [ ] Create cost reports

**Day 27-28: Testing & Documentation**
- [ ] Comprehensive integration testing
- [ ] Performance benchmarking
- [ ] Update documentation
- [ ] Create deployment guides

---

## Testing Strategy

### Performance Testing

**Load Testing Script:**
```python
# scripts/performance_test.py
import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any

class PerformanceTester:
    """Load testing tool for AgenticMemory endpoints."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = []
    
    async def test_endpoint(self, 
                           endpoint: str, 
                           payload: Dict[str, Any],
                           concurrent_users: int = 10,
                           duration_seconds: int = 60) -> Dict[str, Any]:
        """Test endpoint under load."""
        
        async def make_request(session, user_id):
            start_time = time.time()
            try:
                async with session.post(
                    f"{self.base_url}{endpoint}",
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    await response.text()
                    duration = (time.time() - start_time) * 1000
                    
                    return {
                        'user_id': user_id,
                        'duration_ms': duration,
                        'status_code': response.status,
                        'success': response.status == 200
                    }
            except Exception as e:
                return {
                    'user_id': user_id,
                    'duration_ms': (time.time() - start_time) * 1000,
                    'status_code': 0,
                    'success': False,
                    'error': str(e)
                }
        
        # Run load test
        async with aiohttp.ClientSession() as session:
            tasks = []
            start_time = time.time()
            
            while time.time() - start_time < duration_seconds:
                # Create batch of concurrent requests
                batch_tasks = [
                    make_request(session, f"user_{i}_{int(time.time())}")
                    for i in range(concurrent_users)
                ]
                
                batch_results = await asyncio.gather(*batch_tasks)
                self.results.extend(batch_results)
                
                # Wait between batches
                await asyncio.sleep(1)
        
        # Analyze results
        return self._analyze_results(endpoint)
    
    def _analyze_results(self, endpoint: str) -> Dict[str, Any]:
        """Analyze test results."""
        if not self.results:
            return {'error': 'No results to analyze'}
        
        successful_results = [r for r in self.results if r['success']]
        failed_results = [r for r in self.results if not r['success']]
        
        durations = [r['duration_ms'] for r in successful_results]
        
        analysis = {
            'endpoint': endpoint,
            'total_requests': len(self.results),
            'successful_requests': len(successful_results),
            'failed_requests': len(failed_results),
            'success_rate': (len(successful_results) / len(self.results)) * 100,
            'avg_response_time_ms': statistics.mean(durations) if durations else 0,
            'p50_response_time_ms': statistics.median(durations) if durations else 0,
            'p95_response_time_ms': self._percentile(durations, 95) if durations else 0,
            'p99_response_time_ms': self._percentile(durations, 99) if durations else 0,
            'min_response_time_ms': min(durations) if durations else 0,
            'max_response_time_ms': max(durations) if durations else 0
        }
        
        # Error analysis
        if failed_results:
            error_types = {}
            for result in failed_results:
                error = result.get('error', f"HTTP {result['status_code']}")
                error_types[error] = error_types.get(error, 0) + 1
            
            analysis['error_breakdown'] = error_types
        
        return analysis
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

# Usage example
async def run_performance_tests():
    """Run comprehensive performance tests."""
    tester = PerformanceTester("https://your-api-gateway-url.execute-api.region.amazonaws.com/Prod")
    
    # Test ClientData endpoint
    client_data_payload = {
        "caller_id": "+16129782029",
        "agent_type": "elevenlabs_customer_support"
    }
    
    client_data_results = await tester.test_endpoint(
        "/client-data",
        client_data_payload,
        concurrent_users=5,
        duration_seconds=30
    )
    
    print("ClientData Results:")
    print(f"Success Rate: {client_data_results['success_rate']:.1f}%")
    print(f"Avg Response Time: {client_data_results['avg_response_time_ms']:.1f}ms")
    print(f"P95 Response Time: {client_data_results['p95_response_time_ms']:.1f}ms")
    
    # Test Retrieve endpoint
    retrieve_payload = {
        "query": "previous interactions",
        "user_id": "+16129782029",
        "agent_type": "elevenlabs_customer_support"
    }
    
    retrieve_results = await tester.test_endpoint(
        "/retrieve",
        retrieve_payload,
        concurrent_users=5,
        duration_seconds=30
    )
    
    print("\nRetrieve Results:")
    print(f"Success Rate: {retrieve_results['success_rate']:.1f}%")
    print(f"Avg Response Time: {retrieve_results['avg_response_time_ms']:.1f}ms")
    print(f"P95 Response Time: {retrieve_results['p95_response_time_ms']:.1f}ms")

if __name__ == "__main__":
    asyncio.run(run_performance_tests())
```

### Integration Testing

```python
# tests/integration_test.py
import pytest
import asyncio
import json
from src.shared.agent_config import get_config_manager
from src.shared.specialized_memory_manager import SpecializedMemoryManager
from src.shared.cache_manager import get_cache_manager

class TestIntegration:
    """Integration tests for optimized AgenticMemory system."""
    
    @pytest.fixture
    def config_manager(self):
        return get_config_manager()
    
    @pytest.fixture
    def cache_manager(self):
        return get_cache_manager()
    
    def test_agent_config_loading(self, config_manager):
        """Test agent configuration loading."""
        # Test customer support config
        support_config = config_manager.get_agent_config('elevenlabs_customer_support')
        assert support_config is not None
        assert 'memory_config' in support_config
        assert 'performance_config' in support_config
        
        # Test sales config
        sales_config = config_manager.get_agent_config('elevenlabs_sales_agent')
        assert sales_config is not None
        assert 'budget' in sales_config['memory_config']['auto_extract']
    
    def test_specialized_memory_manager(self):
        """Test specialized memory manager."""
        # Test customer support manager
        support_manager = SpecializedMemoryManager('elevenlabs_customer_support')
        assert support_manager.agent_type == 'elevenlabs_customer_support'
        assert 'issue_type' in support_manager.auto_extract_fields
        
        # Test sales manager
        sales_manager = SpecializedMemoryManager('elevenlabs_sales_agent')
        assert sales_manager.agent_type == 'elevenlabs_sales_agent'
        assert 'budget' in sales_manager.auto_extract_fields
    
    def test_field_extraction(self):
        """Test agent-specific field extraction."""
        sales_manager = SpecializedMemoryManager('elevenlabs_sales_agent')
        
        # Test budget extraction
        content = "The customer has a budget of $5000 and wants to implement within 3 months"
        fields = sales_manager.extract_agent_fields(content)
        
        assert 'budget' in fields
        assert '$5000' in fields['budget'] or '5000' in fields['budget']
        assert 'timeline' in fields
        assert '3 months' in fields['timeline']
    
    def test_caching(self, cache_manager):
        """Test caching functionality."""
        # Test cache set/get
        test_key = "test_key"
        test_value = {"data": "test_data"}
        
        cache_manager.set(test_key, test_value, ttl=60)
        cached_value = cache_manager.get(test_key)
        
        assert cached_value == test_value
        
        # Test cache expiration
        cache_manager.set(test_key, test_value, ttl=1)
        asyncio.sleep(2)  # Wait for expiration
        expired_value = cache_manager.get(test_key)
        
        assert expired_value is None
    
    def test_memory_scoring(self):
        """Test memory relevance scoring."""
        sales_manager = SpecializedMemoryManager('elevenlabs_sales_agent')
        
        # Test memory with sales relevance
        sales_memory = {
            'memory': 'Customer interested in premium plan with $10k budget',
            'metadata': {
                'memory_type': 'lead',
                'budget': '$10,000',
                'timestamp': '2025-10-01T10:00:00Z'
            }
        }
        
        score = sales_manager._calculate_memory_score(sales_memory)
        assert score > 1.0  # Should be boosted due to lead type and budget
        
        # Test old memory
        old_memory = {
            'memory': 'Old conversation from 6 months ago',
            'metadata': {
                'memory_type': 'factual',
                'timestamp': '2025-04-01T10:00:00Z'
            }
        }
        
        old_score = sales_manager._calculate_memory_score(old_memory)
        assert old_score < score  # Should have lower score due to age and type

if __name__ == "__main__":
    pytest.main([__file__])
```

---

## Cost-Benefit Analysis

### Performance Improvements vs. Cost

| Optimization | Performance Gain | Cost Impact | ROI |
|--------------|------------------|-------------|-----|
| **Memory Increase (256MB→512MB)** | 20-30% faster execution | +$0.000000208/GB-second | High |
| **Provisioned Concurrency** | Eliminates 3-5s cold starts | +$5-7/month | Very High |
| **Connection Pooling** | 50-100ms faster API calls | No additional cost | Very High |
| **Response Compression** | 30-50% faster transfers | Minimal CPU cost | High |
| **Intelligent Caching** | 60-80% fewer API calls | Minimal memory cost | Very High |
| **Agent Specialization** | Better relevance, 20% faster | No additional cost | High |

### Monthly Cost Comparison (10K calls/month)

**Current System:**
- Lambda Compute: $5-8
- Lambda Requests: $0.20
- API Gateway: $1-2
- CloudWatch Logs: $0.50
- Data Transfer: $0.10
- **Total: $7-11/month**

**Optimized System:**
- Lambda Compute (512MB): $8-12
- Lambda Requests: $0.20
- API Gateway: $1-2
- Provisioned Concurrency: $5-7
- CloudWatch Logs: $0.50
- Data Transfer: $0.08 (with compression)
- **Total: $15-22/month**

**Performance Gains:**
- Cold start elimination: 3-5 seconds → <100ms
- Warm execution: 500ms → 200ms
- 99th percentile: <400ms
- Cache hit rate: 60-80%
- Cost per call: $0.0015-0.0022

**ROI Calculation:**
- Additional cost: $8-11/month
- Performance improvement: 60-80%
- User experience improvement: Significant
- Scalability improvement: 10x capacity

### Scaling Cost Projections

| Monthly Calls | Current Cost | Optimized Cost | Cost per Call (Current) | Cost per Call (Optimized) |
|---------------|--------------|----------------|------------------------|---------------------------|
| 1K | $2-3 | $8-10 | $0.0025 | $0.008 |
| 10K | $7-11 | $15-22 | $0.0009 | $0.0018 |
| 100K | $50-75 | $50-70 | $0.0006 | $0.0006 |
| 1M | $450-650 | $450-600 | $0.0005 | $0.0005 |

**Key Insights:**
- At low volumes (<10K calls/month), optimization has higher relative cost
- At medium volumes (10K-100K calls/month), optimization becomes cost-effective
- At high volumes (>100K calls/month), optimization provides significant cost savings

---

## Deployment Guide

### Step 1: Update Infrastructure

```bash
# 1. Update template.yaml with new configurations
cp template.yaml template.yaml.backup

# 2. Add new resources to template.yaml
# - Provisioned Concurrency
# - S3 bucket for async processing
# - SQS queue for async processing
# - Enhanced IAM permissions

# 3. Build and deploy
sam build
sam deploy --parameter-overrides \
  ProvisionedConcurrencyEnabled=true \
  ProvisionedConcurrency=2 \
  AsyncProcessingEnabled=true
```

### Step 2: Deploy Configuration Files

```bash
# 1. Create config directory
mkdir -p config

# 2. Deploy agent configuration
aws s3 cp config/agent_types.json s3://your-config-bucket/agent-types.json

# 3. Update environment variables to point to config
aws lambda update-function-configuration \
  --function-name elevenlabs-agentic-memory-lambda-function-client-data \
  --environment "Variables={CONFIG_S3_BUCKET=your-config-bucket,CONFIG_S3_KEY=agent-types.json}"
```

### Step 3: Set Up Monitoring

```bash
# 1. Create CloudWatch dashboards
aws cloudwatch put-dashboard \
  --dashboard-name AgenticMemory-Performance \
  --dashboard-body file://monitoring/dashboard.json

# 2. Create alarms
aws cloudwatch put-metric-alarm \
  --alarm-name "AgenticMemory-HighLatency" \
  --metric-name "Duration" \
  --namespace "AWS/Lambda" \
  --statistic "Average" \
  --threshold 1000 \
  --comparison-operator "GreaterThanThreshold" \
  --evaluation-periods 2

# 3. Create cost budget
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget '{
    "BudgetName": "AgenticMemory-Monthly",
    "BudgetType": "COST",
    "TimeUnit": "MONTHLY",
    "BudgetLimit": {
      "Amount": "50",
      "Unit": "USD"
    },
    "CostFilters": {
      "Service": ["AWS Lambda", "Amazon API Gateway", "Amazon S3", "Amazon SQS"]
    }
  }'
```

### Step 4: Performance Testing

```bash
# 1. Run performance tests
python scripts/performance_test.py

# 2. Validate optimizations
python scripts/validate_optimizations.py

# 3. Monitor metrics
aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow
```

---

## Troubleshooting Guide

### Common Issues and Solutions

**Issue 1: High Memory Usage**
```
Symptoms: Lambda out of memory errors
Solution: 
1. Check memory usage in CloudWatch logs
2. Increase memory allocation in 128MB increments
3. Optimize memory usage in code
4. Add memory monitoring
```

**Issue 2: Cold Starts Persist**
```
Symptoms: Still experiencing 3-5 second delays
Solution:
1. Verify Provisioned Concurrency is enabled
2. Check if concurrency is sufficient for traffic
3. Monitor Provisioned Concurrency utilization
4. Consider increasing concurrency allocation
```

**Issue 3: Cache Not Working**
```
Symptoms: No cache hits, high API call volume
Solution:
1. Check cache configuration
2. Verify cache TTL settings
3. Monitor cache hit rates
4. Check for cache key collisions
```

**Issue 4: Agent Configuration Not Loading**
```
Symptoms: Default behavior instead of agent-specific
Solution:
1. Verify configuration file exists in S3
2. Check IAM permissions for S3 access
3. Validate configuration JSON format
4. Check environment variables
```

**Issue 5: Async Processing Failures**
```
Symptoms: Post-call data not processed
Solution:
1. Check SQS queue for messages
2. Verify S3 permissions
3. Check async processing logs
4. Validate message format
```

### Performance Debugging Commands

```bash
# Check Lambda performance
aws lambda get-function-configuration \
  --function-name elevenlabs-agentic-memory-lambda-function-client-data \
  --query 'MemorySize,Timeout,State'

# Check Provisioned Concurrency
aws lambda get-provisioned-concurrency-config \
  --function-name elevenlabs-agentic-memory-lambda-function-client-data \
  --qualifier Prod

# Monitor real-time metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=elevenlabs-agentic-memory-lambda-function-client-data \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 60 \
  --statistics Average

# Check cache performance
aws logs filter-log-events \
  --log-group-name /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data \
  --filter-pattern "Cache hit|Cache miss"
```

---

## Conclusion

This comprehensive optimization guide provides a roadmap to transform your AgenticMemory system into a high-performance, cost-effective platform capable of supporting multiple ElevenLabs agent types. The phased approach ensures minimal disruption while delivering immediate performance benefits.

### Key Takeaways:

1. **Performance First**: Focus on eliminating cold starts and optimizing execution time
2. **Agent Specialization**: Tailor memory behavior to specific agent types for better relevance
3. **Intelligent Caching**: Reduce external API calls and improve response times
4. **Comprehensive Monitoring**: Track performance and costs to optimize continuously
5. **Scalable Architecture**: Design for growth from 10 to 1000+ concurrent calls

### Expected Outcomes:

- **60-80% performance improvement** across all metrics
- **Consistent sub-200ms response times** for warm calls
- **Elimination of cold starts** with Provisioned Concurrency
- **Intelligent memory management** for different agent types
- **Cost-effective scaling** as your usage grows

The implementation roadmap provides clear, actionable steps to achieve these outcomes while maintaining the reliability and production-readiness of your current system.

---

**Next Steps:**
1. Review and approve the optimization plan
2. Begin Phase 1 implementation (Lambda optimization)
3. Set up monitoring and alerting
4. Conduct performance testing
5. Iterate based on results and feedback

This optimization will position your AgenticMemory system as a leading solution for voice AI memory management, capable of scaling to support enterprise-level requirements while maintaining excellent performance and cost efficiency.
