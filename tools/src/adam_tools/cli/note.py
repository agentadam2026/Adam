"""Create or update reading notes for a source."""

import click
import sys
from datetime import date


@click.command()
@click.argument('source_slug')
@click.option('--append', '-a', is_flag=True, help='Append to existing note')
def main(source_slug: str, append: bool):
    """Create or update reading notes for a source. Reads body from stdin."""
    from adam_tools.core.db import get_connection

    conn = get_connection()

    # Verify source exists
    source = conn.execute("SELECT id, title, author FROM sources WHERE slug = ?",
                          (source_slug,)).fetchone()
    if not source:
        click.echo(f"✗ Source '{source_slug}' not found.", err=True)
        # Show available sources
        sources = conn.execute("SELECT slug, title FROM sources ORDER BY slug").fetchall()
        if sources:
            click.echo("\nAvailable sources:")
            for s in sources:
                click.echo(f"  {s['slug']} — {s['title']}")
        raise SystemExit(1)

    d = date.today().isoformat()

    click.echo(f"Enter reading notes for {source['author']}, {source['title']} (Ctrl+D to finish):")
    body = sys.stdin.read().strip()

    if not body:
        click.echo("✗ Empty input, nothing saved.", err=True)
        raise SystemExit(1)

    # Check for existing note for this source
    existing = conn.execute(
        "SELECT id, body FROM reading_notes WHERE source_id = ? ORDER BY date DESC LIMIT 1",
        (source['id'],)
    ).fetchone()

    if existing and append:
        new_body = existing['body'] + '\n\n' + body
        conn.execute(
            "UPDATE reading_notes SET body = ?, updated_at = datetime('now') WHERE id = ?",
            (new_body, existing['id']),
        )
        action = "appended to"
    else:
        conn.execute(
            "INSERT INTO reading_notes (source_id, date, body) VALUES (?, ?, ?)",
            (source['id'], d, body),
        )
        action = "created"

    conn.commit()
    conn.close()
    click.echo(f"✓ Reading note {action} for {source['title']}")


if __name__ == '__main__':
    main()
