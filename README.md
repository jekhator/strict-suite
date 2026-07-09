# stricts

[![PyPI](https://img.shields.io/pypi/v/stricts.svg?style=flat)](https://pypi.org/project/stricts/)
[![CI](https://github.com/jekhator/stricts/workflows/CI/badge.svg)](https://github.com/jekhator/stricts/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

Consolidated strict Python linting and static analysis tools. AST-based DTO discipline, facade-ban enforcement, and complexity metrics.

**Consolidated from strict-module 0.5.0.** This monorepo consolidates the strict-module package and related linting infrastructure. Backward-compatible CLI entry points (`strict-module` and `dto-strict`) are preserved.

> **Python only.** The strict-component (npm/TypeScript) stays in its own repo. This distribution is Python 3.10+ only.

## Overview

Data Transfer Objects (DTOs) and facade discipline are critical for clean API boundaries, especially in regulated environments (healthcare, compliance, financial systems). **stricts** enforces these patterns via static AST analysis, with 6 focused rules:

1. **R001 (HIGH)**: Detect `Dict[str, Any]` or bare `dict`/`list`/`tuple` in service-layer function signatures.
2. **R002 (MEDIUM)**: Flag inline dict literals with 3+ string keys; exception tags can require justification.
3. **R003 (MEDIUM)**: Flag `repr=False` in dataclasses (canonical: plain `@dataclass(frozen=True, slots=True)`).
4. **R004 (HIGH)**: Demand exception tags on module-level functions (e.g., `# facade — celery schedule`).
5. **R005 (LOW)**: Encourage validators to use `DTO.from_dict()` pattern.
6. **R006 (HIGH)**: Detect `typing.Any` in function signatures (parameters and return types).

All rules are configurable; violations can be disabled, severity overridden, or paths scoped.

## Install

```bash
pip install stricts
```

Or with pip+uvx for testing:

```bash
uvx strict-module --help
```

## Quick Start

### Basic CLI Usage

```bash
# Lint a single file
strict-module apps/compliance/services.py

# Lint a directory
strict-module apps/

# Output as GitHub Actions annotations
strict-module apps/ --format github

# Output as JSON
strict-module apps/ --format json

# Use the compat alias
dto-strict apps/
```

### Run-Verified Example

Create a test file `example.py` with a conformant DTO:

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class UserDTO:
    """User data transfer object."""
    user_id: int
    email: str

def process_user(user: UserDTO) -> None:
    """Process a user."""
    print(f"Processing {user.email}")
```

Then lint it:

```bash
$ strict-module example.py
# (no output = clean)
```

Now create a violating example `bad_example.py`:

```python
from typing import Any

def process_user(config: dict[str, Any]) -> None:  # R001: Dict[str, Any] in signature
    """Process a user."""
    return config.get("user_id")
```

Running the linter:

```bash
$ strict-module bad_example.py
bad_example.py:3: R001 (HIGH): Dict[str, Any] detected in service method signature (line 3, column 38)
```

## Configuration

Configuration lives in `pyproject.toml`:

```toml
[tool.strict-module]
service_paths = ["apps/*/services/*.py", "**/services/*.py"]
dto_paths = ["**/dtos.py", "**/dtos/*.py"]
exception_tags = [
    "facade — celery schedule",
    "FRAMEWORK"
]
disabled_rules = []
severity_overrides = {}
```

- **service_paths**: Glob patterns for files to lint with R001 (strict mode).
- **dto_paths**: Glob patterns for files expected to contain DTO definitions.
- **exception_tags**: Recognized justification tags for module-level functions (R004).
- **disabled_rules**: List of rule IDs to disable (e.g., ["R005"]).
- **severity_overrides**: Dict mapping rule IDs to override severity (e.g., {"R002": "HIGH"}).

Backward compatibility: `[tool.strict-module]` config and `.strict-module-baseline.json` baseline files are supported.

## Documentation

Full documentation, including rule details, configuration options, and integration guides, is available in the `docs/` directory.

Historical changelog: see `CHANGELOG-history.md` for strict-module v0.1.0–v0.5.0 release history.

## Development

Install dev dependencies:

```bash
pip install -e .[dev]
```

Run tests:

```bash
pytest tests/ -v
```

Run the self-lint check:

```bash
strict-module strict_module/ --format github
```

Run ruff checks:

```bash
ruff check strict_module/
ruff format --check strict_module/
```

## License

Apache License 2.0. See [LICENSE](LICENSE) for full text.

## Contributing

Contributions are welcome. Please ensure:

- All tests pass.
- Code follows the project's linting rules (run `strict-module` on your changes).
- Commit messages are clear and describe the change.
- No AI attribution in commit messages.
