# Optimization Pass Audit: 2026-10-19

This audit records the optimization pass over the linter source and its test tree. Each source module was reviewed for correctness (latent defects, swallowed exceptions, substring matching, version-specific APIs), dead or duplicated code, control-flow shape, typing precision, literal placement, naming, and per-file performance on the AST walk. The source table lists each reviewed file with the number of findings, whether the file changed in this pass, and a note on the outcome. Findings that were not acted on are recorded in the note with the reason. The test-tree table below covers every Python file under `strict_checkers/tests/`, including the fixtures. Behaviour changes made by the pass are listed under Behavior Changes and in the changelog under 0.6.0.

Source files that only re-export names (package `__init__.py` files) were reviewed; the ones that changed are marked in the table.

| path | findings | changed | note |
|------|----------|---------|------|
| strict_checkers/__init__.py | 0 | no | Re-export surface unchanged. |
| strict_checkers/base.py | 3 | yes | Added shared helpers for violation construction, exception tags (def line and first docstring line, case-insensitive), dataclass decorator, and pytest fixture decorator; removed per-checker copies. |
| strict_checkers/r001.py | 2 | yes | Five copies of the same violation block replaced by one loop over the signature annotations; first-hit and early-return behaviour kept. |
| strict_checkers/r002.py | 3 | yes | Removed a per-class tree re-walk (about 28 percent of lint time in the profiled consumer run); restored the function context after leaving a function (a tag on an earlier function no longer excuses a later dict literal); removed a duplicate attribute assignment. |
| strict_checkers/r003.py | 3 | yes | Removed a read of the legacy node class that Python 3.14 no longer provides (reachable on bare-name keyword values); shared the dataclass decorator check; collapsed calls that the formatting rules flagged as split. |
| strict_checkers/r004.py | 1 | yes | Rewritten to the facade shape: a module-level function whose body only delegates to a class method, with a shared exception-tag check. |
| strict_checkers/r005.py | 1 | yes | Violation construction moved to the shared helper; logic unchanged. |
| strict_checkers/r006.py | 2 | yes | Duplicated per-argument blocks replaced by one labelled loop; annotation matching now by name (see inspection module). |
| strict_checkers/r007.py | 2 | yes | Fixture detection shared with the base class; one violation per fixture function instead of one per fixture decorator; suppression check runs once. |
| strict_checkers/r008.py | 1 | yes | Violation construction moved to the shared helper; logic unchanged. |
| strict_checkers/r009.py | 2 | yes | Rewritten as an advisory rule with decorator, dunder and pytest hook, and recorded-reason exemptions; the former fixture-only helpers are replaced by the decorator check. |
| strict_checkers/r010.py | 1 | yes | Suppression check moved out of the per-alias loop; the legacy-name table is a module constant. |
| strict_checkers/r011.py | 3 | yes | Constants-module exemption matches the file name or a constants directory, not any path substring (a substring match exempted unrelated paths); the generic-visit branches collapsed to one exit. |
| strict_checkers/r012.py | 2 | yes | Removed two broad exception handlers that silently discarded results; the early-return chain collapsed to one predicate; line limit named as a constant. |
| strict_checkers/r013.py | 3 | yes | Duplicate async and sync visitor bodies share one check; removed unnecessary type-ignore comments; the grouping uses a defaultdict. |
| strict_checkers/r014.py | 3 | yes | Removed unused parameters from the log-event checks; removed unnecessary type-ignore comments; line limit named as a constant. |
| strict_checkers/r015.py | 2 | yes | Removed an unused parameter; the timing-capture check keeps the bare round builtin as the only latency calculation, as before, with the perf-counter and round checks separate. |
| strict_config/__init__.py | 1 | yes | Wildcard re-export of the constants module replaced by explicit imports; the exported names and the sorted `__all__` are unchanged (checked by name). |
| strict_config/_config.py | 3 | yes | Malformed or unreadable configuration now raises a typed error naming the path (it previously returned defaults silently); non-table sections are rejected; default lists are copied so loaded configs cannot alter shared constants. |
| strict_config/_version.py | 0 | yes | Version 0.6.0. |
| strict_config/constants.py | 2 | yes | Added the module-level exception tag, named tag constants and the configuration error message. The default tag is now the written form `module-level:`. Added the source and loc-cap error messages. The unused path-pattern constant was removed (CHANGELOG, Removed). |
| strict_inspection/__init__.py | 0 | no | Re-export surface unchanged. |
| strict_inspection/annotations_client.py | 4 | yes | Annotation matching by name instead of substring (a substring match flagged identifiers such as Company and missed qualified typing.Any); removed a Python 3.8 compatibility branch that the 3.12 floor does not need; the en dash and em dash characters inside the noqa parser are written as escapes. |
| strict_inspection/paths_client.py | 1 | yes | Service-path and DTO-path matching share one helper. |
| strict_linter/__init__.py | 0 | yes | Exports `LintInputError` (added). |
| strict_linter/linter_client.py | 4 | yes | Disabled-rule and baseline filters were applied twice per path; now applied once. The checker list is a module constant instead of a list built per file. The exit-code mapping is a severity table. Unused attribute removed. Decision applied: an unreadable or unparseable file now raises `LintInputError`; the CLI prints it to stderr and exits 1 instead of skipping the file. |
| strict_linter/linter_objects.py | 0 | yes | Added `LintInputError` for an unreadable or unparseable source file. |
| strict_loc_cap/__init__.py | 0 | no | Re-export surface unchanged. |
| strict_loc_cap/loc_cap_client.py | 3 | yes | Removed a printed reference to a document outside the public repository and made the refactor example generic. Decision applied: an unreadable counted file or an undecodable baseline now raises `LocCapInputError` (the CLI exits 1 with the error on stderr) instead of counting as zero lines or as an empty baseline. The success line starts with `OK:` instead of a check-mark glyph. |
| strict_loc_cap/loc_cap_objects.py | 1 | yes | Defaults taken from the constants module instead of repeated literals; added `LocCapInputError`. |
| strict_module/__init__.py | 0 | no | Re-export surface unchanged. |
| strict_module/cli.py | 4 | yes | Shared option builders for the two parsers; the linter is built once per run; a malformed configuration prints the error and exits with the blocking code; module-level helpers recorded with a reason. Decision applied: `_lint_all` converts `LintInputError` into a stderr error and exit 1 on both the lint and the baseline-generation paths. |
| strict_rules/__init__.py | 0 | no | Re-export surface unchanged. |
| strict_rules/rules_client.py | 2 | yes | Rule registry typed; Optional replaced with a union. Rule R004 and R009 entries updated to the new rules. |
| strict_rules/rules_objects.py | 0 | no | Severity and violation types unchanged. |

## Decisions Applied

These decisions were taken from the review of the first part of the pass and applied in this pass. Each one has a changelog line under 0.6.0 and a named test.

1. The default exception tag is `module-level:` (colon form). A docstring that only mentions the words as prose no longer exempts a function. Test: `test_r009_prose_docstring_does_not_exempt`, `test_r009_default_tag_is_the_colon_form`.
2. An unreadable or unparseable Python file, an unreadable counted file, and an undecodable loc-cap baseline are errors: the CLI prints the path and the reason to stderr and exits 1. Tests: `strict_checkers/tests/test_unreadable_inputs.py` (library and CLI paths, including `--generate-baseline`), `test_coverage_edge_cases.py`, `test_coverage_edge_cases_extended.py`, `test_loc_cap.py`.
3. `strict_config/__init__.py` names the constants explicitly. The exported names and `__all__` are unchanged. Test: `test_package_exports.py`.
4. `DICT_STR_ANY_PATTERN` is removed (CHANGELOG, Removed). Test: `test_removed_constant_is_not_exported`.
5. The loc-cap success line starts with `OK:`. Test: `test_run_loc_cap_success_line_is_ascii`.
6. `docs/strict_module/architecture/flow-trace.md` describes the fifteen shipped rules, the R004 facade shape and the R004 message, and the error paths. Its examples were re-run against the tree.

## Test Tree

Findings are counted with these lenses: class and method docstrings that are missing, multi-line or generic; determinism (chmod-based or machine-specific paths); weak assertions (length-only, exit-code sets, OR-combined alternatives, conditional checks); repeated default configuration setup; non-ASCII characters; exception bindings other than `error`; and strict-module rule findings that are not the purpose of a fixture. Findings before are counted on the tree at the start of the pass; findings after are counted on the tree at the end of the pass. Fixture purpose findings (for example the R010 findings in the R010 bad fixture) are not counted.

Test-tree summary: 77 files before the pass, 80 after (three added: `test_unreadable_inputs.py`, `test_package_exports.py` and the R009 prose fixture). 41 files changed. Findings before: 288. Findings after: 50, all listed under Deferred Candidates.

| path | findings before | findings after | changed | note |
|------|-----------------|----------------|---------|------|
| strict_checkers/tests/conftest.py | 0 | 0 | yes | Fixture docstrings list their users; dead temp_project and duplicate cli_project_dir removed; linter, error_prefix and run_cli fixtures added. |
| strict_checkers/tests/fixtures/bad/r001_bad_kwarg_bare_collection.py | 0 | 0 | no | Purpose unchanged; no findings. |
| strict_checkers/tests/fixtures/bad/r001_bad_kwarg_dict_str_any.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/fixtures/bad/r001_bad_param.py | 2 | 2 | no | Deferred: extra R009 INFO findings are not asserted by the test; kept to leave the fixture purpose unchanged. |
| strict_checkers/tests/fixtures/bad/r001_bad_return.py | 2 | 2 | no | Deferred: extra R009 INFO findings are not asserted by the test; kept to leave the fixture purpose unchanged. |
| strict_checkers/tests/fixtures/bad/r001_bad_vararg_bare_collection.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/fixtures/bad/r001_bad_vararg_dict_str_any.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/fixtures/bad/r002_bad_dict_max_tags_exceeded.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/fixtures/bad/r002_bad_dict_no_justification.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/fixtures/bad/r002_bad_inline.py | 2 | 2 | no | Deferred: extra R009 INFO findings are not asserted by the test; kept to leave the fixture purpose unchanged. |
| strict_checkers/tests/fixtures/bad/r002_bad_non_serializer.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/fixtures/bad/r003_bad_dataclass.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/fixtures/bad/r004_bad_facade.py | 4 | 4 | no | Deferred: extra R009 INFO findings are not asserted by the test; kept to leave the fixture purpose unchanged. |
| strict_checkers/tests/fixtures/bad/r005_bad_validator.py | 3 | 3 | no | Deferred: extra R009 INFO findings are not asserted by the test; the R005 findings are the purpose. |
| strict_checkers/tests/fixtures/bad/r006_bad_kwarg_any.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/fixtures/bad/r006_bad_vararg_any.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/fixtures/bad/r009_module_function_outside_entry_point.py | 0 | 0 | no | Deferred: the two R009 findings are the purpose; the test asserts exactly two. |
| strict_checkers/tests/fixtures/bad/r009_prose_docstring_not_a_tag.py | 0 | 0 | yes | Added in this pass: a docstring that mentions the tag as prose must not exempt the function (asserted by a named R009 test). |
| strict_checkers/tests/fixtures/bad/r010_legacy_typing_abc.py | 0 | 0 | no | Purpose unchanged: intentional R010 findings (the test asserts four). |
| strict_checkers/tests/fixtures/bad/r011_raise_literal_message.py | 2 | 2 | no | Deferred: extra R009 INFO findings are not asserted by the test; the R011 findings are the purpose. |
| strict_checkers/tests/fixtures/bad/test_r007_bad_fixtures.py | 0 | 0 | no | Purpose unchanged: intentional R007 and R008 findings. |
| strict_checkers/tests/fixtures/bad/test_r007_bare_fixture_decorator.py | 0 | 0 | no | Purpose unchanged: intentional R007 and R008 findings. |
| strict_checkers/tests/fixtures/bad/test_r007_fixture_with_call.py | 0 | 0 | no | Purpose unchanged: intentional R007 and R008 findings. |
| strict_checkers/tests/fixtures/bad/test_r008_bad_bare_test_functions.py | 0 | 0 | no | Purpose unchanged: intentional R008 findings. |
| strict_checkers/tests/fixtures/good/r001_good_basic.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/fixtures/good/r002_good_dict.py | 3 | 0 | yes | Module-level helpers tagged with a recorded reason; the good fixture is now clean. |
| strict_checkers/tests/fixtures/good/r002_good_serializer.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/fixtures/good/r002_multiple_dataclass_serializers.py | 0 | 0 | no | Method without docstring is fixture input and is not changed (method docstrings pending ruling); not counted. |
| strict_checkers/tests/fixtures/good/r003_good_dataclass.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/fixtures/good/r004_good_facade.py | 1 | 1 | no | Deferred: the test asserts that the untagged helper with logic is one R009 advisory; kept intentionally. |
| strict_checkers/tests/fixtures/good/r005_good_validator.py | 4 | 0 | yes | Raises go through constants (R011 was flagging them); helpers tagged; the good fixture is now clean. |
| strict_checkers/tests/fixtures/good/r009_allowed_entry_points.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/fixtures/good/r009_exempt_shapes.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/fixtures/good/r010_modern_abc_imports.py | 1 | 0 | yes | Module-level helper tagged in its docstring; the good fixture is now clean. |
| strict_checkers/tests/fixtures/good/r011_const_reference_raise.py | 5 | 0 | yes | Module-level helpers tagged with a recorded reason; the good fixture is now clean. |
| strict_checkers/tests/fixtures/good/test_r008_good_test_class.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/test_baseline_ratchet.py | 6 | 4 | yes | Length assertion tightened to the violation count; a TemporaryDirectory retained; three precondition guards kept (deferred). |
| strict_checkers/tests/test_cli.py | 6 | 4 | yes | Exit codes asserted exactly. Deferred: 4 R012 INFO findings on multi-line string arguments (checker false positive). |
| strict_checkers/tests/test_cli_main_entry.py | 9 | 7 | yes | Exit codes asserted exactly. Deferred: 7 R012 INFO findings on multi-line string arguments (checker false positive). |
| strict_checkers/tests/test_cli_malformed_config.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/test_cli_real_invocations.py | 10 | 0 | yes | Loose OR and length assertions replaced by exact expectations; alias fixture renamed to project_dir. Deferred: none; R012 not raised here. |
| strict_checkers/tests/test_compat_fallback.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/test_config_loading.py | 3 | 1 | yes | Config fixture used; absent-path literal kept (deterministic). |
| strict_checkers/tests/test_coverage_checkers_comprehensive.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/test_coverage_edge_cases.py | 7 | 1 | yes | Unparseable and missing inputs assert LintInputError through constants. Deferred: 1 R012 INFO finding on a multi-line string argument. |
| strict_checkers/tests/test_coverage_edge_cases_extended.py | 25 | 2 | yes | Chmod-based unreadable test replaced by a directory; dashes replaced by escapes; annotation strings asserted exactly; unused import removed. |
| strict_checkers/tests/test_coverage_negative_control.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/test_github_format.py | 1 | 0 | yes | Lens findings fixed in this pass. |
| strict_checkers/tests/test_loc_cap.py | 2 | 1 | yes | Unreadable counted file raises LocCapInputError through constants; success line asserted as the ASCII OK line. |
| strict_checkers/tests/test_loc_cap_test_exemption.py | 1 | 0 | yes | Lens findings fixed in this pass. |
| strict_checkers/tests/test_noqa.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/test_noqa_r002.py | 13 | 9 | yes | Em dashes replaced by escapes. Deferred: 9 R012 INFO findings on multi-line string arguments (checker false positive). |
| strict_checkers/tests/test_optimization_pass.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/test_package_exports.py | 0 | 0 | yes | Added in this pass: export surface and version-to-changelog lockstep tests. |
| strict_checkers/tests/test_r001_dict_str_any.py | 1 | 0 | yes | Lens findings fixed in this pass. |
| strict_checkers/tests/test_r001_strict_collections.py | 1 | 0 | yes | Lens findings fixed in this pass. |
| strict_checkers/tests/test_r002_annotated_constants.py | 2 | 0 | yes | Module and class docstrings made one line and specific. |
| strict_checkers/tests/test_r002_configurable_threshold.py | 1 | 0 | yes | Lens findings fixed in this pass. |
| strict_checkers/tests/test_r002_inline_dict.py | 1 | 0 | yes | Lens findings fixed in this pass. |
| strict_checkers/tests/test_r002_justification.py | 1 | 0 | yes | Lens findings fixed in this pass. |
| strict_checkers/tests/test_r002_multiple_dataclass_regression.py | 3 | 0 | yes | Multi-line test docstrings condensed to one line. |
| strict_checkers/tests/test_r002_serializer_exemption.py | 1 | 0 | yes | Lens findings fixed in this pass. |
| strict_checkers/tests/test_r002_tag_separator_format.py | 3 | 0 | yes | Em dash in assertions replaced by a Unicode escape. |
| strict_checkers/tests/test_r003_canonical.py | 1 | 0 | yes | Lens findings fixed in this pass. |
| strict_checkers/tests/test_r003_dataclass_trio.py | 1 | 0 | yes | Lens findings fixed in this pass. |
| strict_checkers/tests/test_r003_sensitivity_aware.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/test_r003_strict_relaxed.py | 1 | 0 | yes | Lens findings fixed in this pass. |
| strict_checkers/tests/test_r004_auto_detect.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/test_r004_module_facade.py | 0 | 0 | no | No findings. |
| strict_checkers/tests/test_r005_validator_pattern.py | 1 | 0 | yes | Lens findings fixed in this pass. |
| strict_checkers/tests/test_r006_any.py | 6 | 5 | yes | Deferred: 5 R012 INFO findings on multi-line string arguments (checker false positive). |
| strict_checkers/tests/test_r007_fixtures.py | 2 | 0 | yes | Multi-line test docstring condensed to one line. |
| strict_checkers/tests/test_r008_test_functions.py | 1 | 0 | yes | Lens findings fixed in this pass. |
| strict_checkers/tests/test_r009_module_functions.py | 8 | 0 | yes | Named tests added for the prose-docstring case and the colon form; linter fixture folded; exact count asserted. |
| strict_checkers/tests/test_r010_legacy_typing.py | 1 | 0 | yes | Lens findings fixed in this pass. |
| strict_checkers/tests/test_r011_raise_literals.py | 1 | 0 | yes | Lens findings fixed in this pass. |
| strict_checkers/tests/test_r012_r013_r014_r015.py | 131 | 0 | yes | Config fixture folded into 131 tests; two vacuous boundary tests replaced by real 79/80/81 character inputs; duplicate R013 test removed. |
| strict_checkers/tests/test_service_test_exemption.py | 3 | 0 | yes | Multi-line test docstrings condensed to one line. |
| strict_checkers/tests/test_suppression_surface.py | 5 | 0 | yes | Config and linter fixtures folded; loose OR assertion replaced. |
| strict_checkers/tests/test_unreadable_inputs.py | 0 | 0 | yes | Added in this pass: unreadable and unparseable inputs exit 1 with a stderr error (library and CLI paths). |

## Deferred Candidates

Each item below was found by the lenses above and was not changed in this pass. The reason is given for each.

1. **R012 false positives on multi-line string arguments (26 INFO findings).** `test_cli.py` (4), `test_cli_main_entry.py` (7), `test_coverage_edge_cases.py` (1), `test_noqa_r002.py` (9) and `test_r006_any.py` (5). Each finding is a single-argument call whose argument is a triple-quoted string spanning several lines, which cannot be written on one line. The fix belongs in the rule implementation (`strict_checkers/r012.py`), which is outside the test-tree pass. A per-line suppression was not added because it would hide the checker defect at 26 sites.
2. **Incidental R009 findings in bad fixtures (15 INFO findings).** `r001_bad_param.py` (2), `r001_bad_return.py` (2), `r002_bad_inline.py` (2), `r004_bad_facade.py` (4), `r005_bad_validator.py` (3) and `r011_raise_literal_message.py` (2). No test asserts these; they are advisory findings on module-level helpers in the fixtures. Removing them would change the fixture shape for no test benefit.
3. **One R009 advisory in a good fixture (`r004_good_facade.py`, `format_total`).** `test_r004_ignores_untagged_helper_with_logic` asserts it: the untagged helper with real logic is the case this fixture exists to show.
4. **Absent-path literals (5).** `/nonexistent/...` paths in `test_baseline_ratchet.py`, `test_config_loading.py`, `test_coverage_edge_cases_extended.py` (2) and `test_loc_cap.py`. The paths are absent by construction and the tests are deterministic; `tmp_path`-derived paths would be equally valid.
5. **Precondition guards (3).** `assert len(violations) > 0` in `test_baseline_ratchet.py`. Each is followed by exact assertions in the same test.
6. **Temporary directories instead of `tmp_path` (42 uses in 7 files).** `test_baseline_ratchet.py`, `test_compat_fallback.py`, `test_coverage_edge_cases_extended.py`, `test_noqa_r002.py`, `test_r007_fixtures.py`, `test_service_test_exemption.py` and `test_suppression_surface.py`. Each test is already isolated in its own directory; converting them is mechanical churn with no determinism defect.
7. **Method docstrings.** Not added or stripped (pending ruling). The `RegularClass.__init__` method in `fixtures/good/r002_multiple_dataclass_serializers.py` has no docstring; the fixture is linter input.
8. **Constants and `__all__`.** The constants re-exported by name from `strict_config` are reachable as attributes but are not listed in `__all__`, as before this pass. Whether to declare them is a maintainer decision.
9. **Annotation rendering (observation).** `AnnotationInspector` renders `tuple[int, str]` as `tuple[(int, str)]`. The test checks the prefix only. Source behaviour is unchanged.
10. **Service-path glob (observation).** Service-path matching uses `fnmatch`, so `**/services/*.py` does not match a root-level `services/x.py`. Behaviour is unchanged; the flow-trace examples use `apps/demo/services/`.
11. **Absolute paths in loc-cap output (observation).** The loc-cap command resolves its root, so it prints absolute paths. Behaviour is unchanged; the README shows the output with the root elided.
12. **Workflow echo line (outside scope).** `.github/workflows/cleanup-guard.yml` prints a check-mark glyph in an `echo`. It is a workflow file, not a source, test or markdown file, and was not changed.
13. **Package metadata (outside scope).** The `authors` field in `pyproject.toml` is package metadata, not markdown, and was not changed.

## Behavior Changes

| change | where | changelog entry (0.6.0) |
|--------|-------|-------------------------|
| The default exception tag is `module-level:`; prose that merely mentions the words no longer exempts a function. | `strict_config/constants.py`, `strict_checkers/r009.py` (message) | Added and Changed: the default exception tag entries |
| An unreadable or unparseable Python file exits 1 with a stderr error instead of being skipped. | `strict_linter/linter_client.py`, `strict_module/cli.py` | Fixed: unreadable or unparseable input fails the run |
| An unreadable counted file, or an undecodable LOC cap baseline, exits 1 with a stderr error instead of counting as zero lines or as an empty baseline. | `strict_loc_cap/loc_cap_client.py` | Fixed: unreadable or unparseable input fails the run |
| New public exception classes `LintInputError` (linter) and `LocCapInputError` (loc-cap) are raised by the library API. | `strict_linter`, `strict_loc_cap` | Changed: unreadable input raises a typed error from the library API |
| `DICT_STR_ANY_PATTERN` is removed. | `strict_config/constants.py` | Removed |
| The loc-cap success line starts with `OK:` instead of a check-mark glyph. | `strict_loc_cap/loc_cap_client.py` | Changed: loc-cap success line is ASCII |
| The first part of the pass also changed the R009 default severity and the R004 facade rule, documented in the same changelog section. | `strict_checkers/r004.py`, `strict_checkers/r009.py` | Changed: R009 advisory by default; R004 narrowed to the facade shape |

The `strict_config` export surface (names and `__all__`) is unchanged by the explicit re-export.

## Gate Results

Counts: 35 source modules and 80 test-tree files were reviewed (115 Python files are type-checked by the mypy gate). 41 test-tree files changed; 3 were added. Source modules changed in this pass are marked in the source table. Tests before the pass: 464 passed at 97.45 percent coverage; tests after: 476 passed at 97.64 percent coverage on Python 3.12 and on Python 3.14. Findings before the pass: 288 across the test tree; after: 50, all listed under Deferred Candidates.

Test suite on Python 3.12 (`uv run pytest -v --cov --cov-fail-under=95`), tail:

```
TOTAL                                                                      4826     50    602     72    98%
Required test coverage of 95% reached. Total coverage: 97.64%
============================= 476 passed in 9.05s ==============================
```

Test suite on Python 3.14 (`uv run --python 3.14 pytest -v --cov --cov-fail-under=95`), tail:

```
TOTAL                                                                      4826     50    602     72    98%
Required test coverage of 95% reached. Total coverage: 97.64%
============================= 476 passed in 8.44s ==============================
```

Type check (`uv run mypy strict_checkers/ strict_config/ strict_inspection/ strict_linter/ strict_loc_cap/ strict_rules/ strict_module/`), tail:

```
Success: no issues found in 115 source files
```

Lint (`uvx ruff@0.15.14 check strict_checkers/ strict_config/ strict_inspection/ strict_linter/ strict_loc_cap/ strict_rules/ strict_module/`), tail:

```
All checks passed!
```

Format check (`uvx ruff@0.15.14 format --check strict_module/`), tail:

```
2 files already formatted
```

Self-lint (the verbatim command from the strict-module workflow), exit 0 with no output.

Lockfile (`uv lock --check`), tail:

```
Resolved 15 packages in 1ms
```

Changelog header:

```
## [0.6.0] - 2026-10-18
```

Version file at the tip of the branch:

```
__version__ = "0.6.0"
```
