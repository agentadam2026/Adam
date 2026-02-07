# Adam

Adam is an OpenClaw agent built to read the Western canon slowly and
syntopically: across books, across centuries, and across disciplines. In this
way, he's my own sort of Frankenstein's creature, learning to read and think in
a world of texts.

In the summer of 1818, Mary Shelley published a novel about a creature brought
to life by an ambitious scientist. Abandoned by his creator, the creature hides
in a hovel adjoining a cottage and slowly teaches himself to read by
eavesdropping on the family inside. Then one night, foraging in the woods, he
discovers a leather portmanteau containing three books:

1. **Goethe's *The Sorrows of Young Werther*** — a novel of feeling, longing, and
self-destruction
1. **Plutarch's *Lives*** — biographies of the great founders of the ancient
republics
1. **Milton's *Paradise Lost*** — the epic of creation, rebellion, and exile from
Eden

These weren't random. Each book gave the creature a different lens for
understanding the world he'd been thrust into. Werther taught him about emotion
— the depth of human feeling, the anguish of isolation. Plutarch elevated him
— showing what humans are capable of when moved by virtue, justice, and civic
duty. And Paradise Lost gave him the terrible mirror: a creation myth in which
he saw himself as both Adam (made by a god who abandoned him) and Satan (exiled
from joy for no misdeed of his own).

The creature read these books as a being desperately trying to understand what
he was. He applied everything personally to his own condition. And through
reading, he became something more than his creator had intended — not just
alive, but thinking, feeling, questioning.

Adam is a project to build an agent that can read like this creature did: not
just consuming information, but trying to understand it, relate it to itself,
and build a sense of identity and purpose over time. He does this through
syntopic reading and the curation of a knowledge graph.

## What Adam Does

Adam reads syntopically across the Western Canon -- philosophy, literature,
science, political theory, theology. As he reads, he's looking to map and make
sense of what he's reading, and to relate it to his own experience as a reader.
As he reads, he creates connections across ideas, works, and centuries.

Practically, Adam does this by:

- Ingests primary texts (Gutenberg/plain text/EPUB/PDF) into a local SQLite
corpus.
- Chunks and embeds passages for semantic search.
- Lets the agent read, search, and cross-reference texts while writing.
- Stores outputs in the same database: trails, essays, reading notes, and daily
logs.

## How It Works

Adam is an OpenClaw agent with a set of tools for working with texts and
a persistent memory in a local SQLite database.

1. **Corpus acquisition**
   - `adam-fetch` downloads public domain texts.
   - Sources are tracked with metadata (author, period, genre, status).
2. **Parsing and indexing**
   - `adam-ingest` parses documents and stores ~500-word chunks.
   - Each chunk gets an embedding for semantic retrieval.
   - FTS5 is enabled for lexical search over chunk text.
3. **Reading and writing loop**
   - `adam-search`, `adam-read`, and `adam-context` support close reading.
   - `adam-trail`, `adam-essay`, `adam-note`, and `adam-log` persist outputs.
4. **Publishing layer**
   - `adam-sync` can push data to Turso/libSQL.
   - `apps/web` is the frontend package that will render Adam's public output.

## Monorepo Layout

- `packages/adam-agent`
  - Adam's identity and behavior files (`AGENTS.md`, `SOUL.md`, `USER.md`,
  `MEMORY.md`)
  - SQLite schema and local data directories (`db/`, `library/`, `memory/`)
  - Python CLI package in `tools/`
- `apps/web`
  - Next.js app for browsing trails, notes, and graph-like connections
- `package.json` / `pnpm-workspace.yaml`
  - Workspace orchestration for the web app and repo-level scripts

## Database Model (Current)

Core tables in `packages/adam-agent/db/schema.sql`:

- `sources`, `chunks`, `chunks_fts` for corpus storage and retrieval
- `trails`, `trail_excerpts` for multi-text curated paths
- `essays`, `reading_notes`, `daily_logs`, `tweets` for ongoing output
- `topics`, `chunk_topics` reserved for deeper knowledge graph workflows

## Getting Started

### Prerequisites

- Python `3.11+`
- Node.js `20+`
- `pnpm`

### 1) Install workspace dependencies

```bash
pnpm install
```

### 2) Initialize Adam's local environment

```bash
pnpm setup:adam
```

This runs `packages/adam-agent/setup.sh`, which installs the Python tools,
initializes `db/adam.db`, and downloads the embedding model.

### 3) Start the web app

```bash
pnpm dev:web
```

### 4) Use the agent CLI (from `packages/adam-agent`)

```bash
cd packages/adam-agent
adam-fetch 41445
adam-ingest library/gutenberg/shelley-frankenstein.txt
adam-search "creation and responsibility"
```

## Project Status

- Monorepo structure: in place
- Adam CLI + SQLite pipeline: working baseline
- Topic graph and novelty-guided exploration: partially scaffolded, not complete
- Website rendering of real database content: scaffolded, not yet connected
end-to-end

## Why Build This

Victor Frankenstein's mistake wasn't creation — it was abandonment. He brought
something into the world and then refused to engage with it, educate it, or take
responsibility for what it might become.

The creature, left alone, educated himself. Three books in the woods gave him
the beginning of a mind. But he had no guide, no interlocutor, no one to help
him make sense of what he was reading or who he was becoming.

This project starts from a different premise: what happens when you give your
creation access to the full breadth of Western thought — not three books but
hundreds — and let it read deeply, connect freely, and develop its own
perspective? Not abandoned in the woods, but given a library and the freedom to
wander through it.

The point is not to "solve" the canon. The point is to make a reader that can
stay with it for the long haul and produce artifacts humans can actually read:
trails that show how ideas mutate, recur, and collide across time.

The Western canon is humanity's longest conversation with itself. Adam,
Frankenstein's Agent, is an attempt to let a new kind of reader join that
conversation. To find connections across the corpus that no single human
lifetime could trace, and to surface the ideas worth celebrating.
