#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Extract tagline from README.md for GitHub description sync.

Handles complex README structures including:
- YAML frontmatter (--- blocks)
- Centered divs with logos, titles, badges
- Bold formatting (**tagline**)
- Emoji preservation
- Link-only lines

Usage:
    uv run scripts/extract_tagline.py /path/to/README.md

Returns:
    Tagline on stdout, exit 0 on success
    Error message on stderr, exit 1 on failure
"""

import re
import sys
from pathlib import Path

# GitHub description limit
MAX_LENGTH = 350


def strip_yaml_frontmatter(content: str) -> str:
    """Remove YAML frontmatter if present."""
    if content.startswith("---"):
        # Find closing ---
        match = re.search(r"^---\s*$", content[3:], re.MULTILINE)
        if match:
            return content[3 + match.end():].lstrip()
    return content


def strip_html_tags(line: str) -> str:
    """Remove HTML tags from a line."""
    return re.sub(r"<[^>]+>", "", line)


def is_skip_line(line: str) -> bool:
    """Check if line should be skipped during tagline search."""
    stripped = line.strip()

    # Empty line
    if not stripped:
        return True

    # Markdown headers
    if stripped.startswith("#"):
        return True

    # Badge images ([![ or just ![)
    if stripped.startswith("!["):
        return True

    # Blockquotes (commonly used for notices/warnings)
    if stripped.startswith(">"):
        return True

    # HTML tags (div, img, br, p, etc.)
    if stripped.startswith("<") and not stripped.startswith("<http"):
        # Check if it's an HTML tag (not a broken link or something else)
        if re.match(r"^</?[a-zA-Z][^>]*>", stripped):
            return True

    # Link-only lines: [text](url) or [text][ref]
    # Match lines that are ONLY links with optional whitespace
    link_only = re.match(r"^\s*\[([^\]]+)\]\([^)]+\)(\s*·\s*\[([^\]]+)\]\([^)]+\))*\s*$", stripped)
    if link_only:
        return True

    # Reference-style link definitions: [text]: url
    if re.match(r"^\[[^\]]+\]:\s*\S+", stripped):
        return True

    # Horizontal rules (---, ***, ___)
    if re.match(r"^[-*_]{3,}\s*$", stripped):
        return True

    # Lines that are only HTML after stripping
    no_html = strip_html_tags(stripped).strip()
    if not no_html:
        return True

    return False


def extract_tagline_text(line: str) -> str:
    """
    Extract clean tagline text from a line.

    Handles:
    - Bold formatting: **text** -> text
    - HTML tags: <b>text</b> -> text
    - Leading/trailing whitespace
    """
    text = line.strip()

    # Remove HTML tags
    text = strip_html_tags(text)

    # Remove bold markdown: **text** -> text
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)

    # Remove italic markdown: *text* or _text_ -> text
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)

    # Remove inline code: `text` -> text
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Clean up extra whitespace
    text = " ".join(text.split())

    return text.strip()


def extract_tagline(readme_path: Path) -> str | None:
    """
    Extract tagline from README.md.

    Strategy:
    1. Remove YAML frontmatter
    2. Scan lines, skipping headers/badges/HTML/links
    3. First qualifying line is the tagline
    4. Extract text, stripping formatting
    5. Truncate to GitHub limit if needed

    Returns:
        Tagline string or None if not found
    """
    try:
        content = readme_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None

    # Strip YAML frontmatter
    content = strip_yaml_frontmatter(content)

    lines = content.splitlines()

    for line in lines:
        if is_skip_line(line):
            continue

        # Found a candidate line - extract the tagline
        tagline = extract_tagline_text(line)

        # Validate: should have meaningful content
        if len(tagline) < 10:  # Too short to be a real tagline
            continue

        # Truncate to GitHub limit
        if len(tagline) > MAX_LENGTH:
            tagline = tagline[:MAX_LENGTH - 3] + "..."

        return tagline

    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_tagline.py <readme_path>", file=sys.stderr)
        sys.exit(1)

    readme_path = Path(sys.argv[1])

    if not readme_path.exists():
        print(f"Error: File not found: {readme_path}", file=sys.stderr)
        sys.exit(1)

    tagline = extract_tagline(readme_path)

    if tagline:
        print(tagline)
        sys.exit(0)
    else:
        print("Error: Could not extract tagline from README", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
