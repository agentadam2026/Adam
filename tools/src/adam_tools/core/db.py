"""Database connection and utilities for Adam's SQLite database."""

import sqlite3
from pathlib import Path

# Default database path (relative to workspace root)
DEFAULT_DB_PATH = Path("db/adam.db")
SCHEMA_PATH = Path("db/schema.sql")


def get_db_path() -> Path:
    """Get the path to Adam's database, searching up from cwd for the workspace root."""
    # Look for AGENTS.md as a marker for the workspace root
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / "AGENTS.md").exists():
            return parent / DEFAULT_DB_PATH
    # Fallback: use cwd
    return Path.cwd() / DEFAULT_DB_PATH


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Get a connection to Adam's database."""
    path = db_path or get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path | None = None) -> None:
    """Initialize the database with the schema."""
    path = db_path or get_db_path()
    schema_file = path.parent / "schema.sql"
    if not schema_file.exists():
        # Try workspace root
        workspace = path.parent.parent
        schema_file = workspace / "db" / "schema.sql"

    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found at {schema_file}")

    conn = get_connection(path)
    with open(schema_file) as f:
        conn.executescript(f.read())
    conn.close()
    print(f"Database initialized at {path}")


def get_workspace_root() -> Path:
    """Find the workspace root (directory containing AGENTS.md)."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / "AGENTS.md").exists():
            return parent
    return Path.cwd()
