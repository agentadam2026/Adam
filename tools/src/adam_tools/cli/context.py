"""Read a chunk with surrounding context."""

import click


@click.command()
@click.argument('chunk_id', type=int)
@click.option('--window', '-w', default=2, help='Number of chunks before and after')
def main(chunk_id: int, window: int):
    """Read a chunk with surrounding context (neighboring chunks)."""
    from adam_tools.core.db import get_connection

    conn = get_connection()

    # Get the target chunk
    target = conn.execute("""
        SELECT c.*, s.title, s.author, s.year
        FROM chunks c JOIN sources s ON s.id = c.source_id
        WHERE c.id = ?
    """, (chunk_id,)).fetchone()

    if not target:
        click.echo(f"ERROR: Chunk {chunk_id} not found.", err=True)
        raise SystemExit(1)

    # Get surrounding chunks from the same source
    chunks = conn.execute("""
        SELECT c.id, c.text, c.chapter, c.position, c.word_count
        FROM chunks c
        WHERE c.source_id = ?
          AND c.position BETWEEN ? AND ?
        ORDER BY c.position
    """, (target['source_id'],
          target['position'] - window,
          target['position'] + window)).fetchall()

    click.echo(f"{'═' * 60}")
    click.echo(f"{target['author']}, {target['title']}", nl=False)
    if target['year']:
        click.echo(f" ({target['year']})", nl=False)
    click.echo()
    click.echo(f"Context: chunks {chunks[0]['position'] + 1}–{chunks[-1]['position'] + 1}")
    click.echo(f"{'═' * 60}")

    for chunk in chunks:
        is_target = chunk['id'] == chunk_id
        marker = " ◀" if is_target else ""

        click.echo()
        if chunk['chapter']:
            click.echo(f"[{chunk['chapter']}]")
        click.echo(f"── chunk:{chunk['id']} · pos:{chunk['position'] + 1} · {chunk['word_count']}w{marker} ──")
        click.echo()

        if is_target:
            # Highlight the target chunk
            click.echo(click.style(chunk['text'], bold=True))
        else:
            click.echo(chunk['text'])

    click.echo()
    click.echo(f"{'═' * 60}")
    conn.close()


if __name__ == '__main__':
    main()
