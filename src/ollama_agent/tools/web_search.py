"""Web search tool using DuckDuckGo."""

from typing import Any, Dict
from ddgs import DDGS


def web_search(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Search the web for information.

    Uses DuckDuckGo search API to find relevant web pages for the research query.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default 10)

    Returns:
        Dictionary with search results:
        {
            "results": [
                {
                    "title": "...",
                    "url": "...",
                    "snippet": "...",
                    "source": "..."
                }
            ],
            "query": "original query",
            "count": 10
        }
    """
    try:
        # Perform search using DuckDuckGo
        with DDGS() as ddgs:
            results_list = list(ddgs.text(query, max_results=max_results))

        # Format results
        formatted_results = []
        for result in results_list:
            formatted_results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", ""),
                "source": result.get("href", "").split('/')[2] if result.get("href") else ""
            })

        return {
            "results": formatted_results,
            "query": query,
            "count": len(formatted_results)
        }

    except Exception as e:
        return {
            "results": [],
            "query": query,
            "count": 0,
            "error": str(e)
        }


def get_tool_definition() -> Dict:
    """Return OpenAI-compatible tool definition for web_search.

    Returns:
        Tool definition dictionary
    """
    return {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information on a topic using DuckDuckGo",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        }
    }
