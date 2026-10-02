# DSO repository report v2

Produced by [dso scan repo](../tools/dso/README.md) and the
[MCP tool](../mcp/dso/README.md). `tools/dso/scanning.py:validate_report` is the
runtime validator used by the CLI and MCP gate. This scan snapshot is separate
from the [finding lifecycle record](finding.example.json), which adds human
ownership, SLA, tickets and risk decisions. Version 1 reports are rejected;
regenerate baselines with the current kit.

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer 2 |
| `project` | Required explicit project ID, at most 200 characters |
| `created_at` | UTC timestamp (`Z` or `+00:00`), not in the future |
| `coverage.tools` | Sorted, unique scanner selection |
| `coverage.versions` | Reviewed scanner versions (`X.Y.Z`) |
| `coverage.engine` | `native` or `docker` |
| `coverage.profile` | Scan profile; currently `repo-v2:snapshot,python3-starter,offline-dependencies` |
| `coverage.policy_digest` | SHA256 of the Gitleaks config, all loaded Semgrep rule files and the DSO scanner code |
| `coverage.exclusions` | Sorted reviewer-supplied target-relative exclusions |
| `coverage.default_exclusions` | Directory names never copied: `.git`, `.venv`, `venv`, `__pycache__`, `node_modules` |
| `input` | Snapshot evidence: `files`, `bytes` and a SHA256 manifest of relative paths and contents |
| `complete` | Boolean: every requested scanner completed |
| `runs` | One entry per scanner: `tool`, `status`, `finding_count`, `exit_code`, plus `error_code`/`error` when it failed |
| `findings` | Normalized, deduplicated findings sorted by ID |

Every finding has `id`, `tool`, `rule_id`, `path`, `line`, `package`,
`installed_version`, `fixed_version`, `severity` and `fingerprint`. Empty strings
and line 0 mean "not applicable". Severity is one of info, low, medium, high,
critical, unknown. Paths are target-relative; Trivy target labels may include its
ecosystem label. IDs are SHA256 of the JSON tuple
`[tool, rule_id, path, line, package, installed_version, fingerprint]` with
sorted keys, compact separators and Python's default ASCII escaping.

Secret findings carry `fingerprint`: SHA256 of a DSO domain prefix, the rule ID
and the matched secret. A rotated or replaced secret at the same location is
therefore a new finding. The value itself is never stored, but a weak secret can
be confirmed by guessing, so treat reports and baselines as confidential. Other
tools leave `fingerprint` empty. Reports contain no source snippets or raw
matches. Locations and package identifiers are still private data.

The validator checks field sets, types, lengths, control characters, IDs and
ordering, duplicate identities, per-tool counts, scanner exit codes against run
status, tool-specific finding shapes, profile, default exclusions and snapshot
evidence. A valid incomplete report is retained for diagnosis but cannot pass a
gate. Structural validity is not authenticity: reports and baselines must come
from trusted execution and storage. Database updates can legitimately add
findings for unchanged dependencies. Source line moves create new IDs.

Gate output contains `exit_code` (0 pass, 1 blocking, 2 incomplete or
incomparable), `status`, `mismatch`, `coverage_changes`, `new_or_escalated`,
`existing`, `blocking`, `resolved` and `fix_changed`. Blocking findings are
listed even for incomplete scans. A baseline must have the same `project`; other
coverage differences (engine, tool selection, versions, policy, exclusions) are
reported in `coverage_changes` but still compared, because a baseline only
accepts exact finding IDs. Unknown severity blocks at any threshold, with or
without a baseline. Existing findings are not closed in any external system;
DefectDojo lifecycle integration is future work.
