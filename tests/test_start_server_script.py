"""Tests for the start_server script."""

import sys
from unittest.mock import MagicMock, patch


class TestParseArgs:
    """Tests for argument parsing."""

    def test_parse_args_defaults(self):
        """Test default argument values."""
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(sys, "argv", ["start_server"]):
                from semaphore_mcp.scripts.start_server import parse_args

                args = parse_args()

                assert args.url == "http://localhost:3000"
                assert args.token is None
                assert args.transport == "stdio"
                assert args.host == "0.0.0.0"
                assert args.port == 8000
                assert args.verbose is False

    def test_parse_args_from_env(self):
        """Test argument values from environment variables."""
        env = {
            "SEMAPHORE_URL": "http://env.example.com",
            "SEMAPHORE_API_TOKEN": "env-token",
            "MCP_TRANSPORT": "http",
            "MCP_HOST": "127.0.0.1",
            "MCP_PORT": "9000",
        }
        with patch.dict("os.environ", env, clear=True):
            with patch.object(sys, "argv", ["start_server"]):
                from semaphore_mcp.scripts.start_server import parse_args

                args = parse_args()

                assert args.url == "http://env.example.com"
                assert args.token == "env-token"
                assert args.transport == "http"
                assert args.host == "127.0.0.1"
                assert args.port == 9000

    def test_parse_args_cli_overrides(self):
        """Test CLI arguments override defaults."""
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(
                sys,
                "argv",
                [
                    "start_server",
                    "--url",
                    "http://cli.example.com",
                    "--token",
                    "cli-token",
                    "--transport",
                    "http",
                    "--host",
                    "192.168.1.1",
                    "--port",
                    "3000",
                    "--verbose",
                ],
            ):
                from semaphore_mcp.scripts.start_server import parse_args

                args = parse_args()

                assert args.url == "http://cli.example.com"
                assert args.token == "cli-token"
                assert args.transport == "http"
                assert args.host == "192.168.1.1"
                assert args.port == 3000
                assert args.verbose is True

    def test_parse_args_verbose_short(self):
        """Test -v short flag for verbose."""
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(sys, "argv", ["start_server", "-v"]):
                from semaphore_mcp.scripts.start_server import parse_args

                args = parse_args()

                assert args.verbose is True


class TestMain:
    """Tests for main function."""

    @patch("semaphore_mcp.scripts.start_server.start_server")
    @patch("semaphore_mcp.scripts.start_server.parse_args")
    def test_main_calls_start_server(self, mock_parse_args, mock_start_server):
        """Test that main calls start_server with parsed args."""
        mock_args = MagicMock()
        mock_args.url = "http://test.example.com"
        mock_args.token = "test-token"
        mock_args.transport = "stdio"
        mock_args.host = "0.0.0.0"
        mock_args.port = 8000
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args

        from semaphore_mcp.scripts.start_server import main

        main()

        mock_start_server.assert_called_once_with(
            semaphore_url="http://test.example.com",
            semaphore_token="test-token",
            transport="stdio",
            host="0.0.0.0",
            port=8000,
        )

    @patch("semaphore_mcp.scripts.start_server.start_server")
    @patch("semaphore_mcp.scripts.start_server.parse_args")
    def test_main_verbose_sets_debug_logging(self, mock_parse_args, mock_start_server):
        """Test that verbose flag enables debug logging."""
        mock_args = MagicMock()
        mock_args.url = "http://test.example.com"
        mock_args.token = "test-token"
        mock_args.transport = "stdio"
        mock_args.host = "0.0.0.0"
        mock_args.port = 8000
        mock_args.verbose = True
        mock_parse_args.return_value = mock_args

        import logging

        from semaphore_mcp.scripts.start_server import main

        main()

        # Verify logger was set to DEBUG
        logger = logging.getLogger("semaphore_mcp")
        assert logger.level == logging.DEBUG

    @patch("semaphore_mcp.scripts.start_server.start_server")
    @patch("semaphore_mcp.scripts.start_server.parse_args")
    def test_main_http_transport(self, mock_parse_args, mock_start_server):
        """Test main with HTTP transport."""
        mock_args = MagicMock()
        mock_args.url = "http://test.example.com"
        mock_args.token = "test-token"
        mock_args.transport = "http"
        mock_args.host = "127.0.0.1"
        mock_args.port = 9000
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args

        from semaphore_mcp.scripts.start_server import main

        main()

        mock_start_server.assert_called_once_with(
            semaphore_url="http://test.example.com",
            semaphore_token="test-token",
            transport="http",
            host="127.0.0.1",
            port=9000,
        )
