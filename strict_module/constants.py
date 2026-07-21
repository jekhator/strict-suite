"""Configuration constants and magic strings for strict-module."""

FORMAT_TEXT = "text"
FORMAT_GITHUB = "github"
FORMAT_JSON = "json"
VALID_FORMATS = [FORMAT_TEXT, FORMAT_GITHUB, FORMAT_JSON]

GITHUB_LEVEL_ERROR = "error"
GITHUB_LEVEL_NOTICE = "notice"
GITHUB_LEVEL_WARNING = "warning"

EXIT_CODE_SUCCESS = 0
EXIT_CODE_HIGH_VIOLATION = 1
EXIT_CODE_MEDIUM_VIOLATION = 2
EXIT_CODE_LOW_VIOLATION = 3

VALID_SEVERITY_LEVELS = ["HIGH", "MEDIUM", "LOW", "INFO"]

DEFAULT_LOC_HARD_CAP = 694
DEFAULT_LOC_SOFT_TARGET = 500
DEFAULT_LOC_CAP_BASELINE_FILE = ".loc-cap-baseline.txt"

DEFAULT_MIN_DICT_KEYS = 3
DEFAULT_R003_MODE = "canonical"
DEFAULT_EXCEPTION_TAGS = ["facade - celery schedule", "FRAMEWORK"]
DEFAULT_SERVICE_PATHS = ["apps/*/services/*.py", "**/services/*.py"]
DEFAULT_DTO_PATHS = ["**/dtos.py", "**/dtos/*.py"]
DEFAULT_R006_PATHS = ["apps/*/services/*.py", "**/services/*.py"]

CONFIG_SECTION_STRICT_MODULE = "strict-module"
CONFIG_SECTION_DTO_STRICT = "dto-strict"
CONFIG_SECTION_LOC_CAP = "loc-cap"

NOQA_KEYWORD = "noqa"
PREFIX_STRICT_MODULE = "strict-module"
PREFIX_DTO_STRICT = "dto-strict"

PY_EXTENSION = ".py"
BASENAME_CONSTANTS = "constants.py"
BASENAME_CONST_SUFFIX = "_const.py"
LOC_CAP_BASELINE_LEGACY_NAMES = [
    ".strict-module-baseline.txt",
    ".dto-strict-baseline.txt",
]

DEFAULT_EXCLUDE_PATTERNS = ("migrations", "management/commands")

BARE_COLLECTION_TYPES = ("dict", "list", "tuple")

DICT_STR_ANY_PATTERN = "dict[str,any]"
