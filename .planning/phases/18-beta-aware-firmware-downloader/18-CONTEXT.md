# Phase 18: Beta-Aware Firmware Downloader - Context

**Gathered:** 2026-05-20
**Status:** Ready for planning
**Discussion mode:** `--auto --chain` (autonomous recommended-option selection)

<domain>
## Phase Boundary

`firestarter_app/` gains the minimum consumer-side surface needed to make the v1.4 firmware beta channel actually installable from the `firestarter` CLI. The existing `firestarter fw -i` (stable) flow is preserved byte-identically on stable-installed apps (GATE/INST-01 non-regression). New affordances:

- `firestarter fw -i --pre` → fetches latest pre-release firmware for the configured board (mirrors `pip install --pre` semantics — falls back to stable if no pre-release exists).
- `firestarter fw -i --firmware-version X.Y.Z[bN|rcN]` → exact-tag pin via `/repos/henols/firestarter/releases/tags/{tag}`. Works for both stable and pre-release tags.
- `firestarter fw --list [--all|--pre|--stable]` → enumerates available firmware releases for the configured board. Plain table by default; `--json` for machine consumption.
- **Magic default for beta apps:** when `packaging.version.Version(firestarter.__version__).is_prerelease` is True, bare `firestarter fw -i` (no new flags) auto-routes through the `--pre` selection path. This satisfies the operator's stated requirement: "the beta app shall always download the latest beta fw." Stable-installed apps see no change.
- `firmware.py:_compare_versions` refactored to use `packaging.version.Version` so PEP 440 pre-release strings (`3.1.0b1`, `3.1.0rc2`) no longer crash with `ValueError`. Today's stable path is protected only by GitHub's `/releases/latest` filter; Phase 18's new paths bypass that protection and need a real comparator.

**In scope (Phase 18 only):**
- New CLI flags on the existing `fw` subparser: `--pre`, `--firmware-version`, `--list` (plus `--json` modifier for list output).
- New helper: `FirmwareManager.fetch_release_info(channel='stable'|'pre'|'pinned', version=None, board='uno')` router.
- New helper: `FirmwareManager.list_releases(channel_filter='all'|'pre'|'stable', board='uno')` enumeration.
- Refactor: `_compare_versions` → PEP 440 ordering via `packaging.version.Version`.
- Module-level `FIRMWARE_VERSION_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+((b|rc)[0-9]+)?$')` for `--firmware-version` input validation.
- New explicit dep `packaging>=21.0` in `firestarter_app/pyproject.toml`.
- pytest coverage for each path (stable default, beta-app magic default, --pre, --firmware-version, --list/--json, comparator).

**Out of scope (deferred or other phases):**
- Release listing cache / offline install (Future Requirements).
- README updates documenting the new flags — that's Phase 19 (DOC-01/DOC-02).
- Per-board fallback when `--pre` finds a release that has assets for board X but not board Y (Future Requirements).
- Any other CLI behavior changes — strict carve-out per the v1.4 scope amendment.

</domain>

<decisions>
## Implementation Decisions

### A. CLI Surface Shape

- **D-01:** Extend the existing `fw` subparser ([main.py:192 `create_firmware_args`](firestarter_app/firestarter/main.py#L192)) with new flags. Do NOT introduce a separate `firestarter firmware` top-level command — the `fw` namespace is established and adding flags matches the existing `-i/--install`, `-b/--board`, `-f/--force` shape.
- **D-02:** New flags on `fw`:
  - `--pre` (no short form; `--pre` exactly mirrors `pip install --pre`)
  - `--firmware-version VERSION` (no short form; `VERSION` is a PEP 440 string)
  - `--list` (boolean flag; when present, prints release table and exits — does NOT install)
  - `--json` (boolean modifier; only meaningful with `--list`; outputs JSON instead of plain table)

### B. Pre-release Selection Algorithm (INST-02)

- **D-03:** When `--pre` is active (explicit flag OR beta-app magic default), `fetch_release_info(channel='pre', ...)`:
  1. Paginate `GET /repos/henols/firestarter/releases` via `Link: rel=next` header (D-08 cap).
  2. Filter to releases with `prerelease: True`.
  3. Parse each `tag_name` via `packaging.version.Version`; discard tags that fail to parse (logged WARN, not fatal).
  4. Sort descending by parsed Version; take highest.
  5. Resolve `browser_download_url` for asset `firestarter_{board}.hex` from that release's assets list.
  6. If step 2 yields zero releases → silently fall back to stable path (D-04). If step 5 yields no matching asset for the board → error fatally with the release tag + missing-asset name (operator can then inspect `--list` to find a different release).

### C. Pagination Behavior

- **D-04:** Follow GitHub's standard `Link: <...>; rel="next"` header to paginate `/releases`. Cap at 5 pages (150 releases default page size). If the project ever publishes more than 150 releases, raise the cap in a future milestone. Logged INFO when the cap is hit.

### D. `--pre` Fallback When No Pre-release Exists

- **D-05:** If `--pre` is requested but no `prerelease: True` release exists (or all parse-failed), silently fall back to the stable path (`/releases/latest`) and log INFO: `No pre-release firmware available — falling back to stable (matches pip --pre semantics).`
- **D-06:** This means a beta-installed app with the magic default ALWAYS gets *some* firmware: a beta if one exists, otherwise stable. This satisfies the operator's "always download latest beta" requirement without breaking the install when betas haven't been published yet (e.g., immediately after Phase 18 ships and before Phase 17 has cut a real beta).

### E. `--firmware-version` Validation (INST-03)

- **D-07:** Validate the supplied version string against `FIRMWARE_VERSION_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+((b|rc)[0-9]+)?$')` BEFORE any network call. Invalid input → `argparse.ArgumentTypeError` with example: `Expected X.Y.Z, X.Y.ZbN, or X.Y.ZrcN (e.g. 3.1.0, 3.1.0b2, 3.1.0rc1).`
- **D-08:** Accept both stable (`3.1.0`) and pre-release (`3.1.0b2`, `3.1.0rc1`) forms. The regex is a superset of Phase 15's `BETA_VERSION_RE` (which only accepted pre-release forms) — different validation surface, different regex. Document the relationship: "Phase 15 `BETA_VERSION_RE` validates publisher-side input; Phase 18 `FIRMWARE_VERSION_RE` validates consumer-side install pin."
- **D-09:** On valid input, fetch `/repos/henols/firestarter/releases/tags/{tag}` directly. Resolve the board-matching asset. If the tag returns 404 OR the asset doesn't exist for the board → error fatally with a clear message ("Tag X.Y.ZbN not found in firestarter releases" or "Release X.Y.ZbN has no asset for board {board}").

### F. `--list` Output Format (INST-04)

- **D-10:** Default `firestarter fw --list` output is a plain-text table:
  ```
  Version    Channel       Published              Asset URL
  3.1.0b2    Pre-release   2026-05-20 14:32 UTC   https://...firestarter_uno.hex
  3.1.0b1    Pre-release   2026-05-19 09:11 UTC   https://...firestarter_uno.hex
  3.0.0      Stable        2026-05-15 11:00 UTC   https://...firestarter_uno.hex
  ```
- **D-11:** Sorted by parsed PEP 440 Version descending (newest first). One row per release that has a `firestarter_{board}.hex` asset; releases without a board-matching asset are silently omitted.
- **D-12:** `--list --json` emits the same data as a JSON array of objects with keys `version`, `channel` (`"stable"|"prerelease"`), `published` (ISO-8601), `asset_url`, `tag` (raw `tag_name`). For machine consumption / scripting.
- **D-13:** `--list --pre` filters to `prerelease: True` only; `--list --stable` filters to `prerelease: False` only; `--list --all` (or no channel filter) shows both. `--pre` / `--stable` / `--all` are mutually exclusive within `--list` (argparse mutex group; default `--all`).

### G. `packaging` Dependency

- **D-14:** Add `packaging>=21.0` to `firestarter_app/pyproject.toml` `[project.dependencies]`. Today it's transitive through `pip`/`setuptools`; promoting to explicit guards against transitive disappearance. `21.0` is the version that introduced stable `packaging.version.Version.is_prerelease` semantics; broadly available since 2021.

### H. Refactor Approach

- **D-15:** Keep `FirmwareManager.fetch_latest_release_info(board)` as-is (stable-only, hits `/releases/latest`). It's the back-compat shim used by `manage_firmware_update`'s stable path. Mark its docstring "Stable-only path; use `fetch_release_info` for general channel selection."
- **D-16:** Add new canonical method:
  ```python
  def fetch_release_info(
      self,
      channel: Literal['stable', 'pre', 'pinned'] = 'stable',
      version: Optional[str] = None,  # required when channel='pinned'
      board: str = 'uno',
  ) -> Tuple[Optional[str], Optional[str]]:
      """Returns (resolved_version, download_url) or (None, None) on failure.
      channel='stable' → /releases/latest (same as fetch_latest_release_info).
      channel='pre'    → enumerate /releases, filter prerelease=True, sort by PEP 440, take highest; fall back to 'stable' if empty.
      channel='pinned' → /releases/tags/{version} direct lookup."""
  ```
- **D-17:** Add `list_releases(channel_filter='all', board='uno') -> list[ReleaseInfo]` returning a list of dataclasses/dicts (D-10 / D-12 schema).
- **D-18:** `manage_firmware_update` grows new args: `channel: Literal['stable','pre','pinned'] = 'stable'`, `pinned_version: Optional[str] = None`. Dispatches to `fetch_release_info` with the corresponding kwargs.

### I. Mutually-Exclusive Flag Handling

- **D-19:** `--pre` and `--firmware-version` are mutually exclusive — adding both expresses contradictory intent. Use argparse `add_mutually_exclusive_group()` so argparse handles the rejection. Test: passing both exits non-zero with argparse's standard error message.
- **D-20:** `--list` is mutually exclusive with `-i/--install` — `--list` is read-only enumeration; mixing it with install intent is also contradictory. Same argparse mutex pattern.

### J. Beta-App Magic Default (operator hard requirement)

- **D-21:** **When `firestarter` is a pre-release install** (`packaging.version.Version(firestarter.__version__).is_prerelease` returns True), bare `firestarter fw -i` (with no `--pre`, no `--firmware-version`) AUTO-ROUTES through the `--pre` selection path. This satisfies the operator's stated requirement: "the beta app shall always download the latest beta fw."
- **D-22:** Detection happens in `main.py` at command dispatch time, BEFORE calling `manage_firmware_update`:
  ```python
  if args.command == "fw" and args.install and not args.pre and not args.firmware_version:
      import firestarter as _pkg
      from packaging.version import Version
      if Version(_pkg.__version__).is_prerelease:
          args.pre = True  # magic default
          logger.info("Beta app detected — defaulting to --pre. Use --firmware-version X.Y.Z to pin a stable version.")
  ```
- **D-23:** **Stable-installed apps see no change.** `Version("2.0.7").is_prerelease` is False, so bare `firestarter fw -i` on a stable install continues to hit `/releases/latest` — INST-01 non-regression preserved.
- **D-24:** **Opt-out for beta apps:** to install a stable firmware version while on a beta app, use `firestarter fw -i --firmware-version X.Y.Z` (explicit stable pin). No need for a `--no-pre` flag — the explicit version pin is the documented escape.
- **D-25:** **Audit logging:** the auto-default ALWAYS logs an INFO line at command start so the operator knows magic happened (D-22's log statement). Surprise-free magic.

### K. Caching

- **D-26:** No caching for v1.4. Each `fw -i` / `fw --list` invocation hits GitHub fresh. Listed in REQUIREMENTS.md Future Requirements ("Cached firmware download / offline install — Today the app always hits GitHub. Cache layer would be a separate feature.").

### Claude's Discretion

- **D-27:** Exact `ReleaseInfo` data shape (TypedDict vs dataclass vs plain dict) — planner picks per Python version requirements (project targets >=3.9 per `pyproject.toml`).
- **D-28:** Whether `list_releases` itself paginates or returns an iterator — planner picks based on memory/latency considerations. 150-release cap (D-04) keeps memory bounded either way.
- **D-29:** Whether to surface a `--no-pre` flag for explicit "even though I'm on a beta app, I want stable today" — recommended NO per D-24 (`--firmware-version X.Y.Z` is the documented opt-out); planner can revisit if a clear UX win materializes.
- **D-30:** Exact wording of the magic-default INFO log (D-22 / D-25) — planner picks; constraint is it MUST explicitly say "beta app detected" and "use --firmware-version X.Y.Z to pin stable" so operators understand the opt-out path.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents (gsd-phase-researcher, gsd-planner) MUST read these before planning or implementing.**

### Milestone planning artifacts
- `.planning/PROJECT.md` — Project overview; current milestone v1.4 scope.
- `.planning/REQUIREMENTS.md` §INST — INST-01 through INST-04 (acceptance criteria for this phase).
- `.planning/REQUIREMENTS.md` §"Scope amendment (2026-05-20)" — explicit carve-out for the four CLI additions + comparator fix.
- `.planning/ROADMAP.md` §"Phase 18: Beta-Aware Firmware Downloader" — phase goal, success criteria, dependencies.
- `.planning/STATE.md` §"v1.4 Decisions" — locked decisions including the 2026-05-20 amendment.

### Files to modify in `firestarter_app/`
- `firestarter_app/firestarter/firmware.py` — THE primary file. Extend `FirmwareManager` with `fetch_release_info` + `list_releases` + refactored `_compare_versions`. Preserve `fetch_latest_release_info` as a back-compat shim (D-15).
- `firestarter_app/firestarter/main.py` §`create_firmware_args` (line 192-227) — extend `fw` subparser with `--pre`, `--firmware-version`, `--list`, `--json` flags + mutex groups (D-02, D-19, D-20).
- `firestarter_app/firestarter/main.py` §`fw` command dispatch (line 645-657) — branch on `args.list` vs install; route channel/version to `manage_firmware_update`; add magic-default detection (D-22).
- `firestarter_app/firestarter/constants.py` — add `FIRMWARE_VERSION_RE` constant and `FIRESTARTER_RELEASES_URL` (without `/latest` suffix) for the list/pre paths.
- `firestarter_app/pyproject.toml` — add `packaging>=21.0` to `[project.dependencies]`.

### Files to create
- `firestarter_app/tests/test_firmware_install.py` — new pytest file covering INST-01..04 + comparator fix + magic-default detection. Mock `requests.get` (mirror Phase 15 test pattern with `monkeypatch.setattr` on the module's `requests`).

### Phase 15 deliverables (reference / contract)
- `.planning/phases/15-versioning-locked-step-coordination-foundation/15-CONTEXT.md` D-21 — `BETA_VERSION_RE` regex (Phase 18's `FIRMWARE_VERSION_RE` is its consumer-side superset per D-08).
- `.planning/phases/15-versioning-locked-step-coordination-foundation/15-RESEARCH.md` — PEP 440 details, `packaging.version.Version` semantics (already verified for the publisher side; same library, same semantics).

### External specs
- PEP 440 (https://peps.python.org/pep-0440/) — pre-release ordering rules (`bN < rcN < stable`).
- pip `--pre` semantics (https://pip.pypa.io/en/stable/cli/pip_install/#pre-release-versions) — fallback-to-stable behavior is the reference for D-05.
- GitHub REST API: list releases (https://docs.github.com/en/rest/releases/releases#list-releases) and get release by tag (https://docs.github.com/en/rest/releases/releases#get-a-release-by-tag-name) — endpoints D-03 and D-09 use.
- `packaging.version` (https://packaging.pypa.io/en/stable/version.html) — `Version.is_prerelease` property (D-21 magic-default trigger).

### Phase 19 / 20 contract
- Phase 19 (Documentation) consumes the final CLI surface — README examples will reference `--pre`, `--firmware-version`, `--list` verbatim. Plan 18's task acceptance criteria specify the EXACT flag spellings so Phase 19 doesn't have to guess.
- Phase 20 (E2E) E2E-01 criterion (e): `pip install --pre firestarter==X.Y.ZbN && firestarter fw -i --pre` must succeed end-to-end against the real beta firmware from Phase 17. Phase 18 mocks the GitHub API in unit tests; Phase 20 exercises the real network.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`FirmwareManager.fetch_latest_release_info`** ([firmware.py:101-133](firestarter_app/firestarter/firmware.py#L101)) — Today's `/releases/latest` fetcher. Asset selection logic (`firestarter_{board}.hex` matched against `release_data.get("assets", [])`) is the template for the new `fetch_release_info` router and `list_releases`. Reuse the asset-resolution loop verbatim — it's the contract between firmware publisher (Phases 16/17) and consumer.
- **`FirmwareManager._download_firmware_file`** ([firmware.py:151-182](firestarter_app/firestarter/firmware.py#L151)) — Streaming download to `~/.firestarter/`. Untouched by Phase 18 — both stable + pre + pinned channels resolve to a `browser_download_url` that this method consumes unchanged.
- **`FirmwareManager._install_with_avrdude`** ([firmware.py:184+](firestarter_app/firestarter/firmware.py#L184)) — Untouched by Phase 18.
- **`FirmwareManager.manage_firmware_update`** ([firmware.py:294-300](firestarter_app/firestarter/firmware.py#L294)) — The orchestrator. Grows new args (`channel`, `pinned_version`) per D-18 but its overall shape is preserved.
- **Existing pytest patterns** — `firestarter_app/tests/test_update_version.py` (Phase 15 wave 0/1) is the closest analog for `test_firmware_install.py`: class-based with autouse env-cleanup fixture, `monkeypatch.setattr` on module attributes, no real network calls.

### Established Patterns

- **`requests` for HTTP** — existing fetcher already uses `requests.get` with timeout. Phase 18 reuses (no new dep — `requests` is already in `pyproject.toml`).
- **`logger.info` for operator-visible state changes / `logger.debug` for noise** — preserved in new paths. Magic-default detection logs INFO per D-25; pagination logs DEBUG.
- **`argparse` subparsers** — `fw` is a sub-parser of the top-level parser; new flags attach to it (`fw_parser.add_argument(...)`).
- **Asset name convention `firestarter_{board}.hex`** — established by today's stable releases ([firmware.py:114](firestarter_app/firestarter/firmware.py#L114)). Phase 17 inherits this naming for pre-release artifacts — Phase 18 relies on it.
- **`~/.firestarter/` for downloaded artifacts** ([firmware.py:35 `HOME_PATH`](firestarter_app/firestarter/firmware.py#L35)) — Phase 18 download path unchanged. Filename is derived from URL (line 163-167); pre-release filenames like `firestarter_uno.hex` collide with stable filenames in `~/.firestarter/` — current behavior overwrites the local file, which is intentional ("most-recent download wins").

### Integration Points

- **`firestarter.__version__`** ([firmware.py imports `firestarter.constants`](firestarter_app/firestarter/firmware.py#L19); version lives in `firestarter/__init__.py`) — `import firestarter as _pkg; _pkg.__version__` returns the install-time string (`"2.0.7_dev"` or `"3.1.0b1"` etc.). Pass through `packaging.version.Version(_pkg.__version__).is_prerelease` per D-21.
- **GitHub REST API base** — `https://api.github.com/repos/henols/firestarter/`. Existing `FIRESTARTER_RELEASE_URL` constant (line 8-10 of `constants.py`) hardcodes the `/releases/latest` path; Phase 18 adds a sibling `FIRESTARTER_RELEASES_URL = "https://api.github.com/repos/henols/firestarter/releases"` (for list/pre paths) and a templated `FIRESTARTER_RELEASE_BY_TAG_URL = "https://api.github.com/repos/henols/firestarter/releases/tags/{tag}"` (for pinned).
- **`ConfigManager`** ([firmware.py:53](firestarter_app/firestarter/firmware.py#L53)) — passed to `FirmwareManager` constructor; carries operator config including preferred port. Untouched by Phase 18 unless the planner judges that a `default_firmware_channel` config option is useful (recommendation: NO for v1.4 — keep config surface clean).
- **Existing comparator usage** — `_compare_versions` is called from `manage_firmware_update` line 335 ONLY. Refactor is localized.

</code_context>

<specifics>
## Specific Ideas

- **Operator's hard requirement (driver for the scope amendment):** "the original app can download the latest fw correct" + "the beta app shall always download the latest beta fw and have the possibility to list all available fw's in beta and release. And be capable of installing them." This phrasing drove D-21 (magic default for beta apps). Stable-app default must NOT change.
- **`pip install --pre` is the lodestar** — the user's mental model is the pip flag they already know. D-05 (silent fallback to stable when no prerelease) mirrors pip; D-21 (magic default for prerelease installs) is one step beyond pip but tightly justified by the "always download latest beta" requirement.
- **`firestarter_*.hex` asset naming is a publisher-consumer contract** — established in v1.0, carried through v1.2, locked by Phase 17 for beta releases. Phase 18's asset-resolution loop relies on it. If Phase 17 ever changes the asset name pattern (e.g., `firestarter-uno.hex` instead of `firestarter_uno.hex`), Phase 18 breaks silently. Worth a cross-phase note for Phase 17.
- **Pre-existing dev-suffix carry from v1.0** — App is currently at `2.0.7_dev`, firmware at `3.0.0-dev`. Phase 15 documented that these are silently truncated by old regex. Phase 18's `packaging.version.Version("2.0.7_dev")` will RAISE `InvalidVersion`. The magic-default check (D-21) MUST handle this gracefully — wrap in try/except, treat invalid as non-prerelease (safest fallback). Document in planner output.

</specifics>

<deferred>
## Deferred Ideas

- **Caching the release listing for repeated `--list` invocations** — see Future Requirements in REQUIREMENTS.md.
- **`--no-pre` flag** to force stable on a beta-installed app — D-24 says the documented opt-out is `--firmware-version X.Y.Z` (explicit stable pin). If a clear UX need surfaces, add later. Not in Phase 18 scope.
- **Per-board fallback** when a pre-release exists for one board but not another (e.g., Uno has beta, Leonardo doesn't) — see Future Requirements. INST-02's current spec falls back to stable only when NO prerelease exists at all, not per-board.
- **Default-firmware-channel config option** (e.g., `default_firmware_channel: pre` in operator config) — would let operators pin a channel preference without retyping `--pre`. Cleaner than the magic default but adds config surface. Magic default chosen over config option because operator's requirement is "beta app *always* installs beta", not "beta app remembers operator preference."
- **Signed-artifact verification** — out of v1.4 scope (Future Requirements: signed release artifacts via sigstore/GPG).
- **Promotion path from beta to stable on the consumer side** (e.g., `firestarter fw --promote X.Y.ZbN`) — pure consumer-side promotion would conflict with `pip install` model. Not in scope.

</deferred>

---

*Phase: 18-beta-aware-firmware-downloader*
*Context gathered: 2026-05-20*
*Discussion mode: --auto --chain (autonomous recommended-option selection)*
