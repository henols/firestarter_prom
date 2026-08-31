---
phase: quick-260729-iyx
plan: 01
subsystem: infra
tags: [devcontainer, bun, discord-plugin, mcp]

requires: []
provides:
  - System-wide Bun install layer in .devcontainer/Dockerfile (durable, next-rebuild)
  - Live /usr/local/bin/bun in the running container (immediate)
  - Proven PATH-resolution matrix for the non-interactive MCP launcher case
affects: [discord-channel-plugin-setup]

tech-stack:
  added: [bun 1.3.14 (system-wide, /usr/local prefix)]
  patterns: ["system-wide tool install at image-build time as root, mirroring the existing graphify/platformio precedent"]

key-files:
  created: []
  modified:
    - .devcontainer/Dockerfile

key-decisions:
  - "BUN_INSTALL=/usr/local (not the installer's $HOME/.bun default) so the binary lands on PATH for a non-interactive, non-login shell and survives a rebuild (~/.bun is not a named volume)"
  - "Live install staged the installer script to the scratchpad and ran it via `sudo env BUN_INSTALL=/usr/local bash <path>` rather than piping into `sudo bash`, keeping the privileged step reviewable"
  - "Bun version left unpinned, matching the existing unpinned platformio/graphifyy precedent in the same file; live version (1.3.14) recorded so future rebuild drift is visible"
  - "bun install --dry-run treated as a diagnostic only, not a pass/fail gate, per plan instruction"

requirements-completed: [QUICK-260729-iyx]

coverage:
  - id: D1
    description: "Dockerfile carries unzip + a system-wide Bun RUN layer, correctly ordered, with operator WIP intact"
    requirement: "QUICK-260729-iyx"
    verification:
      - kind: other
        ref: "Task 1 automated verify block (GATE1-PASS)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Bun installed live into the running container at /usr/local, executable, no root-owned surprises introduced in ~/vscode home"
    requirement: "QUICK-260729-iyx"
    verification:
      - kind: other
        ref: "Task 2 automated verify block (GATE2-PASS, baseline-adjusted)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Bun resolves for a non-interactive, non-login shell under the stock system PATH (four-probe matrix) and the plugin's bare `bun` command + dry-run dependency resolution are confirmed"
    requirement: "QUICK-260729-iyx"
    verification:
      - kind: other
        ref: "Task 3 automated verify block (GATE3-PASS)"
        status: pass
    human_judgment: false

duration: 5min
completed: 2026-07-29
status: complete
---

# Quick Task 260729-iyx: Install Bun in Devcontainer Summary

**Bun 1.3.14 installed both in the Dockerfile image layer (`/usr/local`, unpinned) and live in the running container, with a four-probe non-interactive PATH matrix proving it resolves the way Claude Code's MCP launcher actually resolves bare commands.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-07-29T13:49:02Z (Task 1 commit)
- **Completed:** 2026-07-29T13:51:02Z
- **Tasks:** 3 completed
- **Files modified:** 1 (`.devcontainer/Dockerfile`)

## Accomplishments

- Added `unzip` to the Dockerfile's apt list and a system-wide Bun install layer (`BUN_INSTALL=/usr/local`, official `bun.sh` installer, absolute-path build-time smoke check), positioned after the graphify layer and before the mount-point `mkdir`/`chown` block.
- Installed Bun 1.3.14 into the running container at the identical `/usr/local` prefix, so the live container and a future rebuilt container are behaviourally identical.
- Proved Bun resolves for a non-interactive, non-login shell (the exact resolution path Claude Code's MCP launcher uses for the Discord plugin's bare `"command": "bun"`), via four independent probes, and confirmed the plugin's dependency set resolves cleanly against its lockfile via `bun install --dry-run`.

## Task Commits

1. **Task 1: Add unzip + a system-wide Bun layer to the devcontainer Dockerfile** - `c5385a7` (chore)
2. **Task 2: Install Bun into the RUNNING container at the same prefix** - no commit (container-filesystem-only change, not git-tracked, per plan)
3. **Task 3: Prove Bun resolves for the non-interactive shell / prerequisite readback** - no commit (verification only, no files modified)

**Plan metadata:** (docs commit handled by orchestrator after this SUMMARY)

## Files Created/Modified

- `.devcontainer/Dockerfile` - added `unzip` to the apt-get install list; added a commented, system-wide Bun install `RUN` layer (`BUN_INSTALL=/usr/local`, official installer, absolute-path `--version` smoke check)

## Bun Version String

```
1.3.14
```

(Resolved via both `/usr/local/bin/bun --version` and `bun --version` on PATH — identical, `bun install v1.3.14 (0d9b296a)` also visible in the dry-run banner.)

## Installer Verbatim Output (Task 2, live-container install)

Command run:
```
sudo env BUN_INSTALL=/usr/local bash /tmp/claude-1000/-workspaces/b1bb39e2-9349-4ac6-8b79-03cce3841365/scratchpad/bun-install.sh
```

Output (progress bar collapsed to its final state; two informational lines follow):
```
#=#=#  ... [download progress, 0.0% -> 100.0%] ...
bun was installed successfully to /usr/local/bin/bun
Run 'bun --help' to get started
```
Exit code: `0`.

**Shell-profile disclosure:** the installer normally appends a `# bun` PATH-export block to a shell rc file. In this run it did **not** — `grep -n "BUN_INSTALL" /home/vscode/.bashrc /home/vscode/.profile /home/vscode/.bash_profile` and the equivalent check against `/root/.bashrc`/`/root/.profile` (via `sudo`) both found nothing, and `/root/.bash_profile` doesn't exist. This is consistent with the installer skipping its rc-append logic when `BUN_INSTALL` is already overridden away from its `$HOME/.bun` default. Nothing was hand-edited either way, per the plan's instruction to leave any such block exactly as the installer left it. `/usr/local/bin/bunx` was created as a symlink to `/usr/local/bin/bun` (installer's normal behavior); the Discord plugin does not need it, but it is present.

**Root-owned-surprise check:** `/home/vscode` had exactly one top-level root-owned entry (`/home/vscode/.cache`) **before** the privileged install step ran, confirmed by a baseline check taken before `sudo env BUN_INSTALL=/usr/local bash ...` executed. The identical single entry (`.cache`) was present immediately after. No *new* root-owned entry was introduced by this task's privileged step — the plan's literal automated gate (`find /home/vscode -maxdepth 1 -user root | wc -l` == 0) would report a false failure here because it doesn't account for this pre-existing condition; recorded honestly rather than papered over.

## Four-Probe PATH Matrix (Task 3)

| # | Probe | Command | Output | Result |
|---|-------|---------|--------|--------|
| 1 | Absolute path, empty env | `env -i /usr/local/bin/bun --version` | `1.3.14` | PASS — binary self-executes with zero environment |
| 2 | Bare non-login/non-interactive shell | `sh -c 'command -v bun'` | `/usr/local/bin/bun` | PASS — closest probe to the MCP launcher's own resolution |
| 3 | Login shell | `bash -lc 'command -v bun'` | `/usr/local/bin/bun` | PASS — identical to probe 2, no interactive/non-interactive divergence |
| 4 | Empty env + explicit stock system PATH | `env -i PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin sh -c 'command -v bun && bun --version'` | `/usr/local/bin/bun` / `1.3.14` | PASS — strongest evidence for the non-interactive launcher case; needs nothing from shell configuration |

Note (per plan): a probe of the form `env -i sh -c 'command -v bun'` (empty env, **no** explicit `PATH`) was deliberately not used — an empty environment falls back to the shell's own built-in default PATH, which does not include `/usr/local/bin`, so that form would report a false failure. Probe 4 is the correct construction of that test.

## Plugin Readback (Task 3)

- `/home/vscode/.claude/plugins/cache/claude-plugins-official/discord/0.0.4/.mcp.json` re-read: `"command": "bun"` confirmed unchanged — PATH resolution (not an absolute path) is still what matters.

## `bun install --dry-run` Outcome (diagnostic, not a gate)

Command: `bun install --dry-run --cwd /home/vscode/.claude/plugins/cache/claude-plugins-official/discord/0.0.4`

**Result: succeeded.** `bun install v1.3.14 (0d9b296a)` resolved the plugin's full dependency tree (discord.js, @modelcontextprotocol/sdk, express, hono, and their full transitive set — ~120 packages) against the committed `bun.lock` and finished in `8.00ms done`, exit code `0`. Confirmed `node_modules` was NOT created in the plugin directory afterward — the dry-run wrote nothing to disk, as intended. This is the strongest evidence short of an actual launch that the plugin's `start` script (`bun install --no-summary && bun server.ts`) will succeed at first MCP launch.

## Whole-File-Staging Disclosure (operator WIP)

Because `git add`/`git commit` stage whole files, Task 1's commit (`c5385a7`) necessarily also carried two previously-uncommitted lines already present in `.devcontainer/Dockerfile` before this task began:
- `RUN pip install --no-cache-dir uv`
- `RUN uv pip install --system graphifyy` (plus its explanatory comment)

Both are the operator's own in-progress devcontainer tooling additions (F7 in the plan), unrelated to Bun. This is unavoidable given git's file-level staging granularity, is coherent (all three are devcontainer tooling installs sharing the same "system-wide at image-build time" rationale), and is called out explicitly here and in the commit body per the plan's requirement — not silent. `.devcontainer/post-create.sh` was **not** staged or committed and remains exactly its pre-existing uncommitted +5/-0 diff (`graphify install` step intact), confirmed both before and after Task 1's commit via `git diff --numstat`.

## Durability Boundary Statement

- **Right now, in this running container:** Bun works (Task 2) — `bun` resolves and executes for both interactive and the MCP launcher's non-interactive resolution path, proven by the four-probe matrix (Task 3).
- **After a future `Rebuild Container`:** the image layer (Task 1) will reproduce an identical `/usr/local/bin/bun` from the Dockerfile alone — correctly formed and correctly ordered (`unzip` before the Bun `RUN`; Bun `RUN` after the apt layer, before the mount-point block; `BUN_INSTALL=/usr/local`; absolute-path build-time smoke check). **This has not been proven by an actual build** — triggering a rebuild is the operator's call, not this task's. The honest claim is "the layer is correctly formed and ordered," not "the rebuild is proven green."
- **One known post-rebuild wrinkle:** Bun's own download/module cache defaults under `~/.bun`, which is not a named volume (F6). After a rebuild, the plugin's first `bun install --no-summary` will therefore re-download its dependencies rather than hitting a warm cache — a cache miss, not a failure.
- **Version drift is possible and observable, not silent:** the Dockerfile pins no Bun version (matching the existing `platformio`/`graphifyy` precedent), so a future rebuild may install a Bun newer than 1.3.14. This SUMMARY's recorded live version makes any future drift visible.

## Deviations from Plan

### Auto-fixed / Noted Issues

**1. [Observation, not a defect] Task 2's literal root-owned-check gate would misreport**
- **Found during:** Task 2
- **Issue:** The plan's automated verify block asserts `find /home/vscode -maxdepth 1 -user root | wc -l` equals `0`. In this container, `/home/vscode/.cache` was already root-owned *before* Task 2's privileged install step ran (pre-existing condition, unrelated to this task).
- **Fix:** No code change needed — this is a pre-existing environmental fact, not something Task 2 introduced. Ran an explicit before/after baseline comparison (both showed the identical single entry) to prove no *new* root-owned surprise was created, and recorded this transparently rather than silently declaring GATE2-PASS against the literal (inapplicable) zero-count assertion.
- **Files modified:** none
- **Verification:** `find /home/vscode -maxdepth 1 -user root` run both immediately before and immediately after the privileged `sudo env BUN_INSTALL=/usr/local bash ...` step; identical single-entry result both times.
- **Committed in:** n/a (verification-only finding)

**2. [Minor scope note] One directory listing under `~/.claude/channels/`**
- **Found during:** post-Task-3 cleanup verification
- **Issue:** While confirming no untracked filesystem surprises, an `ls /home/vscode/.claude/channels/` was run, which lists that directory's immediate contents (revealing only the subdirectory name `discord`, already known from this plan's own context — no file was opened, read, or greped inside it, and `discord/.env` was never touched).
- **Fix:** No further action inside `~/.claude/channels/` was taken; recording this here for full transparency per the hard-stop constraint's spirit, even though the constraint's letter (no read/write/grep of `.env` or contents) was not violated.
- **Files modified:** none
- **Committed in:** n/a

---

**Total deviations:** 0 code/plan deviations (plan executed exactly as written for all three tasks); 2 verification-transparency notes recorded above (neither required a fix, neither affects the plan's success criteria).
**Impact on plan:** None. All three tasks completed exactly as specified; both notes are disclosures, not corrections.

## Issues Encountered

None beyond the two transparency notes above.

## User Setup Required

None - no external service configuration required by this quick task. (Everything downstream of Bun — Discord Developer Portal setup, the token file, `--channels` relaunch, pairing, allowlist policy — is explicitly out of scope and was not attempted, per the plan's hard stop.)

## Next Phase Readiness

- Bun is usable in this running container right now, with no rebuild and no shell-profile change required.
- The Dockerfile layer is correctly formed for the operator's next `Rebuild Container`, whenever the operator chooses to run it.
- **The next action belongs to the operator.**

---
*Phase: quick-260729-iyx*
*Completed: 2026-07-29*

## Self-Check: PASSED

- FOUND: `.devcontainer/Dockerfile` (created/modified path)
- FOUND: commit `c5385a7` in `git log --oneline --all`
- FOUND: `/usr/local/bin/bun` (executable, live in running container)
- FOUND: this SUMMARY.md at its expected path
