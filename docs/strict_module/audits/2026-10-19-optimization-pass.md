# Optimization Pass Audit: 2026-10-19

This audit records a code-quality and performance pass over every source module of the linter. Each module was reviewed for correctness (latent defects, swallowed exceptions, substring matching, version-specific APIs), dead or duplicated code, control-flow shape, typing precision, literal placement, naming, and per-file performance on the AST walk. The table lists each reviewed file with the number of findings, whether the file changed in this pass, and a note on the outcome. Findings that were not acted on are recorded in the note with the reason. Behaviour changes made by the pass are listed in the changelog under the unreleased section.

Test modules are not part of this table. Source files that only re-export names (package `__init__.py` files) were reviewed and carry no findings.

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
| strict_config/__init__.py | 1 | no | Wildcard re-export of the constants module kept to preserve the names importable from the package. Recorded for a later decision. |
| strict_config/_config.py | 3 | yes | Malformed or unreadable configuration now raises a typed error naming the path (it previously returned defaults silently); non-table sections are rejected; default lists are copied so loaded configs cannot alter shared constants. |
| strict_config/_version.py | 0 | no | Version bump is outside this pass. |
| strict_config/constants.py | 2 | yes | Added the module-level exception tag and named tag constants; added the configuration error message. The unused path-pattern constant is kept because it belongs to the exported constants surface. |
| strict_inspection/__init__.py | 0 | no | Re-export surface unchanged. |
| strict_inspection/annotations_client.py | 4 | yes | Annotation matching by name instead of substring (a substring match flagged identifiers such as Company and missed qualified typing.Any); removed a Python 3.8 compatibility branch that the 3.12 floor does not need; the en dash and em dash characters inside the noqa parser are written as escapes. |
| strict_inspection/paths_client.py | 1 | yes | Service-path and DTO-path matching share one helper. |
| strict_linter/__init__.py | 0 | no | Re-export surface unchanged. |
| strict_linter/linter_client.py | 4 | yes | Disabled-rule and baseline filters were applied twice per path; now applied once. The checker list is a module constant instead of a list built per file. The exit-code mapping is a severity table. Unused attribute removed. Left unchanged and recorded: an unreadable or unparsable file is skipped silently, which a linter should report; changing that is a behaviour decision for the maintainer. |
| strict_linter/linter_objects.py | 0 | no | The baseline entry dataclass is exported and kept. |
| strict_loc_cap/__init__.py | 0 | no | Re-export surface unchanged. |
| strict_loc_cap/loc_cap_client.py | 3 | yes | Removed a printed reference to an internal memory file and made the refactor example generic. Left unchanged and recorded: unreadable files count as zero lines and an unreadable baseline is treated as empty; both are silent. Exclusion patterns match substrings of the full path. The check mark in the success message is kept because it is existing output. |
| strict_loc_cap/loc_cap_objects.py | 1 | yes | Defaults taken from the constants module instead of repeated literals. |
| strict_module/__init__.py | 0 | no | Re-export surface unchanged. |
| strict_module/cli.py | 4 | yes | Shared option builders for the two parsers; the linter is built once per run; a malformed configuration prints the error and exits with the blocking code; module-level helpers recorded with a reason. |
| strict_rules/__init__.py | 0 | no | Re-export surface unchanged. |
| strict_rules/rules_client.py | 2 | yes | Rule registry typed; Optional replaced with a union. Rule R004 and R009 entries updated to the new rules. |
| strict_rules/rules_objects.py | 0 | no | Severity and violation types unchanged. |
