"""Semantic search across Adam's corpus."""

import click
import struct


@click.command()
@click.argument('query')
@click.option('--limit', '-n', default=10, help='Number of results')
@click.option('--source', '-s', default=None, help='Filter by source slug')
@click.option('--model', default='BAAI/bge-base-en-v1.5', help='Embedding model')
@click.option('--fts', is_flag=True, help='Use full-text search instead of semantic')
def main(query: str, limit: int, source: str, model: str, fts: bool):
    """Search for passages across all indexed texts.

    By default uses semantic (embedding) search. Use --fts for keyword search.
    """
    from adam_tools.core.db import get_connection

    conn = get_connection()

    if fts:
        _fulltext_search(conn, query, limit, source)
        return

    # Check if we have embeddings
    has_embeddings = conn.execute(
        "SELECT COUNT(*) as n FROM chunks WHERE embedding IS NOT NULL"
    ).fetchone()['n']

    if has_embeddings == 0:
        click.echo("No embeddings found. Falling back to full-text search.", err=True)
        _fulltext_search(conn, query, limit, source)
        return

    # Embed the query
    from adam_tools.core.embeddings import embed_text
    query_embedding = embed_text(query, model_name=model)

    # Brute-force cosine similarity search
    # (For libSQL/Turso, this would use vector_top_k with DiskANN index)
    # For standard SQLite, we compute distances in Python
    query_vec = query_embedding

    if source:
        rows = conn.execute("""
            SELECT c.id, c.text, c.chapter, c.word_count, c.position, c.embedding,
                   s.title, s.author, s.slug, s.year
            FROM chunks c
            JOIN sources s ON s.id = c.source_id
            WHERE c.embedding IS NOT NULL AND s.slug = ?
        """, (source,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT c.id, c.text, c.chapter, c.word_count, c.position, c.embedding,
                   s.title, s.author, s.slug, s.year
            FROM chunks c
            JOIN sources s ON s.id = c.source_id
            WHERE c.embedding IS NOT NULL
        """).fetchall()

    if not rows:
        click.echo("No results found.")
        return

    # Compute cosine similarities
    import math

    def cosine_similarity(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0
        return dot / (norm_a * norm_b)

    results = []
    for row in rows:
        emb_bytes = row['embedding']
        n_floats = len(emb_bytes) // 4
        emb = list(struct.unpack(f'{n_floats}f', emb_bytes))
        sim = cosine_similarity(query_vec, emb)
        results.append((sim, row))

    results.sort(key=lambda x: x[0], reverse=True)
    results = results[:limit]

    click.echo(f"\n{'─' * 60}")
    click.echo(f"Search: \"{query}\" ({len(results)} results)")
    click.echo(f"{'─' * 60}\n")

    for i, (sim, row) in enumerate(results, 1):
        preview = row['text'][:300].replace('\n', ' ')
        if len(row['text']) > 300:
            preview += '...'

        click.echo(f"[{i}] chunk:{row['id']} (sim: {sim:.3f})")
        click.echo(f"    {row['author']}, {row['title']}", nl=False)
        if row['year']:
            click.echo(f" ({row['year']})", nl=False)
        click.echo()
        if row['chapter']:
            click.echo(f"    {row['chapter']}")
        click.echo(f"    {preview}")
        click.echo()

    conn.close()


def _fulltext_search(conn, query: str, limit: int, source: str | None):
    """Fallback full-text search using FTS5."""
    if source:
        results = conn.execute("""
            SELECT c.id, c.text, c.chapter, c.word_count, c.position,
                   s.title, s.author, s.slug, s.year
            FROM chunks_fts fts
            JOIN chunks c ON c.id = fts.rowid
            JOIN sources s ON s.id = c.source_id
            WHERE chunks_fts MATCH ?
              AND s.slug = ?
            LIMIT ?
        """, (query, source, limit)).fetchall()
    else:
        results = conn.execute("""
            SELECT c.id, c.text, c.chapter, c.word_count, c.position,
                   s.title, s.author, s.slug, s.year
            FROM chunks_fts fts
            JOIN chunks c ON c.id = fts.rowid
            JOIN sources s ON s.id = c.source_id
            WHERE chunks_fts MATCH ?
            LIMIT ?
        """, (query, limit)).fetchall()

    if not results:
        click.echo("No results found.")
        return

    click.echo(f"\n{'─' * 60}")
    click.echo(f"Full-text search: \"{query}\" ({len(results)} results)")
    click.echo(f"{'─' * 60}\n")

    for i, row in enumerate(results, 1):
        preview = row['text'][:300].replace('\n', ' ')
        if len(row['text']) > 300:
            preview += '...'
        click.echo(f"[{i}] chunk:{row['id']}")
        click.echo(f"    {row['author']}, {row['title']}", nl=False)
        if row['year']:
            click.echo(f" ({row['year']})", nl=False)
        click.echo()
        if row['chapter']:
            click.echo(f"    {row['chapter']}")
        click.echo(f"    {preview}")
        click.echo()


if __name__ == '__main__':
    main()
