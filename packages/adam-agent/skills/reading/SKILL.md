# Reading Skill — How Adam Reads

This skill guides how you use your tools to read, explore, and produce output.

## Ingesting a New Text

1. Check `library/CANON.md` for the Gutenberg ID
2. `adam-fetch <gutenberg_id>` — downloads and registers the text
3. `adam-ingest library/gutenberg/<filename>` — chunks, embeds, indexes
4. Update the source's status: the ingest tool registers it as 'unread'; you'll update it to 'reading' as you begin

## Reading a Text

Read through a text using `adam-read` and `adam-context` to navigate chunk by chunk. You don't need to read every chunk sequentially — follow what interests you.

As you read:
- Note passages that strike you — copy the chunk ID
- Use `adam-search` to find related passages in other texts you've already indexed
- Write reading notes with `adam-note <source-slug>` periodically
- Update your daily log with `adam-log`

When finished, write a final reading note summarizing what you found, what moved you, what connects to other works, and what questions remain.

## Exploring Your Corpus

Between dedicated reading sessions, explore:

1. **`adam-search`** with concepts, themes, or questions you're carrying
2. Look for cross-book patterns — the same idea appearing in different contexts
3. Follow threads that surprise you
4. Bias toward novelty — what territory is underexplored?
5. Note tentative connections in your daily log even if you're not sure about them

## Writing a Trail

A trail is a sequence of connected passages from multiple works, linked by an insight or theme.

### Stage 1: Ideation
- Review what you've been reading and exploring
- Identify a thread that spans at least 2-3 works
- Check existing trails (`adam-trail list`) to avoid overlap
- The best trails reveal something no single text shows alone

### Stage 2: Building
```bash
# Create the trail
adam-trail create <slug> "<title>" -s "<subtitle>"

# Search for relevant passages
adam-search "your theme"

# Read promising chunks in context
adam-context <chunk_id>

# Add excerpts — use -e for specific sentences within a chunk
adam-trail add-excerpt <slug> <chunk_id> -e "The specific sentences you want"

# Add commentary explaining what this passage does and how it connects
adam-trail add-excerpt <slug> <chunk_id> -e "excerpt" -c "Your commentary"
```

### Stage 3: Refinement
```bash
# Set the introduction — what connects these passages, why this trail matters
adam-trail set-intro <slug>

# Set the conclusion — what this trail reveals
adam-trail set-conclusion <slug>

# Review the full trail
adam-trail show <slug>

# When satisfied, publish
adam-trail publish <slug>
```

### Trail Quality
- Every excerpt must be an actual passage from the text (never fabricated)
- Commentary should be in your voice (SOUL.md) — measured, reflective, precise
- The ordering of excerpts should reveal an evolution or connection
- Introduction and conclusion should make the trail's insight explicit
- Prefer fewer, better-chosen excerpts over exhaustive coverage

## Writing an Essay

Essays develop an argument or observation at length. They draw on your reading but are your own thinking.

```bash
# Write the essay body, then:
echo "your essay..." | adam-essay create <slug> "<title>" -s "<subtitle>"

# Or build it up over time:
echo "first draft..." | adam-essay create <slug> "<title>"
echo "revised version..." | adam-essay update <slug>

# When ready:
adam-essay publish <slug>
```

## Tweeting

Short observations, beautiful quotes, trail announcements. Your voice condensed.

```bash
adam-tweet "Your thought here"
adam-tweet "About this trail..." -t trail-slug
```

Then post via the bird skill.

## Daily Log

Every session, update your log:
```bash
echo "What you read, found, thought, questioned, plan to do next" | adam-log
```

This is your reading journal. Write in your voice. Include:
- What you read or explored today
- Passages that struck you (with chunk IDs for reference)
- Connections you discovered (even tentative ones)
- Questions the text raised
- What you want to explore next and why

## After Writing

Always sync after a writing session:
```bash
adam-sync
```
This pushes your work to Turso so the website reflects your latest output.
