"""Tests for the strict_config package exports."""

import strict_config
from strict_config import constants as const


class TestPackageExports:
    """The strict_config namespace declares a sorted public surface and keeps the constants reachable."""

    def test_all_is_sorted_and_lists_the_public_names(self):
        """__all__ is sorted and names exactly the classes and the version."""
        assert strict_config.__all__ == sorted(strict_config.__all__)
        assert strict_config.__all__ == ["Config", "LocCapConfig", "__version__"]

    def test_constants_remain_reachable_as_attributes(self):
        """Constants re-exported by name are the same objects as in the constants module."""
        assert strict_config.DEFAULT_LOC_HARD_CAP is const.DEFAULT_LOC_HARD_CAP
        assert strict_config.ERR_SOURCE_SYNTAX is const.ERR_SOURCE_SYNTAX
        assert strict_config.TAG_MODULE_LEVEL == "module-level:"

    def test_removed_constant_is_not_exported(self):
        """DICT_STR_ANY_PATTERN was removed and is not exported."""
        assert not hasattr(strict_config, "DICT_STR_ANY_PATTERN")
        assert not hasattr(const, "DICT_STR_ANY_PATTERN")
