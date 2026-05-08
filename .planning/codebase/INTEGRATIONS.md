# External Integrations

**Analysis Date:** 2026-05-08

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
- GitHub Actions (both repos)
  - `firestarter_app`: Auto-creates patch release on push to `main`, publishes to PyPI on GitHub release
  - `firestarter` (firmware): Builds all PlatformIO environments on push to `main`, creates GitHub release with `.hex` files
  - Version management via custom Python scripts in `.github/scripts/`
  - Uses `stefanzweifel/git-auto-commit-action` for automated version commits
  - Uses `softprops/action-gh-release` for release creation
  - Uses `pypa/gh-action-pypi-publish` for PyPI publishing

## Environment Configuration

**Required env vars:**
- No required environment variables for runtime operation
- CI secrets: `PYPI_API_TOKEN` (for PyPI publishing in GitHub Actions)

**Secrets location:**
- GitHub Actions repository secrets (CI only)
- No application-level secrets required

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None (the GitHub API call in `firmware.py` is a pull request for release info, not a webhook)

---

*Integration audit: 2026-05-08*
