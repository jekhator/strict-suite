"""Adversarial fixtures for R013-R015 - parameterized for calibration boundaries.

This module contains deliberately-violating code patterns for R013, R014, R015.
Thresholds are parameterized so tests will work once canonical calibration
answers land from P14/P15/P16 review.

DO NOT MODIFY THRESHOLDS - they update once calibration boundaries are received.
"""

import pytest


class TestR013AdvPsersial:
    """R013 adversarial fixtures: signature grouping violations.

    CALIBRATION PENDING: These tests are fixtures for when R013 is activated.
    Current state: R013 is disabled. Once calibration boundaries are set,
    update PARAM_R013_SINGLE_PARAM_THRESHOLD and expectations below.
    """

    # Calibration parameter: will be set by coordinator
    PARAM_R013_SINGLE_PARAM_THRESHOLD = None  # e.g., 3 or 4

    @pytest.mark.skip(reason="R013 pending calibration activation")
    def test_r013_short_all_one_per_line_violates(self):
        """Short signature with all params one-per-line should violate R013."""
        # This test will activate once PARAM_R013_SINGLE_PARAM_THRESHOLD is set
        if self.PARAM_R013_SINGLE_PARAM_THRESHOLD is None:
            pytest.skip("Awaiting R013 calibration")

        source = f"""
def func(
    self, x: int,
    y: int,
    z: int,
) -> None:
    pass
"""
        # When R013 is enabled with threshold >= 3:
        # EXPECT 1 violation at signature start

    @pytest.mark.skip(reason="R013 pending calibration activation")
    def test_r013_long_one_per_line_allowed(self):
        """Long signature with one-per-line is allowed."""
        if self.PARAM_R013_SINGLE_PARAM_THRESHOLD is None:
            pytest.skip("Awaiting R013 calibration")

        source = """
def func(
    self, a: int,
    b: int,
    c: int,
    d: int,
    e: int,
) -> None:
    pass
"""
        # When R013 is enabled:
        # EXPECT 0 violations (long signature, allowed)

    @pytest.mark.skip(reason="R013 pending calibration activation")
    def test_r013_grouped_params_allowed(self):
        """Grouped params should not violate."""
        if self.PARAM_R013_SINGLE_PARAM_THRESHOLD is None:
            pytest.skip("Awaiting R013 calibration")

        source = """
def func(
    self, x: int, y: int,
    z: int,
) -> None:
    pass
"""
        # When R013 is enabled:
        # EXPECT 0 violations (params are grouped)


class TestR014AdvPsersial:
    """R014 adversarial fixtures: kwarg call grouping violations.

    CALIBRATION PENDING: These tests are fixtures for when R014 is activated.
    Current state: R014 is disabled. Once calibration boundaries are set,
    update PARAM_R014_KWARG_THRESHOLD and expectations below.
    """

    # Calibration parameter: will be set by coordinator
    PARAM_R014_KWARG_THRESHOLD = None  # e.g., 2 or 3

    @pytest.mark.skip(reason="R014 pending calibration activation")
    def test_r014_two_kwargs_one_per_line_violates(self):
        """Two kwargs each on separate line should violate R014."""
        if self.PARAM_R014_KWARG_THRESHOLD is None:
            pytest.skip("Awaiting R014 calibration")

        source = """
func(
    x=1,
    y=2,
)
"""
        # When R014 is enabled with threshold >= 2:
        # EXPECT 1 violation

    @pytest.mark.skip(reason="R014 pending calibration activation")
    def test_r014_three_kwargs_one_per_line_allowed(self):
        """Three kwargs one-per-line is allowed (intentional vertical)."""
        if self.PARAM_R014_KWARG_THRESHOLD is None:
            pytest.skip("Awaiting R014 calibration")

        source = """
func(
    x=1,
    y=2,
    z=3,
)
"""
        # When R014 is enabled:
        # EXPECT 0 violations (intentional vertical for 3+)

    @pytest.mark.skip(reason="R014 pending calibration activation")
    def test_r014_grouped_kwargs_allowed(self):
        """Grouped kwargs should not violate."""
        if self.PARAM_R014_KWARG_THRESHOLD is None:
            pytest.skip("Awaiting R014 calibration")

        source = """
func(
    x=1, y=2,
)
"""
        # When R014 is enabled:
        # EXPECT 0 violations (grouped on one line)


class TestR015AdvPsersial:
    """R015 adversarial fixtures: wrap-path blank-line rhythm violations.

    CALIBRATION PENDING: These tests are fixtures for when R015 is activated.
    Current state: R015 is disabled. Once calibration boundaries are set,
    update PARAM_R015_STATEMENT_DIFF_THRESHOLD and expectations below.
    """

    # Calibration parameter: will be set by coordinator
    PARAM_R015_STATEMENT_DIFF_THRESHOLD = None  # e.g., 3, 5, or "unlimited"

    @pytest.mark.skip(reason="R015 pending calibration activation")
    def test_r015_asymmetric_structure_violates(self):
        """Try/except with very asymmetric structure should violate R015."""
        if self.PARAM_R015_STATEMENT_DIFF_THRESHOLD is None:
            pytest.skip("Awaiting R015 calibration")

        source = """
try:
    result = call()
    x = process1()
    y = process2()
    z = process3()
    w = process4()
except Exception:
    handle()
"""
        # When R015 is enabled (try=5, except=1, diff=4):
        # EXPECT 1 violation if THRESHOLD < 4

    @pytest.mark.skip(reason="R015 pending calibration activation")
    def test_r015_symmetric_structure_allowed(self):
        """Try/except with matching structure is allowed."""
        if self.PARAM_R015_STATEMENT_DIFF_THRESHOLD is None:
            pytest.skip("Awaiting R015 calibration")

        source = """
try:
    x = foo()
    y = bar()
except Exception:
    x = foo_fail()
    y = bar_fail()
"""
        # When R015 is enabled:
        # EXPECT 0 violations (symmetric structure)

    @pytest.mark.skip(reason="R015 pending calibration activation")
    def test_r015_reasonable_asymmetry_allowed(self):
        """Try/except with reasonable asymmetry (result assignment) allowed."""
        if self.PARAM_R015_STATEMENT_DIFF_THRESHOLD is None:
            pytest.skip("Awaiting R015 calibration")

        source = """
try:
    result = call()
    process(result)
except Exception:
    process(None)
"""
        # When R015 is enabled:
        # EXPECT 0 violations if THRESHOLD >= 1 (except has 1 fewer stmt)


# --- INSTRUCTIONS FOR CALIBRATION ACTIVATION ---
#
# When P14/P15/P16 canonical answers arrive:
#
# 1. Coordinator sends calibration boundaries for each rule
# 2. Update the PARAM_* values above with exact thresholds
# 3. Remove @pytest.mark.skip from test methods you want to activate
# 4. Update EXPECT comments to reflect actual test outcome
# 5. Re-enable R013/R014/R015 implementations in strict_checkers/
# 6. Run: pytest strict_checkers/tests/test_r013_r014_r015_adversarial_fixtures.py -v
# 7. All tests must pass with exact violation counts matching EXPECT
#
# Do NOT modify test structure - only thresholds and skip markers.
