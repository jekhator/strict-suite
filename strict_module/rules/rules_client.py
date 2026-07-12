"""Rule registry for linting rules."""

from typing import Optional

from strict_module.rules.rules_objects import Rule, RuleSeverity


class RuleRegistry:
    """Registry of all linting rules."""

    RULES = {
        "R001": Rule(
            "R001",
            "Dict[str, Any] or bare collections in service signatures",
            RuleSeverity.HIGH,
            "Function signature contains Dict[str, Any], bare dict, list, or tuple without type parameters.",
        ),
        "R002": Rule(
            "R002",
            "Inline dict literals with 3+ keys",
            RuleSeverity.MEDIUM,
            "Inline dict literal with multiple string keys; consider converting to DTO.",
        ),
        "R003": Rule(
            "R003",
            "Dataclass uses anti-canonical repr=False",
            RuleSeverity.MEDIUM,
            "Dataclass uses anti-canonical repr=False. Per strict-module canonical (v0.2): plain @dataclass(frozen=True, slots=True). Remove repr=False.",
        ),
        "R004": Rule(
            "R004",
            "Module-level function without exception tag",
            RuleSeverity.HIGH,
            "Module-level function definition lacks documented exception tag (facade pattern).",
        ),
        "R005": Rule(
            "R005",
            "Validator not using DTO.from_dict() pattern",
            RuleSeverity.LOW,
            "Validator function should use DTO.from_dict() to validate payload shape.",
        ),
        "R006": Rule(
            "R006",
            "typing.Any in signature",
            RuleSeverity.HIGH,
            "Function signature contains typing.Any in parameter or return type. Use forward refs (TYPE_CHECKING) for class types, narrow protocols (IO[bytes]) for file objects, or build a proper DTO for business shapes.",
        ),
        "R007": Rule(
            "R007",
            "Pytest fixtures defined outside conftest.py",
            RuleSeverity.MEDIUM,
            "Pytest fixture @pytest.fixture decorator found in non-conftest file. Fixtures must be defined in conftest.py.",
        ),
        "R008": Rule(
            "R008",
            "Bare module-level test function",
            RuleSeverity.MEDIUM,
            "Module-level test function def test_*() found. Test functions must be defined as methods in Test<Concern> classes.",
        ),
    }

    @classmethod
    def get_rule(cls, rule_id: str) -> Optional[Rule]:
        """Get rule by ID."""
        return cls.RULES.get(rule_id)
