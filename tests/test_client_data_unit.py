"""
Unit tests for client_data Lambda handler functions

Tests the helper functions for name extraction and greeting generation.
"""

import pytest
import sys
import os

# Set dummy environment variables before importing handler
os.environ['MEM0_API_KEY'] = 'test-key'
os.environ['MEM0_ORG_ID'] = 'test-org'
os.environ['MEM0_PROJECT_ID'] = 'test-project'
os.environ['ELEVENLABS_WORKSPACE_KEY'] = 'test-workspace-key'

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'client_data'))

from handler import extract_caller_name, generate_personalized_greeting


class TestExtractCallerName:
    """Test cases for extract_caller_name function"""
    
    def test_extract_name_from_simple_pattern(self):
        """Test extraction with 'name is' pattern"""
        memories = ["User name is John Smith", "Prefers email contact"]
        result = extract_caller_name(memories)
        assert result == "John Smith"
    
    def test_extract_name_from_called_pattern(self):
        """Test extraction with 'called' pattern"""
        memories = ["User called Sarah Johnson", "Lives in Minneapolis"]
        result = extract_caller_name(memories)
        assert result == "Sarah Johnson"
    
    def test_extract_name_from_my_name_pattern(self):
        """Test extraction with 'my name is' pattern"""
        memories = ["My name is Michael Davis", "Premium account holder"]
        result = extract_caller_name(memories)
        assert result == "Michael Davis"
    
    def test_extract_single_name(self):
        """Test extraction of single name"""
        memories = ["User name is Jennifer", "Gold tier member"]
        result = extract_caller_name(memories)
        assert result == "Jennifer"
    
    def test_extract_name_case_insensitive(self):
        """Test that extraction works with different cases"""
        memories = ["user name is ROBERT WILSON", "Active since 2023"]
        result = extract_caller_name(memories)
        assert result == "Robert Wilson"
    
    def test_no_name_found(self):
        """Test when no name pattern is found"""
        memories = ["Premium account holder", "Prefers phone calls"]
        result = extract_caller_name(memories)
        assert result is None
    
    def test_empty_memories(self):
        """Test with empty memory list"""
        memories = []
        result = extract_caller_name(memories)
        assert result is None
    
    def test_exclude_non_names(self):
        """Test that common words are excluded as names"""
        memories = ["User wants help with account", "User needs update"]
        result = extract_caller_name(memories)
        assert result is None
    
    def test_extract_from_semantic_memory(self):
        """Test extraction from conversational context"""
        memories = [
            "User Emily called about billing issue",
            "Previous conversation about account update"
        ]
        result = extract_caller_name(memories)
        assert result == "Emily"
    
    def test_first_match_priority(self):
        """Test that first valid match is returned"""
        memories = [
            "Customer name: Jessica Brown",
            "User name is Amanda Green"
        ]
        result = extract_caller_name(memories)
        # Should find Jessica first
        assert result in ["Jessica Brown", "Amanda Green"]


class TestGeneratePersonalizedGreeting:
    """Test cases for generate_personalized_greeting function"""
    
    def test_new_caller_greeting(self):
        """Test greeting for first-time caller"""
        greeting = generate_personalized_greeting(
            caller_name=None,
            is_returning=False
        )
        assert greeting == "Hello! How may I help you today?"
    
    def test_returning_caller_with_name(self):
        """Test personalized greeting for returning caller with known name"""
        greeting = generate_personalized_greeting(
            caller_name="John",
            is_returning=True
        )
        assert "John" in greeting
        assert greeting.startswith("Hello John!")
        assert "assist you" in greeting
    
    def test_returning_caller_no_name(self):
        """Test greeting for returning caller without name"""
        greeting = generate_personalized_greeting(
            caller_name=None,
            is_returning=True
        )
        assert "called before" in greeting.lower()
        assert "name" in greeting.lower()
    
    def test_greeting_with_premium_status(self):
        """Test that premium account status is mentioned"""
        greeting = generate_personalized_greeting(
            caller_name="Sarah",
            is_returning=True,
            account_status="Premium account holder"
        )
        assert "Sarah" in greeting
        assert "premium customer" in greeting.lower()
    
    def test_greeting_with_vip_status(self):
        """Test that VIP status is mentioned"""
        greeting = generate_personalized_greeting(
            caller_name="Michael",
            is_returning=True,
            account_status="VIP member since 2020"
        )
        assert "Michael" in greeting
        assert "VIP" in greeting
    
    def test_greeting_with_last_interaction(self):
        """Test that last interaction is referenced"""
        greeting = generate_personalized_greeting(
            caller_name="Emily",
            is_returning=True,
            last_interaction="Last inquiry about billing"
        )
        assert "Emily" in greeting
        assert "inquiry" in greeting.lower()
    
    def test_greeting_with_preferences(self):
        """Test that preferences are mentioned"""
        greeting = generate_personalized_greeting(
            caller_name="David",
            is_returning=True,
            preferences=["Prefers email communication"]
        )
        assert "David" in greeting
        assert "email" in greeting.lower()
    
    def test_greeting_combines_multiple_contexts(self):
        """Test greeting with multiple context pieces"""
        greeting = generate_personalized_greeting(
            caller_name="Jessica",
            is_returning=True,
            account_status="Gold tier member",
            last_interaction="Previous issue with payment"
        )
        assert "Jessica" in greeting
        assert "gold" in greeting.lower()
        assert "previous" in greeting.lower() or "issue" in greeting.lower()
    
    def test_greeting_structure(self):
        """Test that greeting has proper structure"""
        greeting = generate_personalized_greeting(
            caller_name="Robert",
            is_returning=True,
            account_status="Premium member"
        )
        # Should start with name, have context, end with question
        assert greeting.startswith("Hello Robert!")
        assert "?" in greeting
        assert greeting.endswith("?")


class TestGreetingEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_greeting_no_optional_params(self):
        """Test greeting with only required parameters"""
        greeting = generate_personalized_greeting(
            caller_name="Test",
            is_returning=True
        )
        assert "Test" in greeting
        assert "?" in greeting
    
    def test_greeting_with_none_preferences(self):
        """Test that None preferences list is handled"""
        greeting = generate_personalized_greeting(
            caller_name="User",
            is_returning=True,
            preferences=None
        )
        assert "User" in greeting
        assert isinstance(greeting, str)
    
    def test_greeting_length_reasonable(self):
        """Test that greeting isn't excessively long"""
        greeting = generate_personalized_greeting(
            caller_name="TestUser",
            is_returning=True,
            account_status="Premium VIP Gold member",
            last_interaction="Multiple inquiries about billing issues",
            preferences=["Prefers email", "Likes detailed explanations"]
        )
        # Should be conversational length, not a novel
        assert len(greeting) < 500
        assert len(greeting) > 20


class TestNameExtractionPatterns:
    """Test various real-world memory patterns for name extraction"""
    
    def test_mem0_factual_format(self):
        """Test extraction from typical Mem0 factual memory format"""
        memories = [
            "The user's name is Stefan Anderson",
            "User has a premium account",
            "Prefers morning calls"
        ]
        result = extract_caller_name(memories)
        assert result == "Stefan Anderson"
    
    def test_conversational_format(self):
        """Test extraction from conversational memory"""
        memories = [
            "User Amanda mentioned she prefers text messages",
            "Previous conversation about account settings"
        ]
        result = extract_caller_name(memories)
        assert result == "Amanda"
    
    def test_customer_service_format(self):
        """Test extraction from customer service style memory"""
        memories = [
            "Customer name: Christopher Lee",
            "Account number: 12345",
            "Last contact: 2025-01-15"
        ]
        result = extract_caller_name(memories)
        assert result == "Christopher Lee"
    
    def test_mixed_format_memories(self):
        """Test extraction when name appears in multiple formats"""
        memories = [
            "Premium customer",
            "User Jennifer works in tech",
            "Prefers evening calls"
        ]
        result = extract_caller_name(memories)
        assert result == "Jennifer"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
