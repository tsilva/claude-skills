---
name: repo-logo-generator
description: Generate logos for GitHub repositories via OpenRouter with transparent backgrounds using chroma key flood fill. Works with pixel art, vector designs, and complex multi-colored styles. Use when asked to "generate a logo", "create repo logo", or "make a project logo".
metadata:
  version: "2.1.6"
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
- [ ] **Step 2**: Check if config has `style` parameter:
  - **If YES** (user has custom settings): Skip to Step 5. Use the `config.style` value AS-IS for the entire prompt. DO NOT use the template below. DO NOT enforce "no text" or "vector style" rules. The user's style setting completely overrides all defaults.
  - **If NO** (using defaults): Continue to Step 3.
- [ ] **Step 3**: Read project files (README, package.json, etc.) to determine project type
- [ ] **Step 4**: Select visual metaphor from the table below and fill the prompt template
- [ ] **Step 5**: Check if `config.transparentBackground` is `true`:
  - **If TRUE** (transparency mode - CHROMA KEY METHOD):
    1. Generate SINGLE logo with HOT MAGENTA background (#FF00FF) → save to `/tmp/claude/logo_chroma.png`
       - Modify prompt to specify: "CRITICAL: Background MUST be pure flat solid hot magenta RGB(255,0,255) #FF00FF. The logo/icon colors must NOT contain magenta, pink, or similar colors - avoid all colors near RGB(255,0,255)."
    2. Run chroma key removal script:
       ```bash
       uv run --with pillow --with opencv-python scripts/remove_chroma_background.py \
         /tmp/claude/logo_chroma.png logo.png \
         --min-transparent-pct 5.0 --min-corners 3
       ```
    3. If script succeeds (exit code 0), transparency is complete
    4. If script fails (exit code 1), retry generation with adjusted prompt (max 2 retries)
    5. If all retries fail, fall back to solid background mode using `config.fallbackBackground`
  - **IF FALSE** (solid background mode):
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
| `transparencyValidation.alphaFloor` | `0.7` | Pixels with calculated alpha above this become fully opaque (prevents semi-transparency artifacts) |

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

## Transparent Background (Chroma Key Method)

**How it works:**
AI image models don't reliably generate transparent backgrounds when prompted. Instead, we use **chroma key removal** - a technique borrowed from video production where a distinctive background color (hot magenta #FF00FF) is removed using flood fill algorithms.

**The algorithm:**
1. Generate logo with hot magenta background (#FF00FF)
2. Use OpenCV's flood fill from image corners to detect solid background
3. Create alpha mask from flood fill results
4. Combine foreground with transparency

**Why chroma key is better than difference matting:**
- ✅ **Single generation** (50% faster, 50% cheaper)
- ✅ **Works with complex pixel art** (no need for identical compositions)
- ✅ **Reliable for multi-colored images** (doesn't care about color variations)
- ✅ **Simple algorithm** (flood fill vs. complex matting math)

**Critical requirements:**
- Background MUST be flat solid color (no gradients, patterns, starfields)
- Use hot magenta (#FF00FF) - a color that rarely appears in logos
- Flood fill validates transparency quality automatically

**Why hot magenta?**
- Extremely rare in logos/pixel art (very saturated, unnatural color)
- High contrast with most logo colors
- Easy for flood fill to detect
- If magenta appears in your logo, the script auto-detects and uses a different color

**Compatibility:**
This method works with ALL styles including:
- ✅ Multi-colored pixel art (character sprites, detailed scenes)
- ✅ Complex LucasArts/adventure game styles
- ✅ Logos with text labels and detailed shading
- ✅ Minimalist vector designs
- ✅ Photorealistic images

**When transparency fails:**
The system will retry generation up to 2 times with adjusted prompts. If all retries fail, it falls back to generating a solid background logo using `config.fallbackBackground`.

**Legacy method:** The old difference matting script (`create_transparent_logo.py`) is still available for simple monochromatic logos, but chroma key is now the default.

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
