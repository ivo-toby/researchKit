"""PDF download and parsing tool."""

from typing import Any, Dict, Optional
from pathlib import Path
import requests
from pypdf import PdfReader
import io


def parse_pdf(url: str, save_path: Optional[str] = None) -> Dict[str, Any]:
    """Download and parse a PDF document.

    Downloads PDF from URL, extracts text content, and optionally
    saves to local file system for reference.

    Args:
        url: URL to PDF document
        save_path: Optional local path to save PDF

    Returns:
        Dictionary with PDF content:
        {
            "url": "...",
            "text": "extracted text content",
            "pages": 42,
            "metadata": {
                "title": "...",
                "author": "...",
                "created": "..."
            },
            "saved_path": "/path/to/file.pdf" or None,
            "word_count": 5678
        }
    """
    try:
        # Download PDF
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; ResearchKit/1.0)'
        }
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()

        # Verify content type
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/pdf' not in content_type:
            return {
                "url": url,
                "text": "",
                "pages": 0,
                "metadata": {},
                "saved_path": None,
                "word_count": 0,
                "error": f"URL does not point to a PDF (Content-Type: {content_type})"
            }

        # Save to file if requested
        saved_path_str = None
        if save_path:
            save_path_obj = Path(save_path)
            save_path_obj.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path_obj, 'wb') as f:
                f.write(response.content)
            saved_path_str = str(save_path_obj.absolute())

        # Parse PDF
        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)

        # Extract metadata
        metadata = {}
        if reader.metadata:
            metadata = {
                "title": reader.metadata.get('/Title', ''),
                "author": reader.metadata.get('/Author', ''),
                "subject": reader.metadata.get('/Subject', ''),
                "creator": reader.metadata.get('/Creator', ''),
                "producer": reader.metadata.get('/Producer', ''),
                "created": str(reader.metadata.get('/CreationDate', '')),
            }

        # Extract text from all pages
        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text())

        full_text = '\n\n'.join(text_parts)
        word_count = len(full_text.split())

        return {
            "url": url,
            "text": full_text,
            "pages": len(reader.pages),
            "metadata": metadata,
            "saved_path": saved_path_str,
            "word_count": word_count
        }

    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "text": "",
            "pages": 0,
            "metadata": {},
            "saved_path": None,
            "word_count": 0,
            "error": f"Download error: {str(e)}"
        }
    except Exception as e:
        return {
            "url": url,
            "text": "",
            "pages": 0,
            "metadata": {},
            "saved_path": None,
            "word_count": 0,
            "error": f"PDF parsing error: {str(e)}"
        }


def get_tool_definition() -> Dict:
    """Return OpenAI-compatible tool definition for parse_pdf.

    Returns:
        Tool definition dictionary
    """
    return {
        "type": "function",
        "function": {
            "name": "parse_pdf",
            "description": "Download and extract text from a PDF document",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to the PDF document"
                    },
                    "save_path": {
                        "type": "string",
                        "description": "Optional path to save the PDF locally"
                    }
                },
                "required": ["url"]
            }
        }
    }
