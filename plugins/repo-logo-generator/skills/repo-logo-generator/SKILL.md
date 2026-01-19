---
name: repo-logo-generator
description: Generate minimalist logos for GitHub repositories via OpenRouter. A thin proxy skill with logo-optimized prompts. Use when asked to "generate a logo", "create repo logo", or "make a project logo".
metadata:
  version: "2.0.4"
---

# Repo Logo Generator

Generate professional minimalist logos by calling the OpenRouter skill with logo-optimized prompts.

## Usage

Use the **openrouter** skill's image generation capability. Refer to that skill for the command syntax, available models, and setup requirements.

Recommended models for logo generation: image generation models with good vector/minimalist style support (check openrouter skill for current options).

## Prompt Template

Use this template, filling in the project context:

```
A minimalist logo for {PROJECT_NAME}: {VISUAL_METAPHOR}.
Clean vector style on solid #0d1117 background (exact hex color, very dark desaturated blue, almost black).
Bright, light-colored icon (white, light blue, or light gray). No text, no letters, no words.
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

**Color guidance:** Use bright whites, light blues (#58a6ff), greens (#3fb950), oranges (#d29922), or purples (#a371f7) for icon elements. These GitHub accent colors provide excellent contrast on dark backgrounds.

## Technical Requirements

Logos must meet these criteria:
- **No text**: Readable at 16x16 to 256x256
- **Centered**: Works in circular and square crops
- **Exact background**: Solid #0d1117 (GitHub dark theme) - very dark desaturated blue, almost black
- **High contrast**: Bright/light icon colors for visibility on dark background
- **Clean style**: Minimalist vector, not photorealistic
- **Single focal point**: One clear visual element

## Workflow

1. Analyze the project (README, package files, code structure)
2. Determine project type and select visual metaphor from table
3. Construct prompt using template
4. Use openrouter skill's image generation to create the logo
5. Save to project's assets directory (e.g., `logo.png` at repo root)

## Example Prompt

For a CLI tool called "fastgrep" that searches files quickly:

```
A minimalist logo for fastgrep: A magnifying glass with speed lines forming a geometric pattern. Clean vector style on solid #0d1117 background (exact hex color, very dark desaturated blue, almost black). Bright, light-colored icon (white, light blue, or light gray). No text, no letters, no words. Single centered icon, geometric shapes, works at 64x64px.
```

Pass this prompt to the openrouter skill's image generation command, saving to the project's assets directory.
