# Contributing

Issues and pull requests welcome. Please include fixtures (good and bad examples) for new rules.

When submitting a fix or feature:

1. Ensure all tests pass: `python3.12 -m pytest strict_module/tests/ -v --tb=short`
2. Format code: `ruff format strict_module/`
3. Lint code: `ruff check strict_module/` and `strict-module strict_module/`
4. Check LOC caps: `strict-module loc-cap strict_module/`
5. Update CHANGELOG.md with your changes under an [Unreleased] section

## Development Setup

```bash
git clone https://github.com/jekhator/strict-suite.git
cd strict-suite
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
python3.12 -m pytest tests/ -v
```

## License

All contributions are licensed under the Apache License 2.0. See LICENSE for details.
