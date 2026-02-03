"""Initialize Adam's database and workspace."""

import click
from pathlib import Path


@click.command()
@click.option('--db-path', default='db/adam.db', help='Path to the database file')
def main(db_path: str):
    """Initialize Adam's database with the schema."""
    from adam_tools.core.db import init_db
    db = Path(db_path)
    db.parent.mkdir(parents=True, exist_ok=True)
    init_db(db)
    click.echo(f"✓ Database initialized at {db}")


if __name__ == '__main__':
    main()
