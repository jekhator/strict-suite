# Contributing

Issues and pull requests welcome. Please include fixtures (good and bad examples) for new rules.

When submitting a fix or feature:

1. Ensure all tests pass: `python3.12 -m pytest tests/ -q`
2. Format code: `ruff format strict_module/ tests/`
3. Lint code: `ruff check strict_module/ tests/` and `strict-module strict_module/`
4. Update CHANGELOG.md with your changes under an [Unreleased] section

## Development Setup

```bash
git clone https://github.com/jekhator/strict-module.git
cd strict-module
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
