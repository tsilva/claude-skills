---
name: readme-generator
description: Creates or updates README.md files following GitHub best practices with badges, visual hierarchy, and comprehensive documentation. Use when asked to "create a README", "generate documentation", "write a README for this project", or when starting a new project that needs documentation.
license: Apache-2.0
metadata:
  author: tsilva
  version: "1.0.0"
---

# README Generator

Create stunning, modern README files that make projects stand out.

## Overview

Generates professional README.md files following GitHub best practices and modern design patterns. Analyzes your codebase to create comprehensive, visually appealing documentation.

## Features

### Visual Design
- **Centered hero section** with logo, title, and tagline
- **Badge collection** - build status, version, license, downloads, etc.
- **Organized sections** with clear visual hierarchy
- **Syntax-highlighted code blocks** with copy-friendly examples
- **Tables** for feature comparisons and API references

### Content Generation
- **Smart project analysis** - auto-detects project type, language, and framework
- **Installation instructions** - npm, pip, cargo, go, etc. based on detected package manager
- **Usage examples** - real code snippets from your codebase
- **API documentation** - extracted from code comments and type definitions
- **Contributing guidelines** - standard open-source contribution workflow
- **License detection** - reads and links to your LICENSE file

### Modern Patterns
- **Collapsible sections** for detailed content using `<details>` tags
- **Quick start guides** - get users running in under 2 minutes
- **Feature highlights** with icons or emojis (when appropriate)
- **Responsive images** that scale properly on all devices

## Logo Generation

Generate a custom logo for your project using the **OpenRouter skill**.

### How to Generate a Logo

1. First, invoke the OpenRouter skill to generate an image:
```bash
# Use an image generation model via OpenRouter
python plugins/openrouter/skills/openrouter/scripts/openrouter_client.py image \
  "google/gemini-3-pro-image-preview" \
  "A minimalist, modern logo for [YOUR_PROJECT_NAME]: [describe the project concept]. Clean vector style, suitable for GitHub README, dark and light mode compatible, centered composition, no text." \
  --output /absolute/path/to/your/project/assets/logo.png
```

2. Then reference it in your README:
```markdown
<p align="center">
  <img src="assets/logo.png" alt="Project Logo" width="200" height="200">
</p>
```

### Recommended Image Models

| Model | Best For | Notes |
|-------|----------|-------|
| `google/gemini-3-pro-image-preview` | Quick iterations | Fast, good quality |
| `black-forest-labs/flux.2-pro` | Final production logo | Highest quality |
| `black-forest-labs/flux-1.1-pro` | Balanced option | Good quality, reasonable speed |

### Logo Prompt Tips

- Include "minimalist" or "clean" for GitHub-appropriate logos
- Specify "no text" to avoid unreadable small text
- Add "dark and light mode compatible" for theme flexibility
- Mention "vector style" for crisp scaling
- Describe the core concept of your project for relevant imagery

## README Structure Template

```markdown
<p align="center">
  <img src="assets/logo.png" alt="Logo" width="200">
</p>

<h1 align="center">Project Name</h1>

<p align="center">
  <strong>One-line description of what it does</strong>
</p>

<p align="center">
  [badges: build, version, license, downloads]
</p>

---

## Overview
Brief explanation of the project's purpose and value proposition.

## Features
- Feature 1
- Feature 2
- Feature 3

## Quick Start

\`\`\`bash
# Installation
npm install your-package

# Basic usage
your-command --help
\`\`\`

## Installation
Detailed installation instructions for different platforms/methods.

## Usage
Comprehensive usage examples with code snippets.

## API Reference
(if applicable) Documentation of public APIs.

## Configuration
Available configuration options and examples.

## Contributing
How to contribute to the project.

## License
License information and link.

---

<p align="center">
  Made with [tool/framework]
</p>
```

## Workflow

1. **Analyze project** - scan for package.json, Cargo.toml, pyproject.toml, go.mod, etc.
2. **Detect project type** - CLI, library, web app, API, etc.
3. **Extract metadata** - name, description, version, author, license
4. **Generate README.md** - create or update the file in the project root
5. **Suggest logo generation** - provide OpenRouter commands for logo creation

## Examples

### CLI Tool README
```markdown
# mycli

> A blazing fast CLI for doing X

[![npm](https://img.shields.io/npm/v/mycli)](https://npmjs.com/package/mycli)

## Install

\`\`\`bash
npm install -g mycli
\`\`\`

## Usage

\`\`\`bash
mycli init        # Initialize a new project
mycli build       # Build the project
mycli deploy      # Deploy to production
\`\`\`
```

### Library README
```markdown
# mylib

A lightweight library for handling X with zero dependencies.

## Install

\`\`\`bash
pip install mylib
\`\`\`

## Quick Start

\`\`\`python
from mylib import Thing

thing = Thing()
result = thing.process(data)
\`\`\`

## API

### `Thing(options)`
Creates a new Thing instance.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `timeout` | `int` | `30` | Request timeout in seconds |
```

## Best Practices Enforced

1. **Scannable content** - users should find what they need in seconds
2. **Copy-paste ready** - all code examples should work as-is
3. **Progressive disclosure** - basic info first, details in expandable sections
4. **Visual hierarchy** - clear headings, consistent formatting
5. **Mobile-friendly** - readable on GitHub mobile app
6. **Accessible** - alt text for images, semantic markup
