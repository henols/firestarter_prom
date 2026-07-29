#!/usr/bin/env bash
set -e

echo "=== Generating platformio.ini wrapper ==="
python3 /workspaces/.devcontainer/gen-platformio-ini.py

echo "=== Installing Python CLI (dev mode) ==="
pip install -e /workspaces/firestarter_app

echo "=== Initialising PlatformIO project dependencies ==="
cd /workspaces/firestarter && pio pkg install

echo "=== Installing graphify skill (writes into ~/.claude volume) ==="
# graphify itself is installed in the image (Dockerfile); this step installs the
# skill/references into the ~/.claude named volume, which is only mounted at runtime.
graphify install

echo "=== Provisioning Discord bridge state (durable: lives on the host bind mount) ==="
# The Discord channel plugin's bun MCP server is installed via the Dockerfile (bun) and
# launched on demand by Claude Code — it is deliberately NOT started here. A second
# instance would collide with Claude Code's own bot on the same token (see the multi-
# instance failure mode we hit). This step only makes the plugin's *state* durable:
# DISCORD_STATE_DIR (set in devcontainer.json) points at the workspace bind mount, so the
# bot token + pairing survive even a named-volume wipe, and .claude/ is gitignored so the
# token is never committed.
DISCORD_STATE_DIR="/workspaces/.claude/channels/discord"
mkdir -p "$DISCORD_STATE_DIR/approved"
# One-time migration: carry an existing token/pairing over from the legacy ~/.claude
# volume location the first time this runs, so pairing is not lost on the switch.
if [ -f "$HOME/.claude/channels/discord/.env" ] && [ ! -f "$DISCORD_STATE_DIR/.env" ]; then
  cp -a "$HOME/.claude/channels/discord/." "$DISCORD_STATE_DIR/"
  echo "  migrated token/access from ~/.claude volume -> workspace"
fi
[ -f "$DISCORD_STATE_DIR/.env" ] && chmod 600 "$DISCORD_STATE_DIR/.env"
echo "  state dir: $DISCORD_STATE_DIR (token present: $([ -f "$DISCORD_STATE_DIR/.env" ] && echo yes || echo NO — run /discord:configure))"

echo "=== Ensuring Discord plugin enabled + marketplace known (config-as-code) ==="
# settings.local.json lives on the workspace bind mount (survives a volume wipe) but is
# gitignored, so this tracked step regenerates the required entries idempotently — making
# the plugin setup reproducible on a fresh clone, not just persisted locally.
python3 - <<'PYEOF'
import json, os
p = "/workspaces/.claude/settings.local.json"
os.makedirs(os.path.dirname(p), exist_ok=True)
try:
    d = json.load(open(p))
except (FileNotFoundError, ValueError):
    d = {}
d.setdefault("enabledPlugins", {})["discord@claude-plugins-official"] = True
d.setdefault("extraKnownMarketplaces", {})["claude-plugins-official"] = {
    "source": {"source": "git", "url": "https://github.com/anthropics/claude-plugins-official.git"}
}
with open(p, "w") as f:
    json.dump(d, f, indent=2)
    f.write("\n")
print("  ensured enabledPlugins.discord + extraKnownMarketplaces.claude-plugins-official")
PYEOF

echo "=== Done ==="
