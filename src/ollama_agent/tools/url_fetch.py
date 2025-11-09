"""URL fetching and content extraction tool."""

from typing import Any, Dict
import requests
from bs4 import BeautifulSoup


def fetch_url(url: str, extract_text: bool = True) -> Dict[str, Any]:
    """Fetch and parse content from a URL.

    Downloads web page content and optionally extracts clean text
    (removing HTML tags, scripts, navigation, etc.).

    Args:
        url: URL to fetch
        extract_text: If True, extract clean text from HTML (default True)

    Returns:
        Dictionary with fetched content:
        {
            "url": "...",
            "title": "...",
            "content": "extracted text content",
            "content_type": "text/html",
            "status_code": 200,
            "word_count": 1234
        }
    """
    try:
        # Fetch URL with a reasonable timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; ResearchKit/1.0)'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '').lower()

        # Parse HTML if content is HTML
        if 'text/html' in content_type and extract_text:
            soup = BeautifulSoup(response.content, 'lxml')

            # Extract title
            title = soup.title.string if soup.title else ""

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()

            # Get text content
            text = soup.get_text(separator='\n', strip=True)

            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines()]
            text = '\n'.join(line for line in lines if line)

            word_count = len(text.split())

            return {
                "url": url,
                "title": title.strip() if title else "",
                "content": text,
                "content_type": content_type,
                "status_code": response.status_code,
                "word_count": word_count
            }
        else:
            # Return raw content for non-HTML
            return {
                "url": url,
                "title": "",
                "content": response.text[:10000],  # Limit to first 10000 chars
                "content_type": content_type,
                "status_code": response.status_code,
                "word_count": len(response.text.split())
            }

    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "title": "",
            "content": "",
            "content_type": "",
            "status_code": 0,
            "word_count": 0,
            "error": str(e)
        }
    except Exception as e:
        return {
            "url": url,
            "title": "",
            "content": "",
            "content_type": "",
            "status_code": 0,
            "word_count": 0,
            "error": f"Parsing error: {str(e)}"
        }


def get_tool_definition() -> Dict:
    """Return OpenAI-compatible tool definition for fetch_url.

    Returns:
        Tool definition dictionary
    """
    return {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch and extract text content from a URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch"
                    },
                    "extract_text": {
                        "type": "boolean",
                        "description": "Extract clean text from HTML (default true)",
                        "default": True
                    }
                },
                "required": ["url"]
            }
        }
    }
