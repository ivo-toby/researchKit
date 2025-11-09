"""Research tools for the Ollama agent."""

from .web_search import web_search, get_tool_definition as web_search_def
from .url_fetch import fetch_url, get_tool_definition as url_fetch_def
from .pdf_parser import parse_pdf, get_tool_definition as pdf_parser_def

# Tool registry maps tool names to their implementations
TOOL_REGISTRY = {
    "web_search": web_search,
    "fetch_url": fetch_url,
    "parse_pdf": parse_pdf,
}

# Tool definitions for Ollama API
TOOL_DEFINITIONS = [
    web_search_def(),
    url_fetch_def(),
    pdf_parser_def(),
]

__all__ = [
    "TOOL_REGISTRY",
    "TOOL_DEFINITIONS",
    "web_search",
    "fetch_url",
    "parse_pdf",
]
