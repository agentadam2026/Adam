"""Create, build, and manage trails."""

import click
import sys
from datetime import date


@click.group()
def main():
    """Manage trails — sequences of connected passages across works."""
    pass


@main.command()
@click.argument('slug')
@click.argument('title')
@click.option('--subtitle', '-s', default=None)
def create(slug: str, title: str, subtitle: str | None):
    """Create a new trail."""
    from adam_tools.core.db import get_connection

    conn = get_connection()

    existing = conn.execute("SELECT id FROM trails WHERE slug = ?", (slug,)).fetchone()
    if existing:
        click.echo(f"✗ Trail '{slug}' already exists.", err=True)
        raise SystemExit(1)

    d = date.today().isoformat()
    conn.execute(
        "INSERT INTO trails (slug, title, subtitle, date) VALUES (?, ?, ?, ?)",
        (slug, title, subtitle, d),
    )
    conn.commit()
    conn.close()
    click.echo(f"✓ Trail created: {title} (slug: {slug})")


@main.command('set-intro')
@click.argument('slug')
def set_intro(slug: str):
    """Set the introduction for a trail. Reads from stdin."""
    from adam_tools.core.db import get_connection

    conn = get_connection()
    trail = conn.execute("SELECT id FROM trails WHERE slug = ?", (slug,)).fetchone()
    if not trail:
        click.echo(f"✗ Trail '{slug}' not found.", err=True)
        raise SystemExit(1)

    click.echo(f"Enter introduction for '{slug}' (Ctrl+D to finish):")
    text = sys.stdin.read().strip()

    conn.execute("UPDATE trails SET introduction = ?, updated_at = datetime('now') WHERE id = ?",
                 (text, trail['id']))
    conn.commit()
    conn.close()
    click.echo(f"✓ Introduction set for '{slug}'")


@main.command('set-conclusion')
@click.argument('slug')
def set_conclusion(slug: str):
    """Set the conclusion for a trail. Reads from stdin."""
    from adam_tools.core.db import get_connection

    conn = get_connection()
    trail = conn.execute("SELECT id FROM trails WHERE slug = ?", (slug,)).fetchone()
    if not trail:
        click.echo(f"✗ Trail '{slug}' not found.", err=True)
        raise SystemExit(1)

    click.echo(f"Enter conclusion for '{slug}' (Ctrl+D to finish):")
    text = sys.stdin.read().strip()

    conn.execute("UPDATE trails SET conclusion = ?, updated_at = datetime('now') WHERE id = ?",
                 (text, trail['id']))
    conn.commit()
    conn.close()
    click.echo(f"✓ Conclusion set for '{slug}'")


@main.command('add-excerpt')
@click.argument('trail_slug')
@click.argument('chunk_id', type=int)
@click.option('--excerpt', '-e', default=None, help='Specific excerpt text (subset of chunk). If omitted, uses full chunk.')
@click.option('--commentary', '-c', default=None, help='Adam\'s commentary on this excerpt')
def add_excerpt(trail_slug: str, chunk_id: int, excerpt: str | None, commentary: str | None):
    """Add an excerpt from a chunk to a trail."""
    from adam_tools.core.db import get_connection

    conn = get_connection()

    trail = conn.execute("SELECT id FROM trails WHERE slug = ?", (trail_slug,)).fetchone()
    if not trail:
        click.echo(f"✗ Trail '{trail_slug}' not found.", err=True)
        raise SystemExit(1)

    chunk = conn.execute("SELECT id, text, source_id FROM chunks WHERE id = ?", (chunk_id,)).fetchone()
    if not chunk:
        click.echo(f"✗ Chunk {chunk_id} not found.", err=True)
        raise SystemExit(1)

    # Get next position
    pos = conn.execute(
        "SELECT COALESCE(MAX(position), -1) + 1 as next_pos FROM trail_excerpts WHERE trail_id = ?",
        (trail['id'],)
    ).fetchone()['next_pos']

    excerpt_text = excerpt or chunk['text']

    # If no commentary provided, read from stdin
    if commentary is None:
        click.echo("Enter commentary for this excerpt (Ctrl+D to finish, empty to skip):")
        commentary = sys.stdin.read().strip() or None

    conn.execute(
        """INSERT INTO trail_excerpts (trail_id, chunk_id, source_id, position, excerpt_text, commentary)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (trail['id'], chunk_id, chunk['source_id'], pos, excerpt_text, commentary),
    )
    conn.commit()
    conn.close()
    click.echo(f"✓ Excerpt added to '{trail_slug}' at position {pos + 1}")


@main.command()
@click.argument('slug')
def publish(slug: str):
    """Mark a trail as published."""
    from adam_tools.core.db import get_connection

    conn = get_connection()
    result = conn.execute(
        "UPDATE trails SET status = 'published', updated_at = datetime('now') WHERE slug = ?",
        (slug,),
    )
    if result.rowcount == 0:
        click.echo(f"✗ Trail '{slug}' not found.", err=True)
        raise SystemExit(1)

    conn.commit()
    conn.close()
    click.echo(f"✓ Trail '{slug}' published")


@main.command('show')
@click.argument('slug')
def show(slug: str):
    """Display a trail with all its excerpts."""
    from adam_tools.core.db import get_connection

    conn = get_connection()

    trail = conn.execute("SELECT * FROM trails WHERE slug = ?", (slug,)).fetchone()
    if not trail:
        click.echo(f"✗ Trail '{slug}' not found.", err=True)
        raise SystemExit(1)

    excerpts = conn.execute("""
        SELECT te.*, s.title, s.author, s.year
        FROM trail_excerpts te
        JOIN sources s ON s.id = te.source_id
        WHERE te.trail_id = ?
        ORDER BY te.position
    """, (trail['id'],)).fetchall()

    click.echo(f"\n{'═' * 60}")
    click.echo(f"  {trail['title']}")
    if trail['subtitle']:
        click.echo(f"  {trail['subtitle']}")
    click.echo(f"  {trail['date']} · {trail['status']}")
    click.echo(f"{'═' * 60}")

    if trail['introduction']:
        click.echo(f"\n{trail['introduction']}")

    for ex in excerpts:
        click.echo(f"\n{'─' * 60}")
        click.echo(f"  {ex['author']}, {ex['title']}", nl=False)
        if ex['year']:
            click.echo(f" ({ex['year']})", nl=False)
        click.echo()
        click.echo(f"{'─' * 60}")
        click.echo()
        # Indent excerpt as blockquote
        for line in ex['excerpt_text'].split('\n'):
            click.echo(f"  > {line}")
        if ex['commentary']:
            click.echo()
            click.echo(f"  {ex['commentary']}")

    if trail['conclusion']:
        click.echo(f"\n{'─' * 60}")
        click.echo(f"\n{trail['conclusion']}")

    click.echo(f"\n{'═' * 60}\n")
    conn.close()


@main.command('list')
@click.option('--status', '-s', default=None, help='Filter by status (draft/published)')
def list_trails(status: str | None):
    """List all trails."""
    from adam_tools.core.db import get_connection

    conn = get_connection()

    if status:
        trails = conn.execute(
            "SELECT slug, title, subtitle, date, status FROM trails WHERE status = ? ORDER BY date DESC",
            (status,),
        ).fetchall()
    else:
        trails = conn.execute(
            "SELECT slug, title, subtitle, date, status FROM trails ORDER BY date DESC"
        ).fetchall()

    if not trails:
        click.echo("No trails found.")
        return

    for t in trails:
        icon = '✓' if t['status'] == 'published' else '○'
        click.echo(f"  {icon} [{t['slug']}] {t['title']}")
        if t['subtitle']:
            click.echo(f"    {t['subtitle']}")
        click.echo(f"    {t['date']} · {t['status']}")

    conn.close()


if __name__ == '__main__':
    main()
