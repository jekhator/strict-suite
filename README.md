# strict-suite

[![PyPI](https://img.shields.io/pypi/v/strict-suite.svg?style=flat)](https://pypi.org/project/strict-suite/)
[![CI](https://github.com/jekhator/strict-suite/workflows/CI/badge.svg)](https://github.com/jekhator/strict-suite/actions)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

AST-based linter for Python DTO discipline and facade-ban enforcement. Consolidated strict Python linting and static analysis tools with complexity metrics.

**Consolidated from strict-module 0.5.0.** This monorepo consolidates the strict-module package and related linting infrastructure. Backward-compatible CLI entry points (`strict-module` and `dto-strict`) are preserved.

> **Python only.** The strict-component (npm/TypeScript) stays in its own repo. This distribution is Python 3.11+ only.

## Overview

Data Transfer Objects (DTOs) and facade discipline are critical for clean API boundaries, especially in regulated environments (healthcare, compliance, financial systems). **stricts** enforces these patterns via static AST analysis, with 6 focused rules:

1. **R001 (HIGH)**: Detect `Dict[str, Any]` or bare `dict`/`list`/`tuple` in service-layer function signatures.
2. **R002 (MEDIUM)**: Flag inline dict literals with 3+ string keys; exception tags can require justification.
3. **R003 (MEDIUM)**: Flag `repr=False` in dataclasses (canonical: plain `@dataclass(frozen=True, slots=True)`).
4. **R004 (HIGH)**: Demand exception tags on module-level functions (e.g., `# facade - celery schedule`).
5. **R005 (LOW)**: Encourage validators to use `DTO.from_dict()` pattern.
6. **R006 (HIGH)**: Detect `typing.Any` in function signatures (parameters and return types).

All rules are configurable; violations can be disabled, severity overridden, or paths scoped.

## Install

```bash
pip install strict-suite
```

Or with optional development dependencies:

```bash
pip install strict-suite[dev]
```

Both CLI entry points (strict-module and dto-strict) are available post-install.

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

Create a test file `example.py` with conformant code:

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class UserDTO:
    """User data transfer object."""
    user_id: int
    email: str

class UserService:
    """Service to process users."""

    def process_user(self, user: UserDTO) -> None:
        """Process a user."""
        print(f"Processing {user.email}")
```

Then lint it:

```bash
$ strict-module example.py
# (no output = clean)
```

Now create a violating example. Save this as `apps/test/services/bad_user.py`:

```python
from typing import Any

class UserService:
    def process_user(self, config: dict[str, Any]) -> None:  # R001: Dict[str, Any] in signature
        """Process a user."""
        return config.get("user_id")
```

Running the linter (from the repo root):

```bash
$ strict-module apps/test/services/bad_user.py
apps/test/services/bad_user.py:4: R001 Dict[str, Any] in signature: process_user
apps/test/services/bad_user.py:4: R006 typing.Any in parameter: process_user
```

### All Rules Demonstrated

**R002** (inline dict literals with 3+ keys):
```python
# violation
def example():
    data = {"key1": "val1", "key2": "val2", "key3": "val3"}
```

**R003** (anti-canonical repr=False on dataclass):
```python
# violation
from dataclasses import dataclass

@dataclass(repr=False)
class MyDTO:
    value: int
```

**R004** (module-level function without exception tag):
```python
# violation (in a non-conftest file)
def process_data(item):
    return item["id"]
```

**R007** (pytest fixtures outside conftest.py):
```python
# violation
import pytest

@pytest.fixture
def my_fixture():
    return "value"
```

**R008** (bare module-level test functions):
```python
# violation
def test_something():
    assert True
```

### LOC Cap Enforcement

Check lines-of-code limits:

```bash
$ strict-module loc-cap src/
src/long_module.py: soft-target 500 exceeded (523 lines)
src/another.py: hard-cap 694 exceeded (750 lines) FAIL
```

Generate baseline:

```bash
$ strict-module loc-cap src/ --generate-baseline > .loc-cap-baseline.txt
```

### Using Both CLI Entry Points

Both `strict-module` and `dto-strict` are equivalent aliases:

```bash
strict-module apps/
dto-strict apps/
```

## Configuration

Configuration lives in `pyproject.toml`:

```toml
[tool.strict-module]
service_paths = ["apps/*/services/*.py", "**/services/*.py"]
dto_paths = ["**/dtos.py", "**/dtos/*.py"]
exception_tags = [
    "facade - celery schedule",
    "FRAMEWORK",
    "aws-boundary"
]
disabled_rules = []
severity_overrides = {}
```

- **service_paths**: Glob patterns for files to lint with R001 (strict mode).
- **dto_paths**: Glob patterns for files expected to contain DTO definitions.
- **exception_tags**: Recognized justification tags for module-level functions (R004 and R009). Example: `aws-boundary` exempts a function from the module-level function rules.
- **disabled_rules**: List of rule IDs to disable (e.g., ["R005"]).
- **severity_overrides**: Dict mapping rule IDs to override severity (e.g., {"R002": "HIGH", "R011": "INFO"}).

Backward compatibility: `[tool.strict-module]` config and `.strict-module-baseline.json` baseline files are supported.

### Suppressing Violations

Use `# noqa` comments to suppress violations on specific lines. Supported forms:

- **Bare `# noqa`**: Suppress any rule on that line.
  ```python
  x = {1: 2, 3: 4, 5: 6}  # noqa
  ```

- **Rule-specific `# noqa: R006`**: Suppress a single rule by ID.
  ```python
  def process(x: Any) -> None:  # noqa: R006
      pass
  ```

- **Namespaced `# noqa: strict-module-R006`**: Use the ruff-external-friendly namespaced form (recommended when running ruff alongside).
  ```python
  def process(x: Any) -> None:  # noqa: strict-module-R006
      pass
  ```

- **Multiple rules `# noqa: R006, R011`**: Suppress multiple rules on one line.
  ```python
  def process(x: Any) -> None:  # noqa: R006, R011
      pass
  ```

When using ruff in parallel, declare `[tool.ruff.lint] external = ["strict-module"]` in `pyproject.toml` to prevent ruff from warning on the external rule codes.

## Public API

The package exports the following public symbols:

- **`__version__`**: Package version string (e.g., "0.1.0")
- **`DtoStrictLinter`**: Main linter class for running AST analysis
- **`Rule`**: Rule definition dataclass
- **`RuleSeverity`**: Enum for rule severity levels (HIGH, MEDIUM, LOW)

Example usage:

```python
from strict_module import DtoStrictLinter, Rule, RuleSeverity, __version__

print(f"strict-suite {__version__}")

linter = DtoStrictLinter()
violations = linter.lint_file("mymodule.py")
for v in violations:
    print(f"{v.rule_id} ({v.severity.value}): {v.message}")
```

## Documentation

Full documentation, including rule details, configuration options, and integration guides, is available in the `docs/` directory.

Historical changelog: see `CHANGELOG-history.md` for strict-module v0.1.0 through v0.5.0 release history.

## Development

Install dev dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
python3.12 -m pytest strict_module/tests/ -v
```

Run the self-lint check:

```bash
strict-module strict_module/ --format text
dto-strict strict_module/
```

Run format and style checks:

```bash
ruff check strict_module/
ruff format --check strict_module/
```

Run LOC cap check:

```bash
strict-module loc-cap strict_module/
```

## License

Apache License 2.0. See [LICENSE](LICENSE) for full text.

## Contributing

Contributions are welcome. Please ensure:

- All tests pass.
- Code follows the project's linting rules (run `strict-module` on your changes).
- Commit messages are clear and describe the change.
- No AI attribution in commit messages.
