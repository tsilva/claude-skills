# README Templates by Project Type

## Table of Contents

- [Standard Sections (All Projects)](#standard-sections-all-projects)
- [AI/ML Projects](#aiml-projects)
- [CLI Tools](#cli-tools)
- [Libraries](#libraries)
- [Web Apps](#web-apps)

---

## Standard Sections (All Projects)

```markdown
## Overview
Brief explanation of purpose and value proposition.

## Features
- Feature 1 with benefit
- Feature 2 with benefit
- Feature 3 with benefit

## Quick Start
```bash
pip install mypackage
```

```python
from mypackage import Feature
result = Feature().run("input")
print(result)  # Output: "Success"
```

## Installation
Detailed installation for different platforms/methods.

## Usage
Comprehensive examples with code snippets.

## Contributing
How to contribute to the project.

## License
License information and link.
```

---

## AI/ML Projects

Include these additional sections:

### Model Card (YAML header)

```yaml
---
language: en
license: mit
library_name: transformers
tags: [text-classification, bert]
datasets: [imdb]
metrics: [accuracy, f1]
base_model: bert-base-uncased
---
```

### Hardware Requirements

```markdown
## Requirements
- **GPU**: NVIDIA with CUDA support (8GB+ VRAM)
- **CUDA**: 11.7+
- **RAM**: 16GB+ recommended
```

### Benchmark Table

| Model | Dataset | Accuracy | GPU | Training Time |
|-------|---------|----------|-----|---------------|
| Base | SQuAD 2.0 | 83.1% | V100 | 2h 15m |
| Large | SQuAD 2.0 | 87.4% | A100 | 4h 30m |

Include random seeds, batch sizes, and hardware for reproducibility.

### Demo Links

```markdown
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](link)
[![Hugging Face](https://img.shields.io/badge/🤗-Demo-yellow)](link)
```

### Required Ethical Sections

- Bias, risks, and limitations
- Out-of-scope uses
- Environmental impact
- Data privacy considerations

### Citation

```bibtex
@article{author2024model,
  title={Model Name},
  author={Author, A.},
  year={2024}
}
```

---

## CLI Tools

### Shell Integration

```bash
# Bash
eval "$(myapp init bash)"

# Zsh
eval "$(myapp init zsh)"

# Fish
myapp init fish | source
```

### Cross-Platform Installation Matrix

| Platform | Command |
|----------|---------|
| macOS (Homebrew) | `brew install myapp` |
| Linux (apt) | `sudo apt install myapp` |
| Windows (Scoop) | `scoop install myapp` |
| From source | `cargo install myapp` |

### Performance Benchmarks

| Tool | Time | Relative |
|------|------|----------|
| myapp | 0.082s | 1.00x |
| alternative1 | 0.273s | 3.34x |
| alternative2 | 0.443s | 5.43x |

Specify exact hardware, scenarios, and equivalent flags for fair comparison.

### Keybinding Reference

| Key | Action |
|-----|--------|
| `space` | Stage selected line |
| `CTRL-R` | Search history |

### Configuration Example

```toml
# ~/.config/myapp/config
--theme="TwoDark"
--style="numbers,changes,header"
```

---

## Libraries

### API Reference Table

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `process()` | `data: str` | `Result` | Process input data |
| `configure()` | `options: dict` | `None` | Set configuration |

### Quick Example

```python
from mylib import Thing

thing = Thing()
result = thing.process(data)
```

---

## Web Apps

### Live Demo Link

Place prominently after hero section.

### Environment Variables Table

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Database connection string |
| `API_KEY` | Yes | External API key |

### Docker Quick Start

```bash
docker run -p 3000:3000 myapp
```
