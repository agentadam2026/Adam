"""Show reading list and progress."""

import click


@click.command()
@click.option('--status', '-s', default=None, help='Filter by status')
@click.option('--period', '-p', default=None, help='Filter by period')
def main(status: str | None, period: str | None):
    """Show the reading list with progress."""
    from adam_tools.core.db import get_connection

    conn = get_connection()

    query = "SELECT * FROM sources WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)
    if period:
        query += " AND period = ?"
        params.append(period)

    query += " ORDER BY year, title"
    sources = conn.execute(query, params).fetchall()

    if not sources:
        click.echo("No sources found.")
        return

    # Group by status
    by_status = {}
    for s in sources:
        by_status.setdefault(s['status'], []).append(s)

    status_order = ['reading', 'finished', 'unread']
    icons = {'reading': '📖', 'finished': '✓', 'unread': '○'}

    click.echo(f"\n{'═' * 50}")
    click.echo(f"  Adam's Library")
    click.echo(f"{'═' * 50}")

    for st in status_order:
        items = by_status.get(st, [])
        if not items:
            continue
        click.echo(f"\n  {icons.get(st, '?')} {st.upper()} ({len(items)})")
        for s in items:
            year = f" ({s['year']})" if s['year'] else ""
            chunk_count = conn.execute(
                "SELECT COUNT(*) as n FROM chunks WHERE source_id = ?", (s['id'],)
            ).fetchone()['n']
            chunks_note = f" · {chunk_count} chunks" if chunk_count > 0 else ""
            click.echo(f"     {s['author']}, {s['title']}{year}{chunks_note}")

    click.echo(f"\n{'═' * 50}\n")
    conn.close()


if __name__ == '__main__':
    main()
