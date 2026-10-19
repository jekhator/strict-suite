# Contributing

Issues and pull requests welcome. Please include fixtures (good and bad examples) for new rules.

## Development Setup

The project is managed with [uv](https://docs.astral.sh/uv/). The CI matrix runs Python 3.12 and 3.14.

```bash
git clone https://github.com/jekhator/strict-suite.git
cd strict-suite
uv sync --all-extras
```

## Running Tests

Tests live under `strict_checkers/tests/` (the pytest `testpaths`). Fixture files used by the rule tests live under `strict_checkers/tests/fixtures/`.

```bash
uv run pytest -v --cov --cov-fail-under=95
```

## Checks Before Submitting

The same gates run in CI. Run them from the repository root.

1. Tests and coverage: `uv run pytest -v --cov --cov-fail-under=95`
2. Type check: `uv run mypy strict_checkers/ strict_config/ strict_inspection/ strict_linter/ strict_loc_cap/ strict_rules/ strict_module/`
3. Lint: `uvx ruff@0.15.14 check strict_checkers/ strict_config/ strict_inspection/ strict_linter/ strict_loc_cap/ strict_rules/ strict_module/`
4. Format check (the carved-out files are listed in `pyproject.toml` and `.github/workflows/ruff.yml`): `uvx ruff@0.15.14 format --check strict_module/`
5. Self-lint: `uv run --python 3.12 python -m strict_module.cli $(find strict_checkers strict_config strict_inspection strict_linter strict_loc_cap strict_rules strict_module -name "*.py" ! -path "*/tests/*" ! -path "*/fixtures/*" | sort) --format github`
6. Add an entry under the `[Unreleased]` section of `CHANGELOG.md` for every user-visible change.

Commit messages must not carry attribution or sign-off lines beyond the author; the attribution workflow rejects them.

## License

All contributions are licensed under the Apache License 2.0. See LICENSE for details.
