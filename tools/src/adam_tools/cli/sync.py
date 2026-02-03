"""Sync local SQLite database to Turso."""

import click


@click.command()
@click.option('--url', envvar='TURSO_DATABASE_URL', help='Turso database URL')
@click.option('--token', envvar='TURSO_AUTH_TOKEN', help='Turso auth token')
def main(url: str | None, token: str | None):
    """Sync the local database to Turso.

    Set TURSO_DATABASE_URL and TURSO_AUTH_TOKEN environment variables,
    or pass --url and --token.
    """
    if not url or not token:
        click.echo("✗ Turso credentials not configured.", err=True)
        click.echo("  Set TURSO_DATABASE_URL and TURSO_AUTH_TOKEN env vars,", err=True)
        click.echo("  or pass --url and --token.", err=True)
        raise SystemExit(1)

    # TODO: Implement sync
    # Options:
    # 1. Turso embedded replicas (local primary, cloud replica)
    #    - Use libsql-experimental Python client
    #    - Automatic sync on write
    # 2. Full database upload
    #    - Export local db, upload to Turso
    #    - Simpler but slower for large dbs
    # 3. Change-based sync
    #    - Track changes since last sync, replay to Turso
    #    - Most efficient but most complex

    click.echo("⚠ Turso sync not yet implemented.")
    click.echo("  This will push your local database to Turso for the website.")
    click.echo(f"  Target: {url}")


if __name__ == '__main__':
    main()
