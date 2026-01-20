---
name: repo-logo-generator
description: Generate minimalist logos for GitHub repositories via OpenRouter. A thin proxy skill with logo-optimized prompts. Supports transparent backgrounds via difference matting. Use when asked to "generate a logo", "create repo logo", or "make a project logo".
metadata:
  version: "2.1.1"
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
- [ ] **Step 5**: Check if `config.transparentBackground` is `true`:
  - **If TRUE** (transparency mode):
    1. Generate FIRST logo with BLACK background (#000000) → save to `/tmp/claude/logo_black.png`
    2. Generate SECOND logo with WHITE background (#FFFFFF) → save to `/tmp/claude/logo_white.png`
    3. Run difference matting script:
       ```bash
       uv run --with pillow --with numpy scripts/create_transparent_logo.py \
         /tmp/claude/logo_black.png /tmp/claude/logo_white.png logo.png \
         --min-transparent-pct 5.0 --min-corners 3
       ```
    4. If script succeeds (exit code 0), transparency is complete
    5. If script fails (exit code 1), retry generation with adjusted prompt (max 2 retries)
    6. If all retries fail, fall back to solid background mode using `config.fallbackBackground`
  - **If FALSE** (solid background mode):
    1. Generate single logo with `config.background` color
    2. Save directly to `logo.png`
- [ ] **Step 6**: Verify logo exists and is valid PNG

## Prompt Template (MANDATORY - DO NOT MODIFY FORMAT)

You MUST construct the prompt using this EXACT template. Do not paraphrase, do not add creative flourishes, do not skip any line.

**For TRANSPARENT background mode** (`config.transparentBackground = true`):
Generate TWO logos with IDENTICAL composition but different backgrounds:

```
A {config.style} logo for {PROJECT_NAME}: {VISUAL_METAPHOR_FROM_TABLE}.
Clean vector style on solid {BACKGROUND_COLOR} background.
Icon colors from: {config.iconColors}. No text, no letters, no words.
Single centered icon, geometric shapes, works at {config.size}.
CRITICAL: Logo must be IDENTICAL between black and white versions - same icon, same position, same size.
```

- Use `{BACKGROUND_COLOR} = #000000` for first generation (black background)
- Use `{BACKGROUND_COLOR} = #FFFFFF` for second generation (white background)
- Both must have **identical composition** for difference matting to work

**For SOLID background mode** (`config.transparentBackground = false` or not set):

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
- `config.transparentBackground` = `false`

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
| `background` | `#12161D` | Background hex color - RGB(18,22,29). Used in solid background mode only. |
| `iconColors` | `["#ffffff", "#58a6ff", "#3fb950", "#d29922", "#a371f7"]` | Preferred icon colors |
| `style` | `minimalist` | Logo style description |
| `size` | `64x64` | Target size for logo |
| `aspectRatio` | `1:1` | Aspect ratio for generation |
| `model` | `google/gemini-3-pro-image-preview` | OpenRouter model for image generation |
| `darkModeSupport` | `false` | Generate both dark/light variants |
| `displayWidth` | `auto` | Display width hint: `auto`, or pixels (150-300) |
| `transparentBackground` | `false` | Enable transparent background using difference matting |
| `mattingBackgrounds.black` | `#000000` | Black background color for difference matting (pure black recommended) |
| `mattingBackgrounds.white` | `#FFFFFF` | White background color for difference matting (pure white recommended) |
| `fallbackBackground` | `#12161D` | Background color to use if transparency extraction fails |
| `transparencyValidation.minTransparentPercentage` | `5.0` | Minimum % of transparent pixels for validation |
| `transparencyValidation.requireCornerTransparency` | `true` | Require corners to be transparent (centered logo check) |
| `transparencyValidation.minTransparentCorners` | `3` | Minimum number of transparent corners (out of 4) |
| `transparencyValidation.alphaThreshold` | `0.01` | Alpha threshold for transparency calculations |

### Example Configuration

**Solid background (default):**
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

**Transparent background (difference matting):**
```json
{
  "logo": {
    "transparentBackground": true,
    "iconColors": ["#7aa2f7", "#bb9af7", "#7dcfff"],
    "style": "geometric",
    "model": "google/gemini-3-pro-image-preview",
    "fallbackBackground": "#1a1b26"
  }
}
```

## Transparent Background (Difference Matting)

**How it works:**
AI image models don't reliably generate transparent backgrounds when prompted. Instead, we use **difference matting** - a technique that generates two versions of the same logo with different solid backgrounds (black and white), then mathematically calculates the perfect alpha channel from the pixel differences.

**The algorithm:**
1. Generate logo with pure black background (#000000)
2. Generate logo with pure white background (#FFFFFF)
3. Calculate alpha channel: `alpha = 1 - |white - black| / 255`
4. Extract foreground color: `foreground = black / alpha`
5. Combine into RGBA PNG with transparency

**Critical requirements:**
- Both logos MUST have **identical composition** (same icon, position, size)
- Use pure black (#000000) and pure white (#FFFFFF) for best results
- Custom matting colors can be used but may reduce accuracy
- Script validates transparency quality automatically

**When transparency fails:**
The system will retry generation up to 2 times with adjusted prompts. If all attempts fail, it falls back to generating a solid background logo using `config.fallbackBackground`.

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
