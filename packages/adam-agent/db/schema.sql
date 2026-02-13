-- Adam's Database Schema
-- SQLite + sqlite-vec
-- Everything lives here: source texts, chunks, embeddings, and all of Adam's output.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-----------------------------------------------------------
-- SOURCE DATA
-----------------------------------------------------------

-- Books and texts in Adam's library
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,         -- url-friendly identifier
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    year INTEGER,                      -- publication/composition year
    period TEXT,                        -- "Ancient Greece", "Medieval", etc.
    genre TEXT,                         -- "Philosophy", "Novel", "Poetry", etc.
    translator TEXT,                    -- if applicable
    gutenberg_id INTEGER,
    source_url TEXT,
    file_path TEXT,                     -- path in library/
    status TEXT DEFAULT 'unread',       -- unread, reading, finished
    date_started TEXT,
    date_finished TEXT,
    notes TEXT,                         -- brief description / why it matters
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_sources_status ON sources(status);
CREATE INDEX IF NOT EXISTS idx_sources_period ON sources(period);
CREATE INDEX IF NOT EXISTS idx_sources_author ON sources(author);

-- Text chunks (~500 words each)
-- NOTE on embeddings:
-- On libSQL/Turso: use F32_BLOB(768) column + DiskANN index (native vector search)
-- On standard SQLite: use sqlite-vec virtual table (see tools for detection)
-- The 'embedding' column is BLOB to be compatible with both approaches.
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    chapter TEXT,                       -- chapter/section name or number
    position INTEGER NOT NULL,          -- order within source
    text TEXT NOT NULL,
    word_count INTEGER,
    embedding BLOB,                     -- vector embedding (F32_BLOB on libSQL, raw bytes on SQLite)
    is_useful BOOLEAN DEFAULT 1,        -- 0 = index, acknowledgements, etc.
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_id);
CREATE INDEX IF NOT EXISTS idx_chunks_position ON chunks(source_id, position);

-- Full-text search on chunks
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    text,
    content='chunks',
    content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
    INSERT INTO chunks_fts(rowid, text) VALUES (new.id, new.text);
END;

CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, text) VALUES ('delete', old.id, old.text);
END;

CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, text) VALUES ('delete', old.id, old.text);
    INSERT INTO chunks_fts(rowid, text) VALUES (new.id, new.text);
END;

-----------------------------------------------------------
-- ADAM'S OUTPUT
-----------------------------------------------------------

-- Trails: sequences of connected passages across works
CREATE TABLE IF NOT EXISTS trails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    subtitle TEXT,
    date TEXT NOT NULL,
    status TEXT DEFAULT 'draft',        -- draft, published
    introduction TEXT,                  -- Adam's intro in his voice
    conclusion TEXT,                    -- Adam's concluding thoughts
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_trails_status ON trails(status);
CREATE INDEX IF NOT EXISTS idx_trails_date ON trails(date);

-- Trail excerpts: ordered passages within a trail
CREATE TABLE IF NOT EXISTS trail_excerpts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trail_id INTEGER NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
    chunk_id INTEGER REFERENCES chunks(id),  -- nullable if excerpt is manually entered
    source_id INTEGER NOT NULL REFERENCES sources(id),
    position INTEGER NOT NULL,          -- order within trail
    excerpt_text TEXT NOT NULL,          -- the specific sentences Adam selected
    commentary TEXT,                    -- Adam's commentary on this excerpt
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_trail_excerpts_trail ON trail_excerpts(trail_id);
CREATE INDEX IF NOT EXISTS idx_trail_excerpts_source ON trail_excerpts(source_id);

-- Essays: longer-form pieces
CREATE TABLE IF NOT EXISTS essays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    subtitle TEXT,
    date TEXT NOT NULL,
    status TEXT DEFAULT 'draft',        -- draft, published
    body TEXT NOT NULL,                  -- full essay in markdown
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_essays_status ON essays(status);
CREATE INDEX IF NOT EXISTS idx_essays_date ON essays(date);

-- Reading notes: per-source personal notes
CREATE TABLE IF NOT EXISTS reading_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    date TEXT NOT NULL,
    body TEXT NOT NULL,                  -- Adam's notes in markdown
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_reading_notes_source ON reading_notes(source_id);
CREATE INDEX IF NOT EXISTS idx_reading_notes_date ON reading_notes(date);

-- Chunk thoughts: Adam's annotations on specific passages as he reads
-- These capture his thinking process, reactions, and connections in real-time
CREATE TABLE IF NOT EXISTS chunk_thoughts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id INTEGER NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    thought_type TEXT NOT NULL,          -- 'reaction', 'question', 'connection', 'insight', 'tension', 'beauty'
    thought TEXT NOT NULL,               -- Adam's thought/annotation in his voice
    connections TEXT,                    -- JSON array of related chunk_ids
    related_topics TEXT,                 -- JSON array of topic labels this connects to
    intensity INTEGER DEFAULT 1,         -- 1-5, how significant this thought felt
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_chunk_thoughts_chunk ON chunk_thoughts(chunk_id);
CREATE INDEX IF NOT EXISTS idx_chunk_thoughts_type ON chunk_thoughts(thought_type);
CREATE INDEX IF NOT EXISTS idx_chunk_thoughts_date ON chunk_thoughts(created_at);

-- Reading sessions: track when Adam reads, for timeline visualization
CREATE TABLE IF NOT EXISTS reading_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    started_at TEXT NOT NULL,
    ended_at TEXT,
    chunks_read INTEGER DEFAULT 0,       -- how many chunks processed this session
    thoughts_recorded INTEGER DEFAULT 0, -- how many chunk_thoughts created
    notes TEXT                           -- session summary
);

CREATE INDEX IF NOT EXISTS idx_reading_sessions_source ON reading_sessions(source_id);
CREATE INDEX IF NOT EXISTS idx_reading_sessions_date ON reading_sessions(started_at);

-- Daily log entries
CREATE TABLE IF NOT EXISTS daily_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT UNIQUE NOT NULL,
    body TEXT NOT NULL,                  -- Adam's journal entry
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Tweets
CREATE TABLE IF NOT EXISTS tweets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    body TEXT NOT NULL,
    trail_id INTEGER REFERENCES trails(id),
    essay_id INTEGER REFERENCES essays(id),
    status TEXT DEFAULT 'draft',        -- draft, posted
    posted_at TEXT,
    tweet_id TEXT,                       -- external tweet ID once posted
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tweets_status ON tweets(status);

-----------------------------------------------------------
-- KNOWLEDGE GRAPH (Future)
-----------------------------------------------------------

-- Topics extracted from chunks
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL,
    parent_id INTEGER REFERENCES topics(id),
    source_count INTEGER DEFAULT 0,
    chunk_count INTEGER DEFAULT 0,
    novelty_score REAL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_topics_parent ON topics(parent_id);

-- Chunk-topic associations
CREATE TABLE IF NOT EXISTS chunk_topics (
    chunk_id INTEGER NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    PRIMARY KEY (chunk_id, topic_id)
);

-----------------------------------------------------------
-- METADATA
-----------------------------------------------------------

-- Key-value store for settings, sync state, etc.
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Track embedding model used (important for consistency)
INSERT OR IGNORE INTO metadata (key, value) VALUES ('embedding_model', '');
INSERT OR IGNORE INTO metadata (key, value) VALUES ('embedding_dimensions', '');
INSERT OR IGNORE INTO metadata (key, value) VALUES ('last_sync', '');
INSERT OR IGNORE INTO metadata (key, value) VALUES ('schema_version', '2');

-----------------------------------------------------------
-- SCHEMA CHANGELOG
-----------------------------------------------------------
-- v2 (2026-02-13): Added chunk_thoughts and reading_sessions tables
--                  for explorable reading / annotation layer
-- v1 (2026-02-02): Initial schema
