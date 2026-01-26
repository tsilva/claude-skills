# Skill Compression Guide

SKILL.md must fit within **15,000 characters**. This guide helps when you exceed the budget.

## Table of Contents

- [Compression Philosophy](#compression-philosophy)
- [Techniques (In Order of Preference)](#techniques-in-order-of-preference)
- [What to Preserve (Never Remove)](#what-to-preserve-never-remove)
- [What to Aggressively Compress](#what-to-aggressively-compress)
- [Verification](#verification)

## Compression Philosophy

1. **Preserve functionality** - Skill must still work after compression
2. **Preserve critical info** - Keep what Claude needs to execute correctly
3. **Remove redundancy** - Say it once, not twice
4. **Trust Claude** - No hand-holding for obvious things

## Techniques (In Order of Preference)

### 1. Remove Verbose Explanations

Before:
```markdown
## How It Works

This skill works by first analyzing the project structure to understand what type of project it is.
Then it reads the configuration files to determine user preferences. After that, it generates
the appropriate output based on the analysis.
```

After:
```markdown
## Workflow
1. Analyze project structure
2. Read config files
3. Generate output
```

### 2. Consolidate Examples

One good example beats three mediocre ones.

Before:
```markdown
## Examples

### Example 1: Basic Usage
/my-skill ./src

### Example 2: With Options
/my-skill ./src --verbose

### Example 3: Different Path
/my-skill ./lib
```

After:
```markdown
## Example
/my-skill ./src --verbose
```

### 3. Eliminate Redundancy

If the same concept appears in multiple places, keep only one.

### 4. Simplify Tables

Remove obvious columns, combine related rows.

Before:
```markdown
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| name | string | yes | none | The skill name |
```

After:
```markdown
| Field | Constraints |
|-------|-------------|
| name | Required. String, 1-64 chars |
```

### 5. Move Reference Material

Put detailed docs in `references/` subdirectory:

```
skill/
├── SKILL.md           # Core instructions only
└── references/
    ├── api-details.md  # Full API reference
    └── examples.md     # Extended examples
```

Reference from SKILL.md: "See `references/api-details.md` for full API reference."

### 6. Remove Obvious Instructions

Claude knows how to:
- Read files
- Run commands
- Parse JSON/YAML
- Handle errors
- Write to files

Don't explain these.

## What to Preserve (Never Remove)

- Required frontmatter (name, description)
- Core workflow steps
- Critical constraints and edge cases
- Configuration parameters and defaults
- Security-relevant instructions
- Error handling for non-obvious cases

## What to Aggressively Compress

- Background explanations ("why" sections)
- Multiple examples of the same concept
- Verbose installation instructions
- Historical context or changelogs
- Best practices Claude already knows
- Obvious prerequisites

## Verification

After compressing, always validate:

```bash
python plugins/skill-author/skills/skill-author/scripts/validate_skill.py /path/to/skill
```

Check for:
- 0 errors
- Character count under 15,000
- Skill still functions correctly
