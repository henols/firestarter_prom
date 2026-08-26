---
last_mapped_commit: e0dc0622d35be57c5a1a57c470a56ec85b0b253f
last_mapped_at: 2026-08-26T20:42:40.949Z
mapped_paths: .claude,.devcontainer,.github,.gitignore,.gitmodules,.vscode,CLAUDE.md
---
# External Integrations

**Analysis Date:** 2026-08-26 (meta-repo / dev-environment layer)
**Prior analysis:** 2026-05-08 (submodule layer — preserved below, not re-verified this run)

---

# Part 1 — Meta-repo integrations (verified 2026-08-26)

## Git remotes & submodules

`.gitmodules` declares two SSH submodule remotes:
- `firestarter` → `git@github.com:henols/firestarter.git`
- `firestarter_app` → `git@github.com:henols/firestarter_app.git`

SSH (not HTTPS) means local submodule operations require an SSH key/agent. CI does **not**
use the submodule remotes — `.github/workflows/catalog-sync-check.yml` checks the sub-repos
out over HTTPS by repo name instead.

## GitHub Actions (meta-repo CI)

**Workflow:** `.github/workflows/catalog-sync-check.yml` (the only one in this repo)

- Runner: `ubuntu-latest`
- Actions consumed: `actions/checkout@v4` (three times — meta plus both sub-repos)
- Cross-repo reads: `henols/firestarter` and `henols/firestarter_app`, at a ref resolved
  by `git ls-remote --exit-code --heads https://github.com/henols/<repo>.git <branch>`,
  falling back to `beta`
- Auth: the default `GITHUB_TOKEN` only; **no repository secrets are referenced**
- Publishes nothing. It only asserts `tools/catalog/messages.toml` byte-identity across
  meta and both sub-repos.
- `workflow_dispatch` is enabled, with no inputs.

## GitHub API / `gh` CLI (agent tooling)

- The `gh` CLI is provisioned by the `ghcr.io/devcontainers/features/github-cli:1`
  devcontainer feature.
- `.claude/skills/devtest-triage/scripts/devtest_issues.py` drives the GitHub **Issues**
  API through `gh` with a fixed argv list (never a shell), for triaging community
  `dev test` chip-validation reports.
- `.claude/skills/devtest-triage/SKILL.md` and
  `.claude/skills/devtest-rootcause/SKILL.md` both instruct `gh issue`/`gh api` usage.
- Auth: whatever credential `gh auth` holds in the container (`~/.config`, a named volume).
  No token is stored in this repo.

## Upstream data oracle — minipro `infoic.xml`

`.claude/skills/devtest-rootcause/scripts/infoic_lookup.py` downloads and caches
(~17.8 MB) a **commit-pinned** upstream catalog:

```
https://gitlab.com/DavidGriffith/minipro/-/raw/a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml
```

The pin must match `build_db.py:MINIPRO_XML_URL` in the host app; the script has a
`--check`/DRIFT mode that fails when the two disagree. Unauthenticated GitLab raw fetch.

## Container image & package registries pulled at build time

`.devcontainer/Dockerfile` / `.devcontainer/devcontainer.json` reach out to:
- **Microsoft Container Registry** — `mcr.microsoft.com/devcontainers/python:3.12`
- **Debian apt repositories** — `udev`, `libusb-1.0-0`, `avrdude`, `unzip`
- **PyPI** — `platformio`, `uv`, and `graphifyy` (the last via `uv pip install --system`)
- **bun.sh** — `curl -fsSL https://bun.sh/install`, installed to `/usr/local`
- **GHCR (devcontainer features)**, digest-pinned in `.devcontainer/devcontainer-lock.json`:
  `ghcr.io/devcontainers/features/github-cli:1`,
  `ghcr.io/devcontainers/features/node:1`,
  `ghcr.io/anthropics/devcontainer-features/claude-code:1`
- **PlatformIO package registry** — via `pio pkg install` in `post-create.sh`
  (AVR toolchain + Arduino framework land in the `firestarter-platformio` volume)
- **VS Code Marketplace** — the five extensions listed in `devcontainer.json`

## Claude Code plugin marketplaces & skill installers

- `.claude/settings.local.json` registers `extraKnownMarketplaces` →
  `claude-plugins-official` from `https://github.com/anthropics/claude-plugins-official.git`,
  and enables `discord@claude-plugins-official`. `post-create.sh` rewrites these entries
  idempotently, since the settings file itself is gitignored.
- `.gitignore` documents two **marketplace-installed, deliberately un-vendored** skills:
  `.claude/skills/find-skills/` (carries `source.json`) and
  `.claude/skills/skill-creator` (installed via
  `npx skills add anthropics/skills@skill-creator`, real files under `.agents/skills/`).
  Reinstall rather than commit them. `skills-lock.json` is the `npx skills` manifest and
  stays local.
- An untracked root `package.json` pins `@mastra/mcp-docs-server` (npm), so npm is a
  further registry in play for MCP docs tooling.

## Discord bot bridge (inbound/outbound messaging)

**Service:** Discord, via the official Claude Code `discord` channel plugin. Its MCP server
runs on Bun.

- State dir: `DISCORD_STATE_DIR=/workspaces/.claude/channels/discord`, set in
  `devcontainer.json` so the token/pairing lives on the host bind mount and survives a
  named-volume wipe. `.claude/` is gitignored, so it is never committed.
- **Credential:** a Discord **bot token** is stored in `.claude/channels/discord/.env`
  (chmod 600 by `post-create.sh`). Never read, quote, or transcribe it.
- Access policy: `.claude/channels/discord/access.json` — keys `dmPolicy`, `allowFrom`,
  `groups`, `pending`; plus a `.claude/channels/discord/approved/` directory.
- **Single-instance gate:** `.devcontainer/discord-singleton.sh` is an `flock` wrapper on
  `/tmp/firestarter-discord-bot.lock` (override: `DISCORD_SINGLETON_LOCK`). Every Claude
  process — including GSD/Agent-spawned workers — would otherwise start its own bot on the
  same token and the gateway connections would collide, scattering inbound DMs.
  First process wins the lock and `exec bun run --shell=bun --silent start`s the plugin;
  the rest `exit 0`. `post-create.sh` repoints the plugin's `.mcp.json` `command`/`args` at
  this wrapper on every rebuild so it survives plugin reinstalls.
- Traffic direction: **inbound** DMs/group messages to the agent, and **outbound** replies.
  Not a webhook — a persistent gateway connection.

## Other agent-runtime services

- **graphify** (`graphifyy` on PyPI, `graphify install` in post-create) — local
  knowledge-graph builder; output at `graphify-out/` and `.planning/graphs/` (both largely
  gitignored).
- **GSD core update check** — `.claude/gsd-core/bin/check-latest-version.cjs` and the
  `.claude/hooks/gsd-check-update*.js` hooks perform a version lookup for the vendored GSD
  runtime (`.claude/gsd-core/VERSION` = `1.6.1`).
- **Researcher fetch cache** — `.planning/research/.cache/` (gitignored) holds
  web/Context7 responses, implying outbound web + Context7 documentation lookups during
  GSD research phases.

## Meta-repo secrets inventory

| Kind | Location | Notes |
|------|----------|-------|
| Discord bot token | `.claude/channels/discord/.env` | gitignored, chmod 600, live |
| GitHub credential | `gh` CLI store under `~/.config` (named volume) | not in repo |
| Claude Code auth | `~/.claude` (named volume `firestarter-claude`) | not in repo |
| CI secrets | none referenced by `.github/workflows/catalog-sync-check.yml` | uses default `GITHUB_TOKEN` |

`.claude/settings.json` declares only `permissions`, `remoteControlAtStartup` and
`autoMode` — no `env` block and no inline keys.

## Webhooks & callbacks (meta-repo)

**Incoming:** none. GitHub Actions triggers are `push`, `pull_request`, and
`workflow_dispatch` — not webhooks the repo receives directly.
**Outgoing:** none. The Discord bridge is a gateway client, not a webhook emitter.

---

# Part 2 — Submodule integrations (from 2026-05-08 analysis; not re-verified this run)

All statements in this part are carried forward verbatim and are
`[unverified in 2026-08-26 scoped remap]`.

## APIs & External Services

**GitHub Releases API:**
- GitHub REST API - Fetches latest firmware release metadata and binary download
  - SDK/Client: `requests` (Python HTTP library)
  - Auth: None (public API, unauthenticated)
  - Endpoint: `https://api.github.com/repos/henols/firestarter/releases/latest`

## Data Storage

**Databases:**
- None (no SQL/NoSQL database)
- EPROM definitions stored as JSON flat files bundled with the package:
  - `firestarter/data/database_generated.json` - Main EPROM definitions
  - `firestarter/data/database_overrides.json` - Default overrides
  - `firestarter/data/pin-maps.json` - Pin mapping configurations

**File Storage:**
- Local filesystem only
- User config/override directory: `~/.firestarter/`
- Firmware binaries downloaded to `~/.firestarter/` on install
- EEPROM on Arduino stores hardware calibration config (persistent across power cycles)

**Caching:**
- None

## Authentication & Identity

**Auth Provider:**
- None - no user authentication
- GitHub API accessed without authentication (public repos, rate-limited at 60 req/hr)

## Monitoring & Observability

**Error Tracking:**
- None (no Sentry, Rollbar, etc.)

**Logs:**
- Python `logging` module with a custom `SingleLineStatusHandler` for single-line status updates in the terminal
- Log output to stdout; verbosity controlled via CLI flags
- Firmware logging via serial debug output (controlled by `SERIAL_DEBUG` build flag, disabled by default)

## CI/CD & Deployment

**Hosting:**
- Python package: PyPI (`https://pypi.org/project/firestarter/`)
- Firmware binaries: GitHub Releases (`.hex` files per board target)

**CI Pipeline:**
- GitHub Actions (both repos — these are the *sub-repos'* workflows, not this meta-repo's)
  - `firestarter_app`: Auto-creates patch release on push to `main`, publishes to PyPI on GitHub release
  - `firestarter` (firmware): Builds all PlatformIO environments on push to `main`, creates GitHub release with `.hex` files
  - Version management via custom Python scripts in `.github/scripts/`
  - Uses `stefanzweifel/git-auto-commit-action` for automated version commits
  - Uses `softprops/action-gh-release` for release creation
  - Uses `pypa/gh-action-pypi-publish` for PyPI publishing

## Environment Configuration

**Required env vars:**
- No required environment variables for runtime operation
- CI secrets: `PYPI_API_TOKEN` (for PyPI publishing in GitHub Actions, sub-repos only)

**Secrets location:**
- GitHub Actions repository secrets (CI only)
- No application-level secrets required

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None (the GitHub API call in `firmware.py` is a pull request for release info, not a webhook)

---

*Meta-repo integration audit: 2026-08-26. Submodule integration audit: 2026-05-08.*
