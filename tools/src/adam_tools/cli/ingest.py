"""Ingest a text: parse, chunk, embed, and store in the database."""

import click
import struct
from pathlib import Path


@click.command()
@click.argument('source_path')
@click.option('--target-words', default=500, help='Target chunk size in words')
@click.option('--model', default='BAAI/bge-base-en-v1.5', help='Embedding model name')
@click.option('--batch-size', default=32, help='Embedding batch size')
@click.option('--no-embed', is_flag=True, help='Skip embedding (just chunk and store)')
def main(source_path: str, target_words: int, model: str, batch_size: int, no_embed: bool):
    """Ingest a text file: parse → chunk → embed → store."""
    from adam_tools.core.db import get_connection
    from adam_tools.core.parsers import parse_file
    from adam_tools.core.chunker import chunk_text

    path = Path(source_path)
    if not path.exists():
        click.echo(f"✗ File not found: {path}", err=True)
        raise SystemExit(1)

    # Parse
    click.echo(f"Parsing {path.name}...")
    parsed = parse_file(path)
    click.echo(f"  Title: {parsed.title}")
    click.echo(f"  Author: {parsed.author}")
    click.echo(f"  Format: {parsed.format}")
    click.echo(f"  Text length: {len(parsed.text):,} chars")

    # Chunk
    click.echo(f"Chunking (target: {target_words} words)...")
    chunks = chunk_text(parsed.text, target_words=target_words)
    click.echo(f"  {len(chunks)} chunks created")

    # Filter out very small chunks
    useful_chunks = [c for c in chunks if c.word_count >= 30]
    skipped = len(chunks) - len(useful_chunks)
    if skipped:
        click.echo(f"  {skipped} tiny chunks skipped")

    # Embed (unless skipped)
    embeddings = None
    if not no_embed:
        click.echo(f"Embedding with {model}...")
        from adam_tools.core.embeddings import embed_texts, get_dimensions
        texts = [c.text for c in useful_chunks]
        embeddings = embed_texts(texts, model_name=model, batch_size=batch_size)
        dims = get_dimensions(model)
        click.echo(f"  {len(embeddings)} embeddings ({dims}d)")

    # Store in database
    conn = get_connection()

    from adam_tools.cli.fetch import slugify
    slug = slugify(f"{parsed.author.split()[-1]}-{parsed.title}")

    existing = conn.execute("SELECT id FROM sources WHERE slug = ?", (slug,)).fetchone()
    if existing:
        source_id = existing['id']
        click.echo(f"  Source already exists (id: {source_id}), replacing chunks...")
        conn.execute("DELETE FROM chunks WHERE source_id = ?", (source_id,))
        conn.execute("UPDATE sources SET file_path = ?, updated_at = datetime('now') WHERE id = ?",
                     (str(path), source_id))
    else:
        cursor = conn.execute(
            """INSERT INTO sources (slug, title, author, file_path, status)
               VALUES (?, ?, ?, ?, 'unread')""",
            (slug, parsed.title, parsed.author, str(path)),
        )
        source_id = cursor.lastrowid
        click.echo(f"  New source registered (id: {source_id})")

    click.echo("Storing chunks...")
    for i, chunk in enumerate(useful_chunks):
        embedding_blob = None
        if embeddings:
            # Pack as raw float32 bytes (compatible with both sqlite-vec and libSQL F32_BLOB)
            embedding_blob = struct.pack(f'{len(embeddings[i])}f', *embeddings[i])

        conn.execute(
            """INSERT INTO chunks (source_id, chapter, position, text, word_count, embedding)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (source_id, chunk.chapter, chunk.position, chunk.text, chunk.word_count, embedding_blob),
        )
    conn.commit()

    # Update metadata
    if embeddings:
        conn.execute("UPDATE metadata SET value = ?, updated_at = datetime('now') WHERE key = 'embedding_model'",
                     (model,))
        conn.execute("UPDATE metadata SET value = ?, updated_at = datetime('now') WHERE key = 'embedding_dimensions'",
                     (str(dims),))
        conn.commit()

    conn.close()
    click.echo(f"\n✓ Ingested: {parsed.title} by {parsed.author}")
    click.echo(f"  {len(useful_chunks)} chunks, source_id: {source_id}")
    if embeddings:
        click.echo(f"  Embeddings: {dims}d {model}")


if __name__ == '__main__':
    main()
