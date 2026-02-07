"""Read a specific chunk with its metadata."""

import click


@click.command()
@click.argument('chunk_id', type=int)
def main(chunk_id: int):
    """Read a specific chunk by ID, with source info and context."""
    from adam_tools.core.db import get_connection

    conn = get_connection()
    row = conn.execute("""
        SELECT c.id, c.text, c.chapter, c.word_count, c.position, c.source_id,
               s.title, s.author, s.slug, s.year
        FROM chunks c
        JOIN sources s ON s.id = c.source_id
        WHERE c.id = ?
    """, (chunk_id,)).fetchone()

    if not row:
        click.echo(f"ERROR: Chunk {chunk_id} not found.", err=True)
        raise SystemExit(1)

    # Get total chunks for this source
    total = conn.execute(
        "SELECT COUNT(*) as n FROM chunks WHERE source_id = ?",
        (row['source_id'],)
    ).fetchone()['n']

    click.echo(f"{'═' * 60}")
    click.echo(f"{row['author']}, {row['title']}", nl=False)
    if row['year']:
        click.echo(f" ({row['year']})", nl=False)
    click.echo()
    if row['chapter']:
        click.echo(f"{row['chapter']}")
    click.echo(f"Chunk {row['position'] + 1}/{total} · {row['word_count']} words · id:{row['id']}")
    click.echo(f"{'─' * 60}")
    click.echo()
    click.echo(row['text'])
    click.echo()
    click.echo(f"{'═' * 60}")

    conn.close()


if __name__ == '__main__':
    main()
