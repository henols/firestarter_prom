---
phase: quick-260729-iyx
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .devcontainer/Dockerfile
autonomous: true
requirements: [QUICK-260729-iyx]
user_setup: []

must_haves:
  truths:
    - "`bun` resolves to `/usr/local/bin/bun` and executes, in the RUNNING container, right now — no rebuild required for the operator to use Discord."
    - "`bun` resolves for a NON-INTERACTIVE, NON-LOGIN shell under the plain system PATH — because the Discord plugin's `.mcp.json` declares `\"command\": \"bun\"` as a bare name that Claude Code's MCP launcher resolves from PATH, with no rc/profile sourcing."
    - "A `Rebuild Container` reproduces the same binary at the same path from the image layer alone — nothing depends on `~/.bun`, which is NOT a named volume."
    - "The operator's uncommitted `uv` + `graphifyy` Dockerfile lines and the `graphify install` post-create step survive intact — `.devcontainer/post-create.sh` is byte-unchanged."
  artifacts:
    - .devcontainer/Dockerfile
    - /usr/local/bin/bun
  key_links:
    - "apt `unzip` line -> the Bun `RUN` layer: the installer unzips its download, so `unzip` must be installed EARLIER in the Dockerfile than the Bun layer or the build breaks."
    - "`BUN_INSTALL=/usr/local` -> `/usr/local/bin/bun` -> the already-on-PATH system bindir: this is the whole mechanism. Any other install prefix (notably the installer's `$HOME/.bun` default) silently breaks the non-interactive MCP launch and does not survive a rebuild."
    - "Dockerfile layer (durability, needs a rebuild) and live-container install (immediate use) are TWO separate deliverables; neither substitutes for the other."
---

<objective>
Install Bun so the already-installed official Claude Code Discord channel plugin can run its MCP server — durably in the devcontainer image, and immediately in the running container.

Bun is the sole hard blocker. The plugin `discord@claude-plugins-official` v0.0.4 is already present at
`/home/vscode/.claude/plugins/cache/claude-plugins-official/discord/0.0.4/`, and its `.mcp.json` declares
`"command": "bun"` with `args: ["run","--cwd","${CLAUDE_PLUGIN_ROOT}","--shell=bun","--silent","start"]`.
`command -v bun` currently returns nothing in this container, so nothing about Discord can work until that resolves.

Purpose: close the blocker on both axes at once — durability (image layer, effective at the operator's next rebuild)
and immediacy (live install, effective now). Discord mode for this setup is DM-only; no guild/channel work is in scope.

Output: an edited `.devcontainer/Dockerfile` carrying `unzip` + a system-wide Bun layer, a working `/usr/local/bin/bun`
in the running container, and a recorded PATH-resolution matrix proving Bun resolves for the non-interactive shell the
MCP launcher actually uses.
</objective>

<execution_context>
@/workspaces/.claude/gsd-core/workflows/execute-plan.md
@/workspaces/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@/workspaces/CLAUDE.md
@/workspaces/.devcontainer/Dockerfile
@/workspaces/.devcontainer/devcontainer.json

**Working directory for ALL tasks:** `/workspaces` (the meta repo). Current branch is
`gsd/v1.22-at28c-software-data-protection-lifecycle` — **stay on it, do not switch or create a branch.**
Neither sub-repo submodule (`firestarter/`, `firestarter_app/`) is touched by any task in this plan.

**No project skills directory exists** (`/workspaces/.claude/skills` absent) — nothing extra to honor.

**Facts established before planning — do NOT re-derive, do NOT contradict:**

| # | Fact |
|---|------|
| F1 | Discord plugin v0.0.4 already installed; its README names Bun as the sole prerequisite; its `.mcp.json` invokes the bare name `bun`. Its `start` script is `bun install --no-summary && bun server.ts`, so first launch runs `bun install` inside the plugin root. |
| F2 | `bun` is NOT installed. Hard blocker. |
| F3 | `curl` 8.14.1 and `unzip` 6.00 are both present in the running container; `sudo` is passwordless for `vscode`; arch is `x86_64` and `/proc/cpuinfo` reports `avx2`, so the installer selects the standard (non-baseline) Linux x64 build. |
| F4 | `/usr/local/bin` is already on PATH for every shell, including non-login/non-interactive. |
| F5 | `npm` exists at RUNTIME only — it comes from the `ghcr.io/devcontainers/features/node:1` feature, applied AFTER the Dockerfile builds. It does NOT exist during Dockerfile `RUN` steps. Do not reach for it in the Dockerfile. |
| F6 | `devcontainer.json` mounts `/home/vscode/.platformio`, `/home/vscode/.config`, `/home/vscode/.cache/pip`, `/home/vscode/.claude` as named volumes. `/home/vscode/.bun` is NOT one — the installer's default `$HOME/.bun` prefix would be wiped by a rebuild. This is why the prefix is overridden. |
| F7 | `.devcontainer/Dockerfile` (+8/-0) and `.devcontainer/post-create.sh` (+5/-0) both carry UNCOMMITTED operator work-in-progress: the `uv` + `graphifyy` install blocks, and the `graphify install` post-create step. **Integrate alongside them. Do not revert, reorder, drop, or reflow them.** |
| F8 | The Dockerfile's own graphify comment states the precedent this plan follows verbatim: *"Installed system-wide at image-build time (as root) so the entry point lands on PATH and there are no runtime cache/permission issues in named volumes."* |

**Why the Dockerfile layer alone is not enough, and why the live install alone is not enough:** the layer only takes
effect at the operator's next `Rebuild Container`, and **this plan must not trigger or request a rebuild — the operator
decides when to rebuild.** The live install is therefore what makes Discord usable today; the layer is what makes it
survive. Ship both.

**Explicitly OUT OF SCOPE — these are operator-only and MUST NOT be attempted by any task:** Discord Developer Portal
work (Message Content Intent, Public Bot toggle, bot token, server invite); reading/writing/validating
`~/.claude/channels/discord/.env` (a token file already exists there and its contents are deliberately unread);
relaunching Claude Code with `--channels`; the pairing DM or `/discord:access pair <code>`; setting
`/discord:access policy allowlist` (this MUST come only AFTER pairing — setting it early makes pairing impossible);
creating or editing `~/.claude/channels/discord/access.json`. Also out of scope: any container rebuild, and any edit
to `.devcontainer/post-create.sh` or `.devcontainer/devcontainer.json`.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add unzip + a system-wide Bun layer to the devcontainer Dockerfile</name>
  <files>.devcontainer/Dockerfile</files>
  <action>
Make exactly two scoped `Edit` calls to `/workspaces/.devcontainer/Dockerfile`. Never use `Write` on this file — it
carries the operator's uncommitted work-in-progress (F7) and a whole-file overwrite risks reflowing or dropping it.

EDIT A — extend the existing `apt-get install` list. The current list is `udev`, `libusb-1.0-0`, `avrdude`. Append a
fourth entry `unzip` as the last item, matching the existing four-space continuation indent and backslash style. Also
append one comment line under the existing "PlatformIO requires udev rules..." comment stating that `unzip` is needed
by the Bun installer added below and is declared here rather than assumed from the base image. Rationale: F3 confirms
`unzip` is present in the *running* container, but that container has devcontainer features applied on top — the base
image is not guaranteed to ship it, and the Bun installer unzips its download. `curl` is deliberately NOT added: it is
part of the `mcr.microsoft.com/devcontainers/python:3.12` base image, and if it ever were not, the Bun `RUN` below
fails loudly at build time rather than silently.

EDIT B — insert a new Bun `RUN` layer. Position: AFTER the existing `RUN uv pip install --system graphifyy` line, and
BEFORE the "Pre-create persistent volume mount points..." comment block. This ordering matters twice: it must sit
after the apt layer from Edit A (so `unzip` exists), and it must not disturb the `mkdir`/`chown` block that
initialises the named-volume mount points.

The inserted block is a comment header plus one `RUN`. The comment must record, in the graphify precedent's voice
(F8), four things: (1) Bun is required by the official Claude Code Discord channel plugin, whose MCP server runs on
Bun; (2) it is installed system-wide as root at image-build time with `BUN_INSTALL=/usr/local` so the binary lands at
`/usr/local/bin/bun`, which is already on PATH for every shell — including the non-interactive, non-login shell that
Claude Code's MCP launcher uses, since the plugin's `.mcp.json` declares the bare command name `bun`; (3) nothing is
written to `~/.bun`, which is not a named volume and would not survive a rebuild (F6); (4) the node feature's package
manager is unavailable at Dockerfile build time, which is why the official installer script is used instead (F5) —
state this by referring to the node devcontainer feature, without writing out any install command for it.

The `RUN` itself is a two-line continuation. First line: pipe the official installer into a `bash` invocation carrying
the prefix override — `curl -fsSL https://bun.sh/install | BUN_INSTALL=/usr/local bash \`. Second line:
`    && /usr/local/bin/bun --version`. Use the ABSOLUTE path for that build-time smoke check, not the bare name: it
proves both that the binary landed at the exact expected path and that it actually executes on this CPU (an
`Illegal instruction` here would be the AVX2/baseline-variant class of failure, which F3 says should not arise), and
it is immune to shell command hashing within the same `RUN`.

Do not pin a Bun version. This matches the in-file precedent (`graphifyy` and `platformio` are both unpinned). Record
the consequence honestly in the SUMMARY: a future rebuild may install a newer Bun than the live container gets in
Task 2, so Task 3 records the live version to make that drift visible rather than invisible.

Then commit. Use the GSD commit helper with an EXPLICIT `--files` list naming only `.devcontainer/Dockerfile` — a bare
commit stages everything, which would sweep in `.planning/` churn, the untracked scratch directories, and possibly a
submodule gitlink. Message: `chore(devcontainer): install Bun system-wide for the Discord channel plugin`.

**State this plainly in the commit body and in the SUMMARY:** because git stages whole files, this commit necessarily
also carries the operator's previously-uncommitted in-file `uv` + `graphifyy` lines (F7). That is unavoidable and
coherent (all three are devcontainer tooling installs), but it must not be silent. `.devcontainer/post-create.sh` is
NOT staged and stays uncommitted with its `graphify install` step intact.
  </action>
  <verify>
    <automated>
D=/workspaces/.devcontainer/Dockerfile
U=$(grep -n '^ *unzip' "$D" | head -1 | cut -d: -f1); B=$(grep -n 'bun.sh/install' "$D" | head -1 | cut -d: -f1); G=$(grep -n 'graphifyy' "$D" | head -1 | cut -d: -f1)
test -n "$U" && test -n "$B" && test -n "$G" && test "$U" -lt "$B" && test "$G" -lt "$B" || { echo GATE1-ORDER-FAIL; exit 1; }
grep -q 'BUN_INSTALL=/usr/local' "$D" && grep -q '/usr/local/bin/bun --version' "$D" || { echo GATE1-BUN-FAIL; exit 1; }
grep -q 'pip install --no-cache-dir uv' "$D" && grep -q 'uv pip install --system graphifyy' "$D" && grep -q 'chown -R vscode:vscode' "$D" || { echo GATE1-WIP-CLOBBERED; exit 1; }
P=$(git -C /workspaces diff --numstat -- .devcontainer/post-create.sh | cut -f1,2 | tr -d '[:blank:]')
test "$P" = "50" || { echo "GATE1-POSTCREATE-TOUCHED: $P"; exit 1; }
test "$(git -C /workspaces show --name-only --format= HEAD | tr -d '[:space:]')" = ".devcontainer/Dockerfile" || { echo GATE1-COMMIT-SCOPE-FAIL; exit 1; }
echo GATE1-PASS
    </automated>
  </verify>
  <done>
`unzip` appears in the apt list at a line number strictly lower than the Bun `RUN`; the Bun layer sits between the
graphify layer and the mount-point `mkdir` block; `BUN_INSTALL=/usr/local` and the absolute-path `--version` smoke
check are both present; all three operator WIP markers (`uv`, `graphifyy`, `chown -R vscode:vscode`) still present;
`post-create.sh` still shows exactly its pre-existing +5/-0 uncommitted diff; HEAD commit touches exactly one file.
  </done>
</task>

<task type="auto">
  <name>Task 2: Install Bun into the RUNNING container at the same prefix</name>
  <files>/usr/local/bin/bun (container filesystem, not git-tracked)</files>
  <action>
Install Bun into the live container so the operator can use Discord without waiting for a rebuild. Target the exact
same prefix as the Dockerfile layer (`/usr/local`) so the live container and a future rebuilt container are
behaviourally identical — a divergence here would make "works today, broken after rebuild" (or the reverse) possible.

Root is required to write into `/usr/local/bin`, and `sudo` strips the environment, so the prefix override cannot be a
plain `VAR=... sudo ...` prefix. Two steps:

1. Download the installer to the session scratchpad directory
   (`/tmp/claude-1000/-workspaces/b1bb39e2-9349-4ac6-8b79-03cce3841365/scratchpad/bun-install.sh`) with
   `curl -fsSL https://bun.sh/install -o <path>`. Do not pipe straight into `sudo bash` — staging the script keeps
   the privileged step reviewable and lets the download failure mode be distinguished from the install failure mode.
2. Run it as root with the prefix injected through `env`: `sudo env BUN_INSTALL=/usr/local bash <path>`.

Capture the installer's full stdout/stderr into the SUMMARY verbatim — including whatever it says about shell profile
files. The installer may append a `# bun` block exporting `BUN_INSTALL`/`PATH` to a shell rc file. **Leave any such
block exactly as the installer left it.** It is inert here: `/usr/local/bin` is already on PATH (F4), so the export is
a harmless duplicate, and the whole point of this prefix is that no rc sourcing is needed. Do not hand-edit rc files
to "clean it up" and do not add PATH exports anywhere.

After the install, record three things: the exact version string, the resolved real path, and whether `bunx` was
created alongside `bun` (the installer normally symlinks it; the Discord plugin does not need `bunx`, but its
presence/absence is worth recording).

Then confirm the privileged step left no root-owned surprises in the operator's home directory — `sudo` can preserve
`HOME`, so it is worth actually checking rather than assuming. Nothing under `/home/vscode` should have become
root-owned at the top level.

Do NOT run `bun install` inside the Discord plugin directory in this task, do NOT launch the plugin's MCP server, and
do NOT touch anything under `~/.claude/channels/`.
  </action>
  <verify>
    <automated>
test -x /usr/local/bin/bun || { echo GATE2-NOT-EXECUTABLE; exit 1; }
/usr/local/bin/bun --version || { echo GATE2-DOES-NOT-RUN; exit 1; }
ls -l /usr/local/bin/bun /usr/local/bin/bunx 2>&1 | head -5
R=$(find /home/vscode -maxdepth 1 -user root | wc -l); test "$R" = "0" || { echo "GATE2-ROOT-OWNED-IN-HOME: $R"; find /home/vscode -maxdepth 1 -user root; exit 1; }
echo GATE2-PASS
    </automated>
  </verify>
  <done>
`/usr/local/bin/bun` exists, is executable, and prints a version string when run. No top-level entry under
`/home/vscode` is root-owned. The installed version string and the installer's full output are recorded in the
SUMMARY.
  </done>
</task>

<task type="auto">
  <name>Task 3: Prove Bun resolves for the non-interactive shell the MCP launcher uses, and record the prerequisite readback</name>
  <files>(verification only — no files modified)</files>
  <action>
The failure mode this task exists to rule out: a Bun install that works when *you* type `bun` in your terminal but is
invisible to the process that actually needs it. Claude Code launches the plugin's MCP server non-interactively from
`.mcp.json`'s bare `"command": "bun"` — no login shell, no `.bashrc`, no `.profile`. An interactive-shell-only PATH
would be a latent failure that passes a naive check.

Run all four probes and record every one's exact output in the SUMMARY as a small matrix (probe -> output):

1. `env -i /usr/local/bin/bun --version` — absolute path, COMPLETELY empty environment. Proves the binary
   self-executes with no PATH, no HOME, no shell involvement at all.
2. `sh -c 'command -v bun'` — bare non-login, non-interactive POSIX shell inheriting the current environment. Must
   print `/usr/local/bin/bun`. This is the probe closest to the MCP launcher's own resolution.
3. `bash -lc 'command -v bun'` — login shell. Must also print `/usr/local/bin/bun`. If probes 2 and 3 disagree, the
   install landed somewhere that only a profile-sourcing shell can see, and the task has FAILED even though `bun`
   "works" in the terminal.
4. `env -i PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin sh -c 'command -v bun && bun --version'`
   — empty environment plus only the stock system PATH. This is the strongest available evidence for the
   non-interactive launcher case: it proves resolution needs nothing from the operator's shell configuration.

Note explicitly in the SUMMARY that a probe of the form `env -i sh -c 'command -v bun'` (empty env, NO explicit PATH)
is deliberately NOT used: an empty environment leaves the shell falling back to its built-in default PATH, which does
not include `/usr/local/bin`, so that probe would report a false failure. Probe 4 is the correct form of that test.

Then do one read-only prerequisite readback against the already-installed plugin, WITHOUT launching it:

- Re-read `/home/vscode/.claude/plugins/cache/claude-plugins-official/discord/0.0.4/.mcp.json` and confirm in the
  SUMMARY that the command is still the bare name `bun` (i.e. PATH resolution, not an absolute path, is what matters).
- Run `bun install --dry-run` with `--cwd` pointed at that plugin directory. `--dry-run` resolves the plugin's
  `bun.lock` dependencies WITHOUT writing `node_modules`, which is the exact thing the plugin's `start` script
  (`bun install --no-summary && bun server.ts`) will do at first launch. Treat this as a DIAGNOSTIC, not a gate:
  record the outcome either way. If it succeeds, the prerequisite chain is proven end to end short of launching. If
  it fails (network, registry, lockfile), record the verbatim error as a finding for the operator — it does not
  invalidate Tasks 1 and 2, and it must not be papered over.

Finally, state the durability boundary explicitly in the SUMMARY so the operator is not misled: Discord works in THIS
container now (Task 2); it will keep working after a `Rebuild Container` because of the image layer (Task 1); the
layer is unverified-by-build because building it is the operator's call, so the honest claim is "the layer is
correctly formed and ordered", not "the rebuild is proven green". Also name the one known post-rebuild wrinkle: Bun's
own download cache defaults under `~/.bun`, which is not a named volume, so the plugin's first `bun install` after a
rebuild re-downloads — a cache miss, not a failure.

**Hard stop.** Do not proceed past this into any Discord setup step. Everything downstream — the Developer Portal
intents, the token file, relaunching Claude Code with `--channels`, the pairing DM, `/discord:access pair`, and the
allowlist policy (which MUST NOT be set before pairing succeeds, or pairing becomes impossible) — is operator-only and
outside this plan. End the SUMMARY with a one-line note that the next action belongs to the operator, without
enumerating it as work performed or work pending on Claude's side.
  </action>
  <verify>
    <automated>
set -e
env -i /usr/local/bin/bun --version
sh -c 'command -v bun'
bash -lc 'command -v bun'
env -i PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin sh -c 'command -v bun && bun --version'
grep -q '"command": "bun"' /home/vscode/.claude/plugins/cache/claude-plugins-official/discord/0.0.4/.mcp.json
echo GATE3-PASS
    </automated>
  </verify>
  <done>
All four PATH probes succeed and are recorded as a matrix in the SUMMARY; probes 2 and 3 both print
`/usr/local/bin/bun` (no interactive-vs-non-interactive divergence); the plugin's `.mcp.json` bare-`bun` command is
confirmed unchanged; the `bun install --dry-run` outcome is recorded verbatim whether it passed or failed; the
durability boundary and the `~/.bun` cache wrinkle are both stated; no Discord setup step was attempted.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| public internet -> root shell in image build | `curl https://bun.sh/install` output is executed by `bash` as root during `docker build` |
| public internet -> root shell in live container | the same installer script is executed by `sudo bash` in Task 2 |
| npm registry -> plugin directory | the plugin's `start` script runs `bun install` against `bun.lock` inside `~/.claude/plugins/cache/...` at first MCP launch |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-iyx-01 | Tampering | `curl \| bash` of the Bun installer, as root, in the Dockerfile layer | medium | accept | Official upstream installer over HTTPS from `bun.sh` — the exact command the plugin's own README prescribes. `curl -fsSL` fails on a bad TLS chain or non-2xx, and the chained `/usr/local/bin/bun --version` fails the build if the payload did not produce a working binary. No third-party mirror, no unpinned redirect target beyond bun.sh's own. Same trust posture the repo already accepts for `pip install platformio` and `uv pip install --system graphifyy`. |
| T-iyx-02 | Tampering | `sudo env ... bash <staged script>` in the live container | medium | mitigate | Installer is downloaded to the scratchpad as a FILE first and executed as a separate, reviewable step rather than piped straight into `sudo bash`; the privileged command names an on-disk path, so what runs as root is inspectable. Post-step check asserts no top-level entry under `/home/vscode` became root-owned. |
| T-iyx-03 | Elevation of Privilege | writing into `/usr/local/bin` as root | low | accept | Deliberate and precedented (F8): a system-wide bindir is what makes the binary resolvable to a non-interactive launcher. The alternative (`~/.bun`) trades this away for a PATH that only works in a configured interactive shell AND does not survive a rebuild (F6). |
| T-iyx-04 | Tampering | unpinned Bun version | low | accept | Matches the in-file precedent for `platformio`/`graphifyy`. Mitigated by observability, not by pinning: Task 3 records the exact installed version so live-vs-rebuilt drift is visible rather than silent. |
| T-iyx-05 | Information Disclosure | the existing Discord bot token at `~/.claude/channels/discord/.env` | high | mitigate | Out of scope BY CONSTRUCTION — no task reads, writes, validates, or greps that path or anything under `~/.claude/channels/`. The token is never loaded into context, and no task output can echo it. |
| T-iyx-06 | Tampering | npm-registry dependency resolution at the plugin's first `bun install` | medium | mitigate | Task 3 uses `--dry-run` only: dependencies are resolved against the plugin's committed `bun.lock` with nothing written to `node_modules`. The real install remains the plugin's own, at the operator's own launch, governed by its lockfile. |
</threat_model>

<verification>
1. `.devcontainer/Dockerfile`: `unzip` present and ordered BEFORE the Bun `RUN`; Bun layer positioned between the
   graphify layer and the mount-point `mkdir` block; `BUN_INSTALL=/usr/local` present; absolute-path build-time smoke
   check present.
2. Operator WIP intact: `uv`, `graphifyy`, and the `chown -R vscode:vscode` block all still in the Dockerfile;
   `.devcontainer/post-create.sh` byte-unchanged (still exactly +5/-0 uncommitted).
3. Commit scope: HEAD touches exactly `.devcontainer/Dockerfile` — no `.planning/` churn, no submodule gitlink.
4. Live container: `/usr/local/bin/bun` exists, is executable, prints a version.
5. PATH matrix: all four probes pass; `sh -c 'command -v bun'` and `bash -lc 'command -v bun'` both resolve to
   `/usr/local/bin/bun`; the stock-system-PATH-with-empty-env probe resolves and runs.
6. Plugin readback: `.mcp.json` still declares the bare `bun` command; `bun install --dry-run` outcome recorded
   verbatim (pass or fail).
7. Nothing under `~/.claude/channels/` was read, written, or listed; no container rebuild was triggered or requested.
</verification>

<success_criteria>
- Bun is usable in the running container right now, with no rebuild and no shell-profile change.
- Bun resolves for a non-interactive, non-login shell under the stock system PATH — proven, not assumed.
- A future `Rebuild Container` reproduces the same binary at the same path from the image layer alone.
- The operator's uncommitted devcontainer work-in-progress survives, and the commit that carries it says so.
- Zero Discord setup steps attempted; the allowlist policy in particular is untouched.
</success_criteria>

<output>
Create `.planning/quick/260729-iyx-install-bun-in-devcontainer-to-enable-di/260729-iyx-SUMMARY.md` when done.
It must include: the installed Bun version string, the installer's verbatim output, the four-probe PATH matrix, the
`bun install --dry-run` outcome, the whole-file-staging disclosure for the operator's WIP lines, and the durability
boundary statement (layer correctly formed vs rebuild not built).
</output>
