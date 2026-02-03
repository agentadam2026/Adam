"""Corpus overview and statistics."""

import click


@click.command()
def main():
    """Show corpus overview: sources, chunks, output counts."""
    from adam_tools.core.db import get_connection

    conn = get_connection()

    # Sources
    sources = conn.execute("""
        SELECT status, COUNT(*) as n FROM sources GROUP BY status
    """).fetchall()
    total_sources = sum(r['n'] for r in sources)
    status_counts = {r['status']: r['n'] for r in sources}

    # Chunks
    chunk_count = conn.execute("SELECT COUNT(*) as n FROM chunks").fetchone()['n']
    total_words = conn.execute("SELECT COALESCE(SUM(word_count), 0) as n FROM chunks").fetchone()['n']

    # Embeddings
    try:
        embed_count = conn.execute("SELECT COUNT(*) as n FROM chunk_embeddings").fetchone()['n']
    except Exception:
        embed_count = 0

    # Output
    trail_count = conn.execute("SELECT COUNT(*) as n FROM trails").fetchone()['n']
    published_trails = conn.execute("SELECT COUNT(*) as n FROM trails WHERE status = 'published'").fetchone()['n']
    essay_count = conn.execute("SELECT COUNT(*) as n FROM essays").fetchone()['n']
    note_count = conn.execute("SELECT COUNT(*) as n FROM reading_notes").fetchone()['n']
    log_count = conn.execute("SELECT COUNT(*) as n FROM daily_logs").fetchone()['n']
    tweet_count = conn.execute("SELECT COUNT(*) as n FROM tweets").fetchone()['n']

    click.echo(f"\n{'═' * 50}")
    click.echo(f"  Adam's Library — Overview")
    click.echo(f"{'═' * 50}")

    click.echo(f"\n  📚 Sources: {total_sources}")
    for status in ['reading', 'finished', 'unread']:
        if status in status_counts:
            icon = {'reading': '📖', 'finished': '✓', 'unread': '○'}[status]
            click.echo(f"     {icon} {status}: {status_counts[status]}")

    click.echo(f"\n  📄 Chunks: {chunk_count:,}")
    click.echo(f"     Words: {total_words:,}")
    click.echo(f"     Embeddings: {embed_count:,}")

    click.echo(f"\n  ✍️  Output:")
    click.echo(f"     Trails: {trail_count} ({published_trails} published)")
    click.echo(f"     Essays: {essay_count}")
    click.echo(f"     Reading notes: {note_count}")
    click.echo(f"     Daily logs: {log_count}")
    click.echo(f"     Tweets: {tweet_count}")

    # Recent sources
    recent = conn.execute("""
        SELECT title, author, status FROM sources
        ORDER BY updated_at DESC LIMIT 5
    """).fetchall()
    if recent:
        click.echo(f"\n  Recent:")
        for r in recent:
            icon = {'reading': '📖', 'finished': '✓', 'unread': '○'}.get(r['status'], '?')
            click.echo(f"     {icon} {r['author']}, {r['title']}")

    click.echo(f"\n{'═' * 50}\n")
    conn.close()


if __name__ == '__main__':
    main()
