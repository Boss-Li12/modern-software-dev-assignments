import os
import pytest
from unittest.mock import patch, MagicMock

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


# ============================================================
# TODO 2: Unit Tests for extract_action_items_llm (AI-Generated)
# ============================================================

class TestExtractActionItemsLLM:
    """
    Unit tests for the LLM-powered action item extraction function.
    Uses mocking to avoid actual LLM API calls during testing.
    
    AI-Generated: These tests were generated with AI assistance for TODO 2.
    """
    
    def _create_mock_response(self, items: list) -> MagicMock:
        """Helper to create a mock Ollama response."""
        mock_response = MagicMock()
        mock_response.message.content = f'{{"items": {items}}}'.replace("'", '"')
        return mock_response
    
    # Test 1: Bullet list input
    @patch('week2.app.services.extract.chat')
    def test_extract_bullet_list(self, mock_chat):
        """Test extraction from bullet list format."""
        mock_chat.return_value = self._create_mock_response([
            "Set up database",
            "Implement user authentication",
            "Write documentation"
        ])
        
        text = """
        Project Tasks:
        - Set up database
        - Implement user authentication
        - Write documentation
        """
        
        result = extract_action_items_llm(text)
        
        assert len(result) == 3
        assert "Set up database" in result
        assert "Implement user authentication" in result
        assert "Write documentation" in result
        mock_chat.assert_called_once()
    
    # Test 2: Keyword-prefixed lines (todo:, action:, next:)
    @patch('week2.app.services.extract.chat')
    def test_extract_keyword_prefixed(self, mock_chat):
        """Test extraction from keyword-prefixed lines."""
        mock_chat.return_value = self._create_mock_response([
            "Review the pull request",
            "Deploy to staging",
            "Schedule team meeting"
        ])
        
        text = """
        Meeting Notes:
        todo: Review the pull request
        action: Deploy to staging
        next: Schedule team meeting
        """
        
        result = extract_action_items_llm(text)
        
        assert len(result) == 3
        assert "Review the pull request" in result
        assert "Deploy to staging" in result
        assert "Schedule team meeting" in result
    
    # Test 3: Empty input
    def test_extract_empty_input(self):
        """Test that empty input returns empty list without calling LLM."""
        result = extract_action_items_llm("")
        assert result == []
        
        result = extract_action_items_llm("   ")
        assert result == []
        
        result = extract_action_items_llm(None)  # type: ignore
        assert result == []
    
    # Test 4: Numbered list input
    @patch('week2.app.services.extract.chat')
    def test_extract_numbered_list(self, mock_chat):
        """Test extraction from numbered list format."""
        mock_chat.return_value = self._create_mock_response([
            "Complete the report",
            "Send email to client",
            "Update project timeline"
        ])
        
        text = """
        Action Items:
        1. Complete the report
        2. Send email to client
        3. Update project timeline
        """
        
        result = extract_action_items_llm(text)
        
        assert len(result) == 3
        assert "Complete the report" in result
    
    # Test 5: Checkbox format input
    @patch('week2.app.services.extract.chat')
    def test_extract_checkbox_format(self, mock_chat):
        """Test extraction from checkbox format."""
        mock_chat.return_value = self._create_mock_response([
            "Fix login bug",
            "Add unit tests",
            "Update README"
        ])
        
        text = """
        Sprint Tasks:
        - [ ] Fix login bug
        - [x] Add unit tests
        - [ ] Update README
        """
        
        result = extract_action_items_llm(text)
        
        assert len(result) == 3
        assert "Fix login bug" in result
    
    # Test 6: Mixed format input
    @patch('week2.app.services.extract.chat')
    def test_extract_mixed_format(self, mock_chat):
        """Test extraction from mixed format input."""
        mock_chat.return_value = self._create_mock_response([
            "Set up CI/CD pipeline",
            "Review code changes",
            "Write API documentation",
            "Fix the critical bug"
        ])
        
        text = """
        Meeting Notes - Jan 20, 2026
        
        Discussion points:
        - [ ] Set up CI/CD pipeline
        todo: Review code changes
        1. Write API documentation
        
        Also, we need to fix the critical bug before release.
        """
        
        result = extract_action_items_llm(text)
        
        assert len(result) == 4
    
    # Test 7: Deduplication
    @patch('week2.app.services.extract.chat')
    def test_extract_deduplication(self, mock_chat):
        """Test that duplicate items are removed."""
        mock_chat.return_value = self._create_mock_response([
            "Fix the bug",
            "Fix the bug",  # Duplicate
            "Update docs",
            "fix the bug"   # Case-insensitive duplicate
        ])
        
        result = extract_action_items_llm("Some notes with duplicates")
        
        # Should have only 2 unique items
        assert len(result) == 2
        assert "Fix the bug" in result
        assert "Update docs" in result
    
    # Test 8: LLM error handling
    @patch('week2.app.services.extract.chat')
    def test_extract_llm_error_handling(self, mock_chat):
        """Test that LLM errors are handled gracefully."""
        mock_chat.side_effect = Exception("LLM connection error")
        
        result = extract_action_items_llm("Some notes")
        
        # Should return empty list on error
        assert result == []
    
    # Test 9: Invalid JSON response handling
    @patch('week2.app.services.extract.chat')
    def test_extract_invalid_json_handling(self, mock_chat):
        """Test handling of invalid JSON response from LLM."""
        mock_response = MagicMock()
        mock_response.message.content = "This is not valid JSON"
        mock_chat.return_value = mock_response
        
        result = extract_action_items_llm("Some notes")
        
        # Should return empty list on parse error
        assert result == []
    
    # Test 10: No action items found
    @patch('week2.app.services.extract.chat')
    def test_extract_no_action_items(self, mock_chat):
        """Test when LLM finds no action items."""
        mock_chat.return_value = self._create_mock_response([])
        
        text = """
        This is just a regular paragraph with no action items.
        It's describing something without any tasks or todos.
        """
        
        result = extract_action_items_llm(text)
        
        assert result == []
