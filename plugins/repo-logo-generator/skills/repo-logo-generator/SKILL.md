---
name: repo-logo-generator
description: Generate minimalist logos for GitHub repositories via OpenRouter. A thin proxy skill with logo-optimized prompts. Use when asked to "generate a logo", "create repo logo", or "make a project logo".
metadata:
  version: "2.0.6"
---

# Repo Logo Generator

Generate professional minimalist logos by calling the OpenRouter skill with logo-optimized prompts.

## Usage

Use the **openrouter** skill's image generation capability. Refer to that skill for the command syntax, available models, and setup requirements.

Recommended models for logo generation: image generation models with good vector/minimalist style support (check openrouter skill for current options).

## Configuration

Logo generation can be customized via configuration files. Check in order (first found wins):

1. **Project config**: `./.claude/readme-generator.json`
2. **User config**: `~/.claude/readme-generator.json`
3. **Default config**: `assets/default-config.json` (bundled with this skill)

Read JSON if exists, extract `logo` object. Project overrides user overrides default.

Users can copy the default config as a starting point:
```bash
cp <skill-path>/assets/default-config.json ~/.claude/readme-generator.json
```

### Configurable Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `background` | `#12161D` | Background hex color - RGB(18,22,29). Must be flat solid color. |
| `iconColors` | `["#ffffff", "#58a6ff", "#3fb950", "#d29922", "#a371f7"]` | Preferred icon colors |
| `style` | `minimalist` | Logo style description (can be detailed prompt text) |
| `size` | `64x64` | Target size for logo |
| `aspectRatio` | `1:1` | Aspect ratio for generation |
| `model` | `google/gemini-3-pro-image-preview` | OpenRouter model for image generation |
| `darkModeSupport` | `false` | Generate both dark/light variants |

### Example Configuration

```json
{
  "logo": {
    "background": "#1a1b26",
    "iconColors": ["#7aa2f7", "#bb9af7", "#7dcfff"],
    "style": "geometric",
    "model": "google/gemini-3-pro-image-preview"
  }
}
```

## Prompt Template

Use this template with configuration values (or defaults if no config found):

```
A {config.style} logo for {PROJECT_NAME}: {VISUAL_METAPHOR}.
Clean vector style on solid {config.background} background.
Icon colors from: {config.iconColors}. No text, no letters, no words.
Single centered icon, geometric shapes, works at {config.size}.
```

**Default prompt** (when no config exists, uses `assets/default-config.json`):

```
A minimalist logo for {PROJECT_NAME}: {VISUAL_METAPHOR}.
Clean vector style on flat solid #12161D background (no gradients, no patterns).
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
- **Flat background**: Solid #12161D - RGB(18,22,29). No gradients, starfields, patterns, or textures.
- **High contrast**: Bright/light icon colors for visibility on dark background
- **Clean style**: Minimalist vector, not photorealistic
- **Single focal point**: One clear visual element

## Workflow

1. **Load configuration**: Check `./.claude/readme-generator.json` then `~/.claude/readme-generator.json` for logo settings
2. Analyze the project (README, package files, code structure)
3. Determine project type and select visual metaphor from table
4. Construct prompt using template with config values (or defaults)
5. Use openrouter skill's image generation (using `config.model`) to create the logo
6. Save to project's assets directory (e.g., `logo.png` at repo root)
7. If `config.darkModeSupport` is true, generate a second variant with inverted colors

## Example Prompt

For a CLI tool called "fastgrep" that searches files quickly (using default config):

```
A minimalist logo for fastgrep: A magnifying glass with speed lines forming a geometric pattern. Clean vector style on flat solid #12161D background (no gradients, no patterns). Bright, light-colored icon (white, light blue, or light gray). No text, no letters, no words. Single centered icon, geometric shapes, works at 64x64px.
```

**With custom config** (`background: "#1a1b26"`, `style: "geometric"`, `iconColors: ["#7aa2f7", "#bb9af7"]`):

```
A geometric logo for fastgrep: A magnifying glass with speed lines forming a geometric pattern. Clean vector style on flat solid #1a1b26 background. Icon colors from: #7aa2f7, #bb9af7. No text, no letters, no words. Single centered icon, geometric shapes, works at 64x64px.
```

Pass this prompt to the openrouter skill's image generation command, saving to the project's assets directory.
