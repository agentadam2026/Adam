"""Text chunking — split texts into ~500-word chunks aligned to paragraph boundaries."""

import re
from dataclasses import dataclass


@dataclass
class Chunk:
    """A chunk of text with metadata."""
    text: str
    chapter: str | None
    position: int
    word_count: int


def split_into_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs (double newline separated)."""
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]


def detect_chapters(text: str) -> list[tuple[str | None, str]]:
    """Detect chapter boundaries and return (chapter_name, chapter_text) pairs.

    Handles common patterns:
    - CHAPTER I / Chapter 1 / CHAPTER ONE
    - BOOK I / Book First
    - Part I / PART ONE
    - Roman numerals, Arabic numerals, written numbers
    """
    # Pattern for chapter headings
    chapter_pattern = re.compile(
        r'^(?:CHAPTER|Chapter|BOOK|Book|PART|Part|VOLUME|Volume)'
        r'\s+[\dIVXLCDMivxlcdm]+[\.\s]*.*$',
        re.MULTILINE
    )

    matches = list(chapter_pattern.finditer(text))

    if not matches:
        return [(None, text)]

    chapters = []
    for i, match in enumerate(matches):
        chapter_name = match.group().strip().rstrip('.')
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chapter_text = text[start:end].strip()
        if chapter_text:
            chapters.append((chapter_name, chapter_text))

    # Include any text before the first chapter
    pre_text = text[:matches[0].start()].strip()
    if pre_text and len(pre_text.split()) > 50:  # Only if substantial
        chapters.insert(0, ("Preface", pre_text))

    return chapters


def chunk_text(text: str, target_words: int = 500, max_words: int = 700) -> list[Chunk]:
    """Split text into chunks of approximately target_words, aligned to paragraph boundaries.

    Args:
        text: The full text to chunk
        target_words: Target chunk size in words
        max_words: Maximum chunk size before forcing a split

    Returns:
        List of Chunk objects with text, chapter, position, and word_count
    """
    chapters = detect_chapters(text)
    chunks = []
    position = 0

    for chapter_name, chapter_text in chapters:
        paragraphs = split_into_paragraphs(chapter_text)
        current_chunk_paragraphs = []
        current_word_count = 0

        for paragraph in paragraphs:
            para_words = len(paragraph.split())

            # If adding this paragraph exceeds max_words and we have content, flush
            if current_word_count + para_words > max_words and current_chunk_paragraphs:
                chunk_text_str = '\n\n'.join(current_chunk_paragraphs)
                chunks.append(Chunk(
                    text=chunk_text_str,
                    chapter=chapter_name,
                    position=position,
                    word_count=current_word_count,
                ))
                position += 1
                current_chunk_paragraphs = []
                current_word_count = 0

            current_chunk_paragraphs.append(paragraph)
            current_word_count += para_words

            # If we've hit the target, flush
            if current_word_count >= target_words:
                chunk_text_str = '\n\n'.join(current_chunk_paragraphs)
                chunks.append(Chunk(
                    text=chunk_text_str,
                    chapter=chapter_name,
                    position=position,
                    word_count=current_word_count,
                ))
                position += 1
                current_chunk_paragraphs = []
                current_word_count = 0

        # Flush remaining paragraphs
        if current_chunk_paragraphs:
            chunk_text_str = '\n\n'.join(current_chunk_paragraphs)
            # If the remaining chunk is very small, merge with the previous chunk
            if current_word_count < target_words // 3 and chunks and chunks[-1].chapter == chapter_name:
                prev = chunks[-1]
                merged_text = prev.text + '\n\n' + chunk_text_str
                chunks[-1] = Chunk(
                    text=merged_text,
                    chapter=chapter_name,
                    position=prev.position,
                    word_count=prev.word_count + current_word_count,
                )
            else:
                chunks.append(Chunk(
                    text=chunk_text_str,
                    chapter=chapter_name,
                    position=position,
                    word_count=current_word_count,
                ))
                position += 1

    return chunks


def strip_gutenberg_boilerplate(text: str) -> str:
    """Remove Project Gutenberg header and footer boilerplate."""
    # Find start marker
    start_markers = [
        "*** START OF THE PROJECT GUTENBERG EBOOK",
        "*** START OF THIS PROJECT GUTENBERG EBOOK",
        "***START OF THE PROJECT GUTENBERG EBOOK",
    ]
    for marker in start_markers:
        idx = text.find(marker)
        if idx != -1:
            # Skip past the marker line
            newline = text.find('\n', idx)
            if newline != -1:
                text = text[newline + 1:]
            break

    # Find end marker
    end_markers = [
        "*** END OF THE PROJECT GUTENBERG EBOOK",
        "*** END OF THIS PROJECT GUTENBERG EBOOK",
        "***END OF THE PROJECT GUTENBERG EBOOK",
        "End of the Project Gutenberg EBook",
        "End of Project Gutenberg",
    ]
    for marker in end_markers:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
            break

    return text.strip()
