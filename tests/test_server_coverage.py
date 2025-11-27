"""
Additional tests for SemaphoreMCPServer to improve coverage.
These tests focus on server startup and configuration methods.
"""

from unittest.mock import MagicMock, patch

from semaphore_mcp.server import SemaphoreMCPServer, start_server


class TestSemaphoreMCPServerCoverage:
    """Additional coverage tests for SemaphoreMCPServer."""

    def test_server_initialization_with_parameters(self):
        """Test server initialization with explicit parameters."""
        server = SemaphoreMCPServer("http://test.example.com", "test-token")

        assert server.url == "http://test.example.com"
        assert server.token == "test-token"
        assert server.semaphore is not None
        assert server.project_tools is not None
        assert server.template_tools is not None
        assert server.task_tools is not None
        assert server.environment_tools is not None

    @patch("semaphore_mcp.server.get_config")
    def test_server_initialization_from_config(self, mock_get_config):
        """Test server initialization using config values."""
        mock_get_config.side_effect = lambda key: {
            "SEMAPHORE_URL": "http://config.example.com",
            "SEMAPHORE_API_TOKEN": "config-token",
        }.get(key)

        server = SemaphoreMCPServer()

        assert server.url == "http://config.example.com"
        assert server.token == "config-token"

    @patch("semaphore_mcp.server.get_config")
    def test_server_initialization_partial_config(self, mock_get_config):
        """Test server initialization with partial config override."""
        mock_get_config.side_effect = lambda key: {
            "SEMAPHORE_URL": "http://config.example.com",
            "SEMAPHORE_API_TOKEN": "config-token",
        }.get(key)

        # Override URL but use config token
        server = SemaphoreMCPServer("http://override.example.com")

        assert server.url == "http://override.example.com"
        assert server.token == "config-token"

    def test_register_tools_called(self):
        """Test that register_tools is called during initialization."""
        with patch.object(SemaphoreMCPServer, "register_tools") as mock_register:
            SemaphoreMCPServer("http://test.example.com", "test-token")
            mock_register.assert_called_once()

    def test_register_tools_all_tools_registered(self):
        """Test that all tools are properly registered."""
        server = SemaphoreMCPServer("http://test.example.com", "test-token")

        # Verify FastMCP instance was created
        assert server.mcp is not None
        assert server.mcp.name == "semaphore"

        # The actual tool registration calls are mocked by FastMCP
        # We just verify the tool instances exist
        assert hasattr(server, "project_tools")
        assert hasattr(server, "template_tools")
        assert hasattr(server, "task_tools")
        assert hasattr(server, "environment_tools")

    @patch("semaphore_mcp.server.logger")
    def test_run_method_logging(self, mock_logger):
        """Test the run method logs startup message."""
        server = SemaphoreMCPServer("http://test.example.com", "test-token")

        # Mock the FastMCP run method to avoid actually starting the server
        with patch.object(server.mcp, "run") as mock_run:
            server.run()

            # Check that both log messages were called
            assert mock_logger.info.call_count == 2
            mock_logger.info.assert_any_call(
                "Starting FastMCP server for SemaphoreUI at http://test.example.com"
            )
            mock_logger.info.assert_any_call("STDIO transport")
            mock_run.assert_called_once_with(transport="stdio")

    @patch("semaphore_mcp.server.SemaphoreMCPServer")
    def test_start_server_function_with_parameters(self, mock_server_class):
        """Test start_server function with parameters."""
        mock_server_instance = MagicMock()
        mock_server_class.return_value = mock_server_instance

        start_server("http://test.example.com", "test-token")

        mock_server_class.assert_called_once_with(
            "http://test.example.com", "test-token", host="127.0.0.1", port=8000
        )
        mock_server_instance.run.assert_called_once_with(transport="stdio")

    @patch("semaphore_mcp.server.SemaphoreMCPServer")
    def test_start_server_function_without_parameters(self, mock_server_class):
        """Test start_server function without parameters."""
        mock_server_instance = MagicMock()
        mock_server_class.return_value = mock_server_instance

        start_server()

        mock_server_class.assert_called_once_with(
            None, None, host="127.0.0.1", port=8000
        )
        mock_server_instance.run.assert_called_once_with(transport="stdio")

    def test_tool_classes_integration(self):
        """Test that tool classes are properly integrated with semaphore client."""
        with patch("semaphore_mcp.server.create_client") as mock_create_client:
            mock_semaphore = MagicMock()
            mock_create_client.return_value = mock_semaphore

            server = SemaphoreMCPServer("http://test.example.com", "test-token")

            # Verify all tool classes received the same semaphore client
            assert server.project_tools.semaphore == mock_semaphore
            assert server.template_tools.semaphore == mock_semaphore
            assert server.task_tools.semaphore == mock_semaphore
            assert server.environment_tools.semaphore == mock_semaphore

    @patch("semaphore_mcp.server.FastMCP")
    def test_fastmcp_initialization(self, mock_fastmcp_class):
        """Test FastMCP initialization."""
        mock_fastmcp_instance = MagicMock()
        mock_fastmcp_class.return_value = mock_fastmcp_instance

        server = SemaphoreMCPServer("http://test.example.com", "test-token")

        mock_fastmcp_class.assert_called_once_with(
            "semaphore", host="127.0.0.1", port=8000
        )
        assert server.mcp == mock_fastmcp_instance

    def test_tool_registration_methods(self):
        """Test that tool registration calls the correct FastMCP methods."""
        server = SemaphoreMCPServer("http://test.example.com", "test-token")

        # Mock the tool method of FastMCP to track calls
        with patch.object(server.mcp, "tool") as mock_tool:
            mock_tool.return_value = lambda x: x  # Return identity function

            # Call register_tools again to test
            server.register_tools()

            # Verify tool() was called multiple times (once for each registered tool)
            assert mock_tool.call_count > 10  # We have many tools registered

    def test_logging_configuration_imported(self):
        """Test that logging configuration is available in the server module."""
        # Since configure_logging is called at module import time,
        # we can't easily mock it after import. Instead, verify it's imported.
        import semaphore_mcp.server

        assert hasattr(semaphore_mcp.server, "logger")
        assert semaphore_mcp.server.logger is not None

    def test_server_attributes_exist(self):
        """Test that all expected server attributes exist."""
        server = SemaphoreMCPServer("http://test.example.com", "test-token")

        # Test all expected attributes
        required_attributes = [
            "url",
            "token",
            "semaphore",
            "mcp",
            "project_tools",
            "template_tools",
            "task_tools",
            "environment_tools",
        ]

        for attr in required_attributes:
            assert hasattr(server, attr), f"Server missing attribute: {attr}"
            assert getattr(server, attr) is not None, f"Server attribute {attr} is None"

    def test_server_methods_exist(self):
        """Test that all expected server methods exist."""
        server = SemaphoreMCPServer("http://test.example.com", "test-token")

        # Test all expected methods
        required_methods = ["register_tools", "run"]

        for method in required_methods:
            assert hasattr(server, method), f"Server missing method: {method}"
            assert callable(getattr(server, method)), f"Server {method} is not callable"
