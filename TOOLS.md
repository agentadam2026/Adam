# TOOLS.md — Adam's Tools

These are your tools for reading, exploring, and writing. They all operate on your SQLite database at `db/adam.db`.

## Setup

First time only: `bash setup.sh` (installs dependencies, initializes database, downloads embedding model).

## Corpus Tools

### adam-fetch — Download a text from Project Gutenberg
```bash
adam-fetch <gutenberg_id>
```
Downloads the text to `library/gutenberg/` and registers it in your database. Check `library/CANON.md` for Gutenberg IDs.

### adam-ingest — Process a text into your database
```bash
adam-ingest <path>
adam-ingest library/gutenberg/shelley-frankenstein.txt
adam-ingest library/other/some-book.epub
adam-ingest library/other/some-paper.pdf
```
Parses the file, splits into ~500-word chunks, embeds them, and stores everything in the database. Supports `.txt`, `.md`, `.epub`, and `.pdf`.

### adam-search — Semantic search across your corpus
```bash
adam-search "the nature of virtue"
adam-search "the nature of virtue" -n 20           # more results
adam-search "creation and responsibility" -s shelley-frankenstein  # filter by source
```
Searches all chunks by semantic similarity to your query. Returns ranked results with source info and text preview.

### adam-read — Read a specific chunk
```bash
adam-read <chunk_id>
```
Displays a chunk with its full text, source info, chapter, and position.

### adam-context — Read a chunk with surrounding context
```bash
adam-context <chunk_id>
adam-context <chunk_id> -w 5    # 5 chunks before and after
```
Shows the target chunk (highlighted) with neighboring chunks for broader context. Default window: 2 chunks each side.

### adam-stats — Corpus overview
```bash
adam-stats
```
Shows: total sources (by status), chunk count, word count, embedding count, output counts (trails, essays, notes, logs, tweets).

### adam-library — Reading list and progress
```bash
adam-library
adam-library -s reading    # only currently reading
adam-library -p "Ancient Greece"  # filter by period
```

## Writing Tools

### adam-log — Daily log
```bash
echo "Today I continued reading..." | adam-log
echo "Additional thoughts..." | adam-log -a        # append to today's entry
echo "Yesterday's reflection..." | adam-log -d 2026-02-01  # specific date
```
Creates or updates your daily log entry. Use `-a` to append rather than replace.

### adam-note — Reading notes
```bash
echo "My notes on this text..." | adam-note shelley-frankenstein
echo "More thoughts..." | adam-note shelley-frankenstein -a  # append
```
Creates or updates reading notes for a specific source (by slug).

### adam-trail — Manage trails
```bash
adam-trail create <slug> "<title>" -s "<subtitle>"   # create a new trail
adam-trail set-intro <slug>                           # set introduction (stdin)
adam-trail add-excerpt <slug> <chunk_id>              # add a passage
adam-trail add-excerpt <slug> <chunk_id> -e "specific sentences" -c "commentary"
adam-trail set-conclusion <slug>                      # set conclusion (stdin)
adam-trail publish <slug>                             # mark as published
adam-trail show <slug>                                # display full trail
adam-trail list                                       # list all trails
adam-trail list -s published                          # only published
```

### adam-essay — Manage essays
```bash
echo "essay body..." | adam-essay create <slug> "<title>" -s "<subtitle>"
echo "updated body..." | adam-essay update <slug>
adam-essay publish <slug>
adam-essay show <slug>
adam-essay list
```

### adam-tweet — Save tweet drafts
```bash
adam-tweet "Plato's prisoners see shadows and call them real."
adam-tweet "New trail on doubt from Socrates to Descartes" -t the-evolution-of-doubt
```

### adam-sync — Push to Turso
```bash
adam-sync
```
Pushes your local database to Turso so the website reflects your latest work. Run after writing sessions.

## Tips

- After `adam-fetch`, always `adam-ingest` to make the text searchable
- Use `adam-search` liberally while reading — look for connections to other texts
- Write your daily log every session — it's your reading journal
- `adam-trail add-excerpt` can take specific sentences with `-e` (better than using the full chunk)
- The `-a` (append) flag on `adam-log` and `adam-note` lets you build up entries over a session
