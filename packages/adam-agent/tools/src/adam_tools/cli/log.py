"""Create or update daily log entries."""

import click
import sys
from datetime import date


@click.command()
@click.option('--date', '-d', 'log_date', default=None, help='Date (YYYY-MM-DD), defaults to today')
@click.option('--append', '-a', is_flag=True, help='Append to existing entry instead of replacing')
def main(log_date: str | None, append: bool):
    """Create or update a daily log entry. Reads body from stdin."""
    from adam_tools.core.db import get_connection

    d = log_date or date.today().isoformat()
    conn = get_connection()

    click.echo(f"Enter log entry for {d} (Ctrl+D to finish):")
    body = sys.stdin.read().strip()

    if not body:
        click.echo("ERROR: Empty input, nothing saved.", err=True)
        raise SystemExit(1)

    existing = conn.execute("SELECT id, body FROM daily_logs WHERE date = ?", (d,)).fetchone()

    if existing:
        if append:
            new_body = existing['body'] + '\n\n' + body
        else:
            new_body = body
        conn.execute(
            "UPDATE daily_logs SET body = ?, updated_at = datetime('now') WHERE id = ?",
            (new_body, existing['id']),
        )
        action = "appended to" if append else "updated"
    else:
        conn.execute(
            "INSERT INTO daily_logs (date, body) VALUES (?, ?)",
            (d, body),
        )
        action = "created"

    conn.commit()
    conn.close()
    click.echo(f"OK: Log {action} for {d}")


if __name__ == '__main__':
    main()
