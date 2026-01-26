# Skill Templates

Copy-paste templates for creating skills.

## Table of Contents

- [Project-Level Skill (Minimal)](#project-level-skill-minimal)
- [Project-Level Skill (Full)](#project-level-skill-full)
- [Plugin Skill - plugin.json](#plugin-skill---pluginjson)
- [Plugin Skill - SKILL.md](#plugin-skill---skillmd)
- [marketplace.json Entry](#marketplacejson-entry)
- [Python Script Template](#python-script-template)
- [Description Examples](#description-examples)

## Project-Level Skill (Minimal)

Location: `.claude/skills/{skill-name}/SKILL.md`

```yaml
---
name: {skill-name}
description: {What it does}. Use when {triggers}.
---

# {Skill Title}

{Instructions here}
```

## Project-Level Skill (Full)

```yaml
---
name: {skill-name}
description: {What it does}. Use when {triggers}. Handles {use cases}.
argument-hint: "[arg1] [arg2]"
---

# {Skill Title}

## Overview

{Brief explanation}

## Workflow

1. {Step 1}
2. {Step 2}
3. {Step 3}

## Configuration

{Any configurable options}

## Examples

{Usage examples}
```

## Plugin Skill - plugin.json

Location: `plugins/{plugin-name}/.claude-plugin/plugin.json`

```json
{
  "name": "{plugin-name}",
  "description": "{What this skill does}.",
  "version": "1.0.0",
  "author": {
    "name": "{your-name}"
  }
}
```

## Plugin Skill - SKILL.md

Location: `plugins/{plugin-name}/skills/{skill-name}/SKILL.md`

```yaml
---
name: {skill-name}
description: {What it does}. Use when {triggers}. Handles {use cases}.
license: MIT
argument-hint: "[optional-args]"
metadata:
  author: {your-name}
  version: "1.0.0"
---

# {Skill Title}

## Overview

{Brief explanation of what this skill does}

## Workflow

1. {Step 1}
2. {Step 2}
3. {Step 3}

## Commands

### Primary Operation

```bash
{main command or operation}
```

### Validation

```bash
python plugins/skill-author/skills/skill-author/scripts/validate_skill.py plugins/{plugin-name}/skills/{skill-name}
```

## Configuration

{Any configurable options, if applicable}

## Error Handling

{Common errors and how to resolve them}
```

## marketplace.json Entry

Add to `.claude-plugin/marketplace.json` plugins array:

```json
{
  "name": "{plugin-name}",
  "source": "./plugins/{plugin-name}",
  "description": "{Same description as plugin.json}",
  "version": "1.0.0"
}
```

## Python Script Template

Location: `plugins/{plugin-name}/skills/{skill-name}/scripts/{script-name}.py`

```python
#!/usr/bin/env python3
"""
{Brief description of what this script does.}

Usage:
    python {script-name}.py [args]

Exit codes: 0 = success, 1 = error
"""

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="{Description}")
    parser.add_argument("input", type=str, help="Input argument")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Implementation here

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Description Examples

### Good Descriptions

```yaml
# Specific, includes triggers
description: Generate professional README files with badges, logo integration, and modern design. Use when creating or updating project documentation, or when user asks for a README.

# Clear use cases
description: Validate Claude Code skills against the Agent Skills specification. Use when creating a new skill, modifying SKILL.md, or debugging skill issues.

# Multiple triggers
description: Extract text from PDFs, fill forms, merge documents. Triggers on PDF file paths, requests for document extraction, or form filling tasks.
```

### Bad Descriptions

```yaml
# Too vague
description: Helps with files

# No triggers
description: A utility for various tasks

# Too long/verbose
description: This is a comprehensive skill that helps users with many different types of tasks including but not limited to... (continues for 800 more characters)
```
