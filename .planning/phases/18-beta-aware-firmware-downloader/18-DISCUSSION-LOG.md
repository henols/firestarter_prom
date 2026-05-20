# Phase 18: Beta-Aware Firmware Downloader - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.

**Date:** 2026-05-20
**Phase:** 18-beta-aware-firmware-downloader
**Discussion mode:** `--auto --chain` (autonomous recommended-option selection)
**Areas discussed:** A) CLI surface, B) Pre-release selection, C) Pagination, D) `--pre` fallback, E) Version validation, F) `--list` output, G) Dependency, H) Refactor approach, I) Mutex flags, J) Beta-app magic default, K) Caching

---

## A. CLI Surface Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Extend `fw` subparser with new flags (`--pre`, `--firmware-version`, `--list`, `--json`) | Matches existing pattern; minimal new surface. | ✓ |
| Add new top-level `firestarter firmware` subparser with sub-subcommands | More extensible long-term but doubles entry points. | |
| Hybrid: extend `fw` AND add `firestarter firmware list` subparser | Convenience aliases. Adds duplicate surface. | |

**Rationale:** `fw` is the established namespace ([main.py:192](firestarter_app/firestarter/main.py#L192)); existing flags `-i/--install`, `-b/--board`, `-f/--force` set the pattern.

---

## B. Pre-release Selection Algorithm (INST-02)

| Option | Description | Selected |
|--------|-------------|----------|
| `packaging.version.Version` PEP 440 sort across all `prerelease: true` tags | Canonical PEP 440 ordering. Handles edge cases (b vs rc, double-digit N). | ✓ |
| Take most recently published (by `published_at` timestamp) | Simpler. Fails when releases are published out of version order. | |
| Take first in API response (GitHub default order) | Brittle — depends on undocumented API behavior. | |

---

## C. `/releases` Pagination

| Option | Description | Selected |
|--------|-------------|----------|
| Follow `Link: rel=next` header, cap at 5 pages (150 releases default) | Standard GitHub API pagination; bounded memory. | ✓ |
| Fetch single page (30 releases) and stop | May miss older releases. | |
| Unbounded pagination | Risk: huge repos could OOM. | |

---

## D. `--pre` Fallback When No Pre-release Exists

| Option | Description | Selected |
|--------|-------------|----------|
| Silent fallback to stable + INFO log (mirrors `pip install --pre`) | Operator gets *some* firmware; matches pip mental model. | ✓ |
| Error fatally — refuse to install stable when `--pre` was requested | More explicit but breaks bare beta-app install when no beta has been published. | |

---

## E. `--firmware-version` Validation (INST-03)

| Option | Description | Selected |
|--------|-------------|----------|
| `FIRMWARE_VERSION_RE` regex (superset of Phase 15 `BETA_VERSION_RE`); validate in argparse | Fail fast, no network call on bad input. Documented relationship to Phase 15. | ✓ |
| Validate via `packaging.version.Version` parse — accept any PEP 440 string | More permissive (accepts `1.0.0.dev1`, `1.0.0a1`, etc.) but milestone scope is `b`/`rc` only. | |
| No validation — pass to GitHub API and let 404 explain | Wastes a network round-trip on typos. | |

---

## F. `--list` Output Format (INST-04)

| Option | Description | Selected |
|--------|-------------|----------|
| Plain text table default; `--json` modifier for machine consumption | Greppable for humans, parseable for scripts. | ✓ |
| JSON only | Forces operators to pipe through `jq` for basic listing. | |
| Plain table only | Closes off scripting use cases. | |

---

## G. `packaging` Dependency

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit `packaging>=21.0` in `pyproject.toml` `[project.dependencies]` | Guards against transitive disappearance; documents intent. | ✓ |
| Rely on transitive availability through `pip`/`setuptools` | Works today but brittle. | |
| Vendor-copy the few needed `Version` parts | Avoids dep entirely. Reinvents widely-used library. | |

---

## H. Refactor Approach

| Option | Description | Selected |
|--------|-------------|----------|
| Keep `fetch_latest_release_info` as stable-only back-compat shim; add new `fetch_release_info(channel, version, board)` router | Localized change; existing callers untouched until they opt in. | ✓ |
| Replace `fetch_latest_release_info` with router in-place; rename for clarity | Cleaner final state but breaks any external callers. | |
| Split into three methods (`fetch_stable`, `fetch_pre`, `fetch_pinned`) | More boilerplate at callsites; harder to test uniformly. | |

---

## I. Mutually-Exclusive Flag Handling

| Option | Description | Selected |
|--------|-------------|----------|
| argparse `add_mutually_exclusive_group()` for `--pre` ⊥ `--firmware-version`, and `--list` ⊥ `-i/--install` | argparse handles rejection automatically; standard idiom. | ✓ |
| Validate at command-dispatch time with custom error | More flexible (could give better error messages) but reinvents argparse. | |

---

## J. Beta-App Magic Default (operator hard requirement)

| Option | Description | Selected |
|--------|-------------|----------|
| Magic default: bare `fw -i` on a pre-release install auto-routes to `--pre`; detect via `Version(__version__).is_prerelease` | Satisfies operator's "beta app always installs latest beta"; INFO log informs operator | ✓ |
| Require explicit `--pre` flag from beta operators (no magic) | Cleaner mental model but contradicts the stated requirement. | |
| Add a config option `default_firmware_channel: pre` in operator config | More configurable but requires beta operators to set it manually. | |

**Rationale:** The operator's phrasing — "the beta app shall always download the latest beta fw" — is strong and unambiguous. Magic default is the simplest way to honor that without making the operator type `--pre` every time. The opt-out path (`--firmware-version X.Y.Z`) and the INFO log per D-25 keep the behavior auditable.

---

## K. Caching

| Option | Description | Selected |
|--------|-------------|----------|
| No caching for v1.4; each invocation hits GitHub | Simple; matches today's behavior. Listed in Future Requirements. | ✓ |
| Cache release listings in `~/.firestarter/cache/` with TTL | Faster repeated `--list` invocations; adds cache invalidation surface. | |

---

## Claude's Discretion

- **D-27**: Exact `ReleaseInfo` data shape (TypedDict vs dataclass vs plain dict) — planner picks.
- **D-28**: Whether `list_releases` paginates eagerly or returns an iterator — planner picks.
- **D-29**: Whether a `--no-pre` flag is worth adding for beta-app operators to opt back to stable — recommended NO; `--firmware-version X.Y.Z` is the documented opt-out.
- **D-30**: Exact wording of magic-default INFO log — planner picks; constraint is it must say "beta app detected" + name the opt-out path.

## Deferred Ideas

- Release-listing cache / offline install — Future Requirements.
- `--no-pre` flag — see D-29.
- Per-board fallback when one board has beta and another doesn't — Future Requirements.
- `default_firmware_channel` config option — option J non-selected.
- Signed-artifact verification — Future Requirements.
- Consumer-side beta→stable promotion command — out of scope.
