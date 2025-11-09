"""Tests for Ollama agent research tools."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from ollama_agent.tools.web_search import web_search, web_search_def
from ollama_agent.tools.url_fetch import fetch_url, url_fetch_def
from ollama_agent.tools.pdf_parser import parse_pdf, pdf_parser_def
from ollama_agent.tools import TOOL_REGISTRY, TOOL_DEFINITIONS


class TestWebSearch:
    """Test web search tool."""

    def test_web_search_def_structure(self):
        """Test web search definition structure."""
        definition = web_search_def()

        assert definition["type"] == "function"
        assert definition["function"]["name"] == "web_search"
        assert "query" in definition["function"]["parameters"]["properties"]
        assert "max_results" in definition["function"]["parameters"]["properties"]
        assert definition["function"]["parameters"]["required"] == ["query"]

    @patch('ollama_agent.tools.web_search.DDGS')
    def test_web_search_success(self, mock_ddgs):
        """Test successful web search."""
        # Mock DuckDuckGo results
        mock_results = [
            {
                "title": "Test Result 1",
                "href": "https://example.com/1",
                "body": "Test snippet 1"
            },
            {
                "title": "Test Result 2",
                "href": "https://example.com/2",
                "body": "Test snippet 2"
            }
        ]

        mock_instance = MagicMock()
        mock_instance.text.return_value = mock_results
        mock_ddgs.return_value.__enter__.return_value = mock_instance

        result = web_search("test query", max_results=2)

        assert result["success"] is True
        assert len(result["results"]) == 2
        assert result["results"][0]["title"] == "Test Result 1"
        assert result["results"][0]["url"] == "https://example.com/1"
        assert result["query"] == "test query"

    @patch('ollama_agent.tools.web_search.DDGS')
    def test_web_search_error(self, mock_ddgs):
        """Test web search error handling."""
        mock_ddgs.return_value.__enter__.side_effect = Exception("Search failed")

        result = web_search("test query")

        assert result["success"] is False
        assert "error" in result
        assert "Search failed" in result["error"]


class TestUrlFetch:
    """Test URL fetch tool."""

    def test_url_fetch_def_structure(self):
        """Test URL fetch definition structure."""
        definition = url_fetch_def()

        assert definition["type"] == "function"
        assert definition["function"]["name"] == "fetch_url"
        assert "url" in definition["function"]["parameters"]["properties"]
        assert "extract_text" in definition["function"]["parameters"]["properties"]
        assert definition["function"]["parameters"]["required"] == ["url"]

    @patch('ollama_agent.tools.url_fetch.requests.get')
    def test_fetch_url_success(self, mock_get):
        """Test successful URL fetch."""
        # Mock HTML response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body><h1>Test Title</h1><p>Test content</p></body></html>"
        mock_response.headers = {"content-type": "text/html"}
        mock_get.return_value = mock_response

        result = fetch_url("https://example.com", extract_text=True)

        assert result["success"] is True
        assert "Test Title" in result["text"]
        assert "Test content" in result["text"]
        assert result["url"] == "https://example.com"

    @patch('ollama_agent.tools.url_fetch.requests.get')
    def test_fetch_url_no_text_extraction(self, mock_get):
        """Test URL fetch without text extraction."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body><h1>Test</h1></body></html>"
        mock_response.headers = {"content-type": "text/html"}
        mock_get.return_value = mock_response

        result = fetch_url("https://example.com", extract_text=False)

        assert result["success"] is True
        assert "<html>" in result["html"]
        assert "text" not in result

    @patch('ollama_agent.tools.url_fetch.requests.get')
    def test_fetch_url_error(self, mock_get):
        """Test URL fetch error handling."""
        mock_get.side_effect = Exception("Connection failed")

        result = fetch_url("https://example.com")

        assert result["success"] is False
        assert "error" in result
        assert "Connection failed" in result["error"]


class TestPdfParser:
    """Test PDF parser tool."""

    def test_pdf_parser_def_structure(self):
        """Test PDF parser definition structure."""
        definition = pdf_parser_def()

        assert definition["type"] == "function"
        assert definition["function"]["name"] == "parse_pdf"
        assert "url" in definition["function"]["parameters"]["properties"]
        assert "save_path" in definition["function"]["parameters"]["properties"]
        assert definition["function"]["parameters"]["required"] == ["url"]

    @patch('ollama_agent.tools.pdf_parser.requests.get')
    @patch('ollama_agent.tools.pdf_parser.PdfReader')
    def test_parse_pdf_success(self, mock_pdf_reader, mock_get):
        """Test successful PDF parsing."""
        # Mock PDF download
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake pdf content"
        mock_get.return_value = mock_response

        # Mock PDF reading
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test PDF content"

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_reader.metadata = {"/Title": "Test PDF", "/Author": "Test Author"}
        mock_pdf_reader.return_value = mock_reader

        result = parse_pdf("https://example.com/test.pdf")

        assert result["success"] is True
        assert "Test PDF content" in result["text"]
        assert result["metadata"]["title"] == "Test PDF"
        assert result["metadata"]["author"] == "Test Author"
        assert result["url"] == "https://example.com/test.pdf"

    @patch('ollama_agent.tools.pdf_parser.requests.get')
    def test_parse_pdf_download_error(self, mock_get):
        """Test PDF parser download error handling."""
        mock_get.side_effect = Exception("Download failed")

        result = parse_pdf("https://example.com/test.pdf")

        assert result["success"] is False
        assert "error" in result
        assert "Download failed" in result["error"]


class TestToolRegistry:
    """Test tool registry and definitions."""

    def test_tool_registry_contains_all_tools(self):
        """Test that tool registry contains all expected tools."""
        assert "web_search" in TOOL_REGISTRY
        assert "fetch_url" in TOOL_REGISTRY
        assert "parse_pdf" in TOOL_REGISTRY

    def test_tool_definitions_has_all_tools(self):
        """Test that tool definitions includes all tools."""
        assert len(TOOL_DEFINITIONS) == 3

        tool_names = [tool["function"]["name"] for tool in TOOL_DEFINITIONS]
        assert "web_search" in tool_names
        assert "fetch_url" in tool_names
        assert "parse_pdf" in tool_names

    def test_tool_registry_functions_callable(self):
        """Test that all tools in registry are callable."""
        for name, func in TOOL_REGISTRY.items():
            assert callable(func), f"Tool {name} is not callable"

    def test_tool_definitions_valid_structure(self):
        """Test that all tool definitions have valid structure."""
        for tool_def in TOOL_DEFINITIONS:
            assert "type" in tool_def
            assert tool_def["type"] == "function"
            assert "function" in tool_def
            assert "name" in tool_def["function"]
            assert "description" in tool_def["function"]
            assert "parameters" in tool_def["function"]
            assert "type" in tool_def["function"]["parameters"]
            assert "properties" in tool_def["function"]["parameters"]
            assert "required" in tool_def["function"]["parameters"]
