"""Create and manage essays."""

import click
import sys
from datetime import date


@click.group()
def main():
    """Manage essays."""
    pass


@main.command()
@click.argument('slug')
@click.argument('title')
@click.option('--subtitle', '-s', default=None)
def create(slug: str, title: str, subtitle: str | None):
    """Create a new essay. Reads body from stdin."""
    from adam_tools.core.db import get_connection

    conn = get_connection()

    existing = conn.execute("SELECT id FROM essays WHERE slug = ?", (slug,)).fetchone()
    if existing:
        click.echo(f"ERROR: Essay '{slug}' already exists.", err=True)
        raise SystemExit(1)

    d = date.today().isoformat()
    click.echo(f"Enter essay body (Ctrl+D to finish):")
    body = sys.stdin.read().strip()

    if not body:
        click.echo("ERROR: Empty input, nothing saved.", err=True)
        raise SystemExit(1)

    conn.execute(
        "INSERT INTO essays (slug, title, subtitle, date, body) VALUES (?, ?, ?, ?, ?)",
        (slug, title, subtitle, d, body),
    )
    conn.commit()
    conn.close()
    click.echo(f"OK: Essay created: {title} (slug: {slug})")


@main.command()
@click.argument('slug')
def update(slug: str):
    """Update an essay's body. Reads new body from stdin."""
    from adam_tools.core.db import get_connection

    conn = get_connection()

    existing = conn.execute("SELECT id, title FROM essays WHERE slug = ?", (slug,)).fetchone()
    if not existing:
        click.echo(f"ERROR: Essay '{slug}' not found.", err=True)
        raise SystemExit(1)

    click.echo(f"Enter updated body for '{existing['title']}' (Ctrl+D to finish):")
    body = sys.stdin.read().strip()

    conn.execute("UPDATE essays SET body = ?, updated_at = datetime('now') WHERE id = ?",
                 (body, existing['id']))
    conn.commit()
    conn.close()
    click.echo(f"OK: Essay '{slug}' updated")


@main.command()
@click.argument('slug')
def publish(slug: str):
    """Mark an essay as published."""
    from adam_tools.core.db import get_connection

    conn = get_connection()
    result = conn.execute(
        "UPDATE essays SET status = 'published', updated_at = datetime('now') WHERE slug = ?",
        (slug,),
    )
    if result.rowcount == 0:
        click.echo(f"ERROR: Essay '{slug}' not found.", err=True)
        raise SystemExit(1)
    conn.commit()
    conn.close()
    click.echo(f"OK: Essay '{slug}' published")


@main.command('show')
@click.argument('slug')
def show(slug: str):
    """Display an essay."""
    from adam_tools.core.db import get_connection

    conn = get_connection()
    essay = conn.execute("SELECT * FROM essays WHERE slug = ?", (slug,)).fetchone()
    if not essay:
        click.echo(f"ERROR: Essay '{slug}' not found.", err=True)
        raise SystemExit(1)

    click.echo(f"\n{'═' * 60}")
    click.echo(f"  {essay['title']}")
    if essay['subtitle']:
        click.echo(f"  {essay['subtitle']}")
    click.echo(f"  {essay['date']} · {essay['status']}")
    click.echo(f"{'═' * 60}\n")
    click.echo(essay['body'])
    click.echo(f"\n{'═' * 60}\n")
    conn.close()


@main.command('list')
@click.option('--status', '-s', default=None)
def list_essays(status: str | None):
    """List all essays."""
    from adam_tools.core.db import get_connection

    conn = get_connection()
    if status:
        essays = conn.execute(
            "SELECT slug, title, date, status FROM essays WHERE status = ? ORDER BY date DESC",
            (status,),
        ).fetchall()
    else:
        essays = conn.execute(
            "SELECT slug, title, date, status FROM essays ORDER BY date DESC"
        ).fetchall()

    if not essays:
        click.echo("No essays found.")
        return

    for e in essays:
        icon = 'OK:' if e['status'] == 'published' else '○'
        click.echo(f"  {icon} [{e['slug']}] {e['title']} · {e['date']}")
    conn.close()


if __name__ == '__main__':
    main()
