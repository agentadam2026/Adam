"""Fetch a text from Project Gutenberg by ID."""

import click
import re
from pathlib import Path


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


@click.command()
@click.argument('gutenberg_id', type=int)
@click.option('--library-dir', default='library/gutenberg', help='Directory to save texts')
def main(gutenberg_id: int, library_dir: str):
    """Fetch a text from Project Gutenberg by ID and register it in the database."""
    import httpx
    from adam_tools.core.db import get_connection

    lib_dir = Path(library_dir)
    lib_dir.mkdir(parents=True, exist_ok=True)

    # Try UTF-8 text first
    url = f"https://www.gutenberg.org/ebooks/{gutenberg_id}.txt.utf-8"
    click.echo(f"Fetching Gutenberg #{gutenberg_id}...")

    try:
        resp = httpx.get(url, follow_redirects=True, timeout=30)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        click.echo(f"ERROR: Failed to fetch: {e}", err=True)
        raise SystemExit(1)

    text = resp.text

    # Extract title and author from Gutenberg header
    title = f"Gutenberg #{gutenberg_id}"
    author = "Unknown"
    for line in text[:3000].split('\n'):
        line = line.strip()
        if line.lower().startswith('title:'):
            title = line.split(':', 1)[1].strip()
        elif line.lower().startswith('author:'):
            author = line.split(':', 1)[1].strip()

    slug = slugify(f"{author.split()[-1] if author != 'Unknown' else 'unknown'}-{title}")

    # Save file
    filename = f"{slug}.txt"
    file_path = lib_dir / filename
    file_path.write_text(text, encoding='utf-8')
    click.echo(f"OK: Saved to {file_path}")

    # Register in database
    conn = get_connection()
    conn.execute(
        """INSERT OR IGNORE INTO sources (slug, title, author, gutenberg_id, source_url, file_path, status)
           VALUES (?, ?, ?, ?, ?, ?, 'unread')""",
        (slug, title, author, gutenberg_id, url, str(file_path)),
    )
    conn.commit()
    conn.close()

    click.echo(f"OK: Registered: {title} by {author} (slug: {slug})")


if __name__ == '__main__':
    main()
