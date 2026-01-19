---
name: repo-logo-generator
description: Generate minimalist logos for GitHub repositories via OpenRouter. A thin proxy skill with logo-optimized prompts. Use when asked to "generate a logo", "create repo logo", or "make a project logo".
metadata:
  version: "2.0.9"
---

# Repo Logo Generator

Generate professional minimalist logos by calling the OpenRouter skill with logo-optimized prompts.

## REQUIRED: Execution Checklist (MUST complete in order)

Follow these steps exactly. Do not skip steps or improvise.

- [ ] **Step 1**: Load config by reading each path in order (stop at first that exists):
  1. Read `./.claude/readme-generator.json` (project config)
  2. Read `~/.claude/readme-generator.json` (user config)
  3. Read `assets/default-config.json` from this skill's directory (default)

  **IMPORTANT**: Actually READ each file path, don't just search for JSON files.
- [ ] **Step 2**: Read project files (README, package.json, etc.) to determine project type
- [ ] **Step 3**: Select visual metaphor from the table below (MUST use table, do NOT invent custom metaphors)
- [ ] **Step 4**: Fill the prompt template using the EXACT format below (do not paraphrase)
- [ ] **Step 5**: Call openrouter skill with the filled template
- [ ] **Step 6**: Save output to project root as `logo.png`

## Prompt Template (MANDATORY - DO NOT MODIFY FORMAT)

You MUST construct the prompt using this EXACT template. Do not paraphrase, do not add creative flourishes, do not skip any line:

```
A {config.style} logo for {PROJECT_NAME}: {VISUAL_METAPHOR_FROM_TABLE}.
Clean vector style on solid {config.background} background.
Icon colors from: {config.iconColors}. No text, no letters, no words.
Single centered icon, geometric shapes, works at {config.size}.
```

**Default values** (when no config exists):
- `config.style` = `minimalist`
- `config.background` = `#12161D`
- `config.iconColors` = `#ffffff, #58a6ff, #3fb950, #d29922, #a371f7`
- `config.size` = `64x64`

### Filled Example

For a CLI tool called "fastgrep":

```
A minimalist logo for fastgrep: A magnifying glass with speed lines forming a geometric pattern.
Clean vector style on solid #12161D background.
Icon colors from: #ffffff, #58a6ff, #3fb950, #d29922, #a371f7. No text, no letters, no words.
Single centered icon, geometric shapes, works at 64x64.
```

## Visual Metaphors by Project Type (MUST use this table)

Select the metaphor that matches the project type. Do NOT invent alternatives.

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

## ❌ DO NOT

- Invent custom visual metaphors (use the table above)
- Paraphrase the template (use it verbatim with values filled in)
- Add extra descriptive language like "network nodes", "data fragments", "circuit patterns", "flowing streams"
- Skip any line of the template
- Add "gradient", "3D", "glossy", "photorealistic" or similar non-minimalist styles
- Include text, letters, or words in the logo description

## Configuration Reference

Logo generation can be customized via configuration files. Check in order (first found wins):

1. **Project config**: `./.claude/readme-generator.json`
2. **User config**: `~/.claude/readme-generator.json`
3. **Default config**: `assets/default-config.json` (bundled with this skill)

Read JSON if exists, extract `logo` object. Project overrides user overrides default.

### Configurable Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `background` | `#12161D` | Background hex color - RGB(18,22,29). Must be flat solid color. |
| `iconColors` | `["#ffffff", "#58a6ff", "#3fb950", "#d29922", "#a371f7"]` | Preferred icon colors |
| `style` | `minimalist` | Logo style description |
| `size` | `64x64` | Target size for logo |
| `aspectRatio` | `1:1` | Aspect ratio for generation |
| `model` | `google/gemini-3-pro-image-preview` | OpenRouter model for image generation |
| `darkModeSupport` | `false` | Generate both dark/light variants |
| `displayWidth` | `auto` | Display width hint: `auto`, or pixels (150-300) |

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

## Technical Requirements

Logos must meet these criteria:
- **No text**: Readable at 16x16 to 256x256
- **Centered**: Works in circular and square crops
- **Flat background**: Solid color. No gradients, starfields, patterns, or textures.
- **High contrast**: Bright/light icon colors for visibility on dark background
- **Clean style**: Minimalist vector, not photorealistic
- **Single focal point**: One clear visual element

## Usage

Use the **openrouter** skill's image generation capability. Refer to that skill for the command syntax, available models, and setup requirements.
