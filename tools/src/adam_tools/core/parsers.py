"""Text extraction from various formats: plain text, EPUB, PDF."""

from pathlib import Path
from dataclasses import dataclass


@dataclass
class ParsedSource:
    """Result of parsing a source text."""
    title: str
    author: str
    text: str
    format: str  # "txt", "epub", "pdf"
    metadata: dict  # any additional metadata from the file


def parse_file(path: Path) -> ParsedSource:
    """Parse a file and extract clean text. Dispatches by extension."""
    suffix = path.suffix.lower()
    if suffix in ('.txt', '.md'):
        return parse_plaintext(path)
    elif suffix == '.epub':
        return parse_epub(path)
    elif suffix == '.pdf':
        return parse_pdf(path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def parse_plaintext(path: Path) -> ParsedSource:
    """Parse a plain text file (e.g., from Project Gutenberg)."""
    from .chunker import strip_gutenberg_boilerplate

    text = path.read_text(encoding='utf-8', errors='replace')

    # Try to extract title and author from Gutenberg header
    title = path.stem.replace('-', ' ').replace('_', ' ').title()
    author = "Unknown"

    lines = text[:3000].split('\n')
    for line in lines:
        line = line.strip()
        if line.lower().startswith('title:'):
            title = line.split(':', 1)[1].strip()
        elif line.lower().startswith('author:'):
            author = line.split(':', 1)[1].strip()

    # Strip boilerplate
    clean_text = strip_gutenberg_boilerplate(text)

    return ParsedSource(
        title=title,
        author=author,
        text=clean_text,
        format="txt",
        metadata={},
    )


def parse_epub(path: Path) -> ParsedSource:
    """Parse an EPUB file and extract clean text."""
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup

    book = epub.read_epub(str(path))

    # Extract metadata
    title = "Unknown"
    author = "Unknown"
    titles = book.get_metadata('DC', 'title')
    if titles:
        title = titles[0][0]
    creators = book.get_metadata('DC', 'creator')
    if creators:
        author = creators[0][0]

    # Extract text from all content documents
    chapters = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), 'html.parser')
        text = soup.get_text(separator='\n\n')
        text = text.strip()
        if text:
            chapters.append(text)

    full_text = '\n\n'.join(chapters)

    return ParsedSource(
        title=title,
        author=author,
        text=full_text,
        format="epub",
        metadata={},
    )


def parse_pdf(path: Path) -> ParsedSource:
    """Parse a PDF file and extract clean text."""
    import fitz  # PyMuPDF

    doc = fitz.open(str(path))

    # Extract metadata
    metadata = doc.metadata or {}
    title = metadata.get('title', '') or path.stem.replace('-', ' ').replace('_', ' ').title()
    author = metadata.get('author', '') or "Unknown"

    # Extract text from all pages
    pages = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            pages.append(text.strip())

    full_text = '\n\n'.join(pages)
    doc.close()

    return ParsedSource(
        title=title,
        author=author,
        text=full_text,
        format="pdf",
        metadata=metadata,
    )
