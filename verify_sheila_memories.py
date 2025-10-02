#!/usr/bin/env python3
"""
Verify memories stored for +15074595005 (Sheila)
"""

import json
import os
from mem0 import MemoryClient

# Initialize Mem0 client
MEM0_API_KEY = os.getenv("MEM0_API_KEY") or input("Enter MEM0_API_KEY: ").strip()
MEM0_ORG_ID = os.getenv("MEM0_ORG_ID") or input("Enter MEM0_ORG_ID: ").strip()
MEM0_PROJECT_ID = os.getenv("MEM0_PROJECT_ID") or input("Enter MEM0_PROJECT_ID: ").strip()

client = MemoryClient(
    api_key=MEM0_API_KEY,
    org_id=MEM0_ORG_ID,
    project_id=MEM0_PROJECT_ID
)

caller_id = "+15074595005"

print(f"🔍 Retrieving all memories for {caller_id}...")
print("=" * 80)

try:
    result = client.get_all(user_id=caller_id)
    
    memories = result.get("results", [])
    
    print(f"\n📊 Total memories: {len(memories)}")
    
    if memories:
        # Separate by type
        factual_memories = [m for m in memories if m.get("metadata", {}).get("type") == "factual"]
        semantic_memories = [m for m in memories if m.get("metadata", {}).get("type") == "semantic"]
        
        print(f"   Factual: {len(factual_memories)}")
        print(f"   Semantic: {len(semantic_memories)}")
        
        print("\n" + "=" * 80)
        print("FACTUAL MEMORIES (Summaries & Evaluations)")
        print("=" * 80)
        
        for i, mem in enumerate(factual_memories, 1):
            print(f"\n[{i}] Memory ID: {mem.get('id', 'N/A')}")
            print(f"    Created: {mem.get('created_at', 'N/A')}")
            print(f"    Updated: {mem.get('updated_at', 'N/A')}")
            
            metadata = mem.get("metadata", {})
            print(f"    Agent ID: {metadata.get('agent_id', 'N/A')}")
            print(f"    Conversation ID: {metadata.get('conversation_id', 'N/A')}")
            print(f"    Timestamp: {metadata.get('timestamp', 'N/A')}")
            
            memory_text = mem.get("memory", "")
            if len(memory_text) > 200:
                print(f"    Memory: {memory_text[:200]}...")
            else:
                print(f"    Memory: {memory_text}")
        
        if semantic_memories:
            print("\n" + "=" * 80)
            print("SEMANTIC MEMORIES (Conversation Transcripts)")
            print("=" * 80)
            
            for i, mem in enumerate(semantic_memories, 1):
                print(f"\n[{i}] Memory ID: {mem.get('id', 'N/A')}")
                print(f"    Created: {mem.get('created_at', 'N/A')}")
                
                metadata = mem.get("metadata", {})
                print(f"    Conversation ID: {metadata.get('conversation_id', 'N/A')}")
                
                memory_text = mem.get("memory", "")
                if len(memory_text) > 200:
                    print(f"    Memory: {memory_text[:200]}...")
                else:
                    print(f"    Memory: {memory_text}")
        
        print("\n" + "=" * 80)
        print(f"✅ SUCCESS: Found {len(memories)} memories for {caller_id}")
        
        if len(factual_memories) > 0 and len(semantic_memories) == 0:
            print("\n⚠️  NOTE: Only factual memory found. Semantic memory likely timed out.")
            print("    This is expected for the 161-message conversation test.")
        
    else:
        print(f"\n❌ No memories found for {caller_id}")
        print("   Possible reasons:")
        print("   - Lambda timed out before storing any memories")
        print("   - Wrong caller ID")
        print("   - Mem0 API issue")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
