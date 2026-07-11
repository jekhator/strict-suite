"""Tests for GitHub format output."""

from strict_module.rules import Violation, RuleSeverity


class TestGithubFormat:
    """Test suite for related functionality."""

    def test_github_format_error(self):
        """Test GitHub format for HIGH severity."""
        violation = Violation(
            rule_id="R001",
            severity=RuleSeverity.HIGH,
            file="app.py",
            line=10,
            col=5,
            message="Dict[str, Any] in signature: process_user",
        )

        output = violation.format_github()
        assert "::error" in output
        assert "file=app.py" in output
        assert "line=10" in output

    def test_github_format_warning(self):
        """Test GitHub format for MEDIUM severity."""
        violation = Violation(
            rule_id="R002",
            severity=RuleSeverity.MEDIUM,
            file="service.py",
            line=20,
            col=0,
            message="Inline dict literal with 4 keys",
        )

        output = violation.format_github()
        assert "::warning" in output
        assert "file=service.py" in output

    def test_github_format_notice(self):
        """Test GitHub format for LOW severity."""
        violation = Violation(
            rule_id="R005",
            severity=RuleSeverity.LOW,
            file="validator.py",
            line=15,
            col=0,
            message="Validator does not use DTO.from_dict()",
        )

        output = violation.format_github()
        assert "::notice" in output or "::warning" in output  # LOW may be notice or warning

    def test_text_format(self):
        """Test text format output."""
        violation = Violation(
            rule_id="R001",
            severity=RuleSeverity.HIGH,
            file="app.py",
            line=10,
            col=5,
            message="Dict[str, Any] in signature: process_user",
        )

        output = violation.format_text()
        assert "app.py:10:" in output
        assert "R001" in output
        assert "Dict[str, Any]" in output
