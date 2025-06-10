"""
Tests for the BaseTool class functionality.
"""
import pytest
import pytest_asyncio
from unittest.mock import MagicMock, patch
from semaphore_mcp.tools.base import BaseTool


class TestBaseTool:
    """Test suite for BaseTool base class functionality."""
    
    @pytest_asyncio.fixture
    async def base_tool(self):
        """Create a BaseTool instance with a mock API client."""
        mock_client = MagicMock()
        return BaseTool(mock_client)
    
    @pytest.mark.asyncio
    async def test_init(self, base_tool):
        """Test BaseTool initialization."""
        assert base_tool.semaphore is not None
        
    @pytest.mark.asyncio
    async def test_handle_error(self, base_tool):
        """Test error handling functionality."""
        test_exception = Exception("Test error")
        operation = "testing"
        
        # The handle_error method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            base_tool.handle_error(test_exception, operation)
        
        # Verify the error message contains our operation
        assert "testing" in str(excinfo.value)
