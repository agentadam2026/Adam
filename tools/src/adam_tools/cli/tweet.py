"""Save tweet drafts."""

import click
from datetime import date


@click.command()
@click.argument('text')
@click.option('--trail', '-t', default=None, help='Associated trail slug')
@click.option('--essay', '-e', default=None, help='Associated essay slug')
def main(text: str, trail: str | None, essay: str | None):
    """Save a tweet draft to the database."""
    from adam_tools.core.db import get_connection

    conn = get_connection()
    d = date.today().isoformat()

    trail_id = None
    essay_id = None

    if trail:
        row = conn.execute("SELECT id FROM trails WHERE slug = ?", (trail,)).fetchone()
        if row:
            trail_id = row['id']

    if essay:
        row = conn.execute("SELECT id FROM essays WHERE slug = ?", (essay,)).fetchone()
        if row:
            essay_id = row['id']

    conn.execute(
        "INSERT INTO tweets (date, body, trail_id, essay_id) VALUES (?, ?, ?, ?)",
        (d, text, trail_id, essay_id),
    )
    conn.commit()
    conn.close()
    click.echo(f"✓ Tweet draft saved")


if __name__ == '__main__':
    main()
