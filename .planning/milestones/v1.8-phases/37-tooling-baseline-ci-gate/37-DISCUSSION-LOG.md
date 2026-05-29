# Phase 37: Tooling Baseline + CI Gate - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-27
**Phase:** 37-Tooling Baseline + CI Gate
**Areas discussed:** Baseline→green strategy, Coverage gate, CI triggers & shape, Linter/type strictness (all four resolved via operator delegation: "what do you recommend?" → "Accept all four")

---

## Gray-area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Baseline → green + git-blame | noqa-everything vs autofix-first; `.git-blame-ignore-revs` for the whole-tree reformat | (delegated) |
| Coverage gate floor & ratchet | hard 60% vs measured-floor + ratchet vs defer | (delegated) |
| CI triggers & job shape | main-only (dormant) vs all-PR triggers; separate vs folded job; single vs matrix Python | (delegated) |
| Linter/type strictness | E/F/I/UP only vs broader set; mypy count-script vs baseline-tool vs strict-islands | (delegated) |

**User's choice:** "what do you recommend?" — operator delegated all four decisions to Claude.
**Notes:** Phase 37 is heavily pre-specified by the ROADMAP/REQUIREMENTS/PROJECT. The operator chose to take the recommended option on every open gray area rather than discuss each individually.

---

## Recommended decisions (presented, then accepted)

### Baseline → Green Strategy
| Option | Description | Selected |
|--------|-------------|----------|
| Format + autofix-I + noqa residue, blame-ignore-revs | `ruff format` (1 commit) → `ruff check --fix --select I` → `ruff check --add-noqa`; `.git-blame-ignore-revs` for the format SHA | ✓ |
| Blanket `--add-noqa` everything (incl. unsorted imports) | Minimal logic touch, more noqa litter | |
| Conservative: only enable rules the tree already passes | Lowest churn, defers UP | |

**Notes:** No hand-fixing in Phase 37 (honors locked "not hand-fixing everything"); star-import F403/F405 noqa'd now, fixed in Phase 39.

### Coverage Gate Floor & Ratchet
| Option | Description | Selected |
|--------|-------------|----------|
| Measured floor (5% step) + manual ratchet; 60% if already there | Honest baseline; never fails day one; ratchet to 70% by Phase 42 | ✓ |
| Hard-set 60% now | Per spec literal; risks failing build + forcing premature tests | |
| Defer coverage gate to a later phase | Ship lint/format/mypy only now | |

### CI Triggers & Job Shape
| Option | Description | Selected |
|--------|-------------|----------|
| All-PR triggers + folded single job + single Py3.11 (py39 target) | Fixes the dormant-gate gap; minimal YAML | ✓ |
| Keep main-only triggers | Gate dormant during the whole v1.8 branch milestone | |
| Separate parallel lint job / 3.9–3.12 matrix | More YAML + extra env setup; matrix deferred | |

### Linter / Type Strictness
| Option | Description | Selected |
|--------|-------------|----------|
| E/F/I/UP only + strict-islands + mypy count-script | Lean baseline; dependency-free watermark gate | ✓ |
| Add B/SIM/C4 now | More signal, more noqa litter today (defer to Phase 42) | |
| mypy-baseline tool | More precise than a count; extra dependency (deferred fallback) | |

---

## Claude's Discretion

- Name/location/implementation of the mypy watermark count-comparison script.
- `pre-commit` hook pinning (local vs pinned mirrors) + exact versions.
- Coverage config location (`[tool.coverage.*]` + CI flags vs pytest `addopts`).
- Precise 5%-step rounding for the coverage floor (after measurement).
- Whether import-sort autofix is `--select I` alone or a slightly wider mechanically-safe subset.

## Deferred Ideas

- Full 3.9–3.12 CI test matrix (out of tooling scope; later CI-hardening pass).
- Broader ruff rule set (B/bugbear, SIM, C4) → Phase 42 quality sweep.
- `mypy-baseline` tool as a more-precise alternative to the count-script.
- Reviewed-not-folded todos (off-domain, hardware/protocol): `avrdude-mcu-detection-fallback.md`, `serial-cobs-resync-data-path.md`, `w27c512-eeprom-misclassification.md`.
