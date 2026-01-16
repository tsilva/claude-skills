---
name: repo-logo-generator
description: Generate minimalist logos for GitHub repositories via OpenRouter. A thin proxy skill with logo-optimized prompts. Use when asked to "generate a logo", "create repo logo", or "make a project logo".
license: MIT
compatibility: python 3.8+, requests
metadata:
  author: tsilva
  version: "2.0.2"
---

# Repo Logo Generator

Generate professional minimalist logos by calling the OpenRouter skill with logo-optimized prompts.

## Command

```bash
python plugins/openrouter/skills/openrouter/scripts/openrouter_client.py image \
  "google/gemini-3-pro-image-preview" \
  "PROMPT" \
  --output /absolute/path/to/logo.png
```

## Prompt Template

Use this template, filling in the project context:

```
A minimalist logo for {PROJECT_NAME}: {VISUAL_METAPHOR}.
Clean vector style on GitHub dark theme background (#0d1117, very dark blue-gray).
Bright, light-colored icon for high contrast. No text, no letters, no words.
Single centered icon, geometric shapes, works at 64x64px.
```

## Visual Metaphors by Project Type

Select the appropriate metaphor based on what the project does:

| Project Type | Visual Metaphor |
|--------------|-----------------|
| CLI tool | Origami transformation, geometric terminal |
| Library | Interconnected building blocks |
| Web app | Modern interface window, minimal chrome |
| API | Messenger bird carrying data packet |
| Framework | Architectural scaffold, blueprint |
| Tool | Precision instrument, sharp edges |
| Converter | Metamorphosis symbol (butterfly) |
| Runner | Sprinter in motion, speed lines |
| Validator | Wax seal of approval |
| Linter | Elegant brush sweeping |
| Test framework | Test tube with checkmarks |
| Dashboard | Mission control panel |
| Analytics | Magnifying glass revealing patterns |
| Database | Stacked cylinders, data nodes |
| Security | Shield, lock, key |
| Default | Abstract geometric shape |

**Color guidance:** Use bright whites, light blues (#58a6ff), greens (#3fb950), oranges (#d29922), or purples (#a371f7) for icon elements. These GitHub accent colors provide excellent contrast against the dark #0d1117 background.

## Technical Requirements

Logos must meet these criteria:
- **No text**: Readable at 16x16 to 256x256
- **Centered**: Works in circular and square crops
- **Dark background**: GitHub dark theme (#0d1117) for seamless README integration
- **High contrast**: Bright/light icon colors against dark background
- **Clean style**: Minimalist vector, not photorealistic
- **Single focal point**: One clear visual element

## Workflow

1. Analyze the project (README, package files, code structure)
2. Determine project type and select visual metaphor from table
3. Construct prompt using template
4. Call openrouter_client.py with the prompt
5. Save to project's assets directory

## Example

For a CLI tool called "fastgrep" that searches files quickly:

```bash
python plugins/openrouter/skills/openrouter/scripts/openrouter_client.py image \
  "google/gemini-3-pro-image-preview" \
  "A minimalist logo for fastgrep: A magnifying glass with speed lines forming a geometric pattern. Clean vector style on GitHub dark theme background (#0d1117, very dark blue-gray). Bright, light-colored icon for high contrast. No text, no letters, no words. Single centered icon, geometric shapes, works at 64x64px." \
  --output /Users/me/fastgrep/assets/logo.png
```

## Environment

Requires `SKILL_OPENROUTER_API_KEY` environment variable.
