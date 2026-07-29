#!/usr/bin/env bash
#
# Singleton launcher for the Discord channel plugin's MCP bot.
#
# Every Claude Code process — the interactive session AND every worker/subagent that GSD
# or the Agent tool spawns — initializes MCP and would otherwise each start a Discord bot
# on the SAME token. Multiple gateway connections on one token collide and scatter inbound
# DMs across instances. Claude Code has no supported way to launch a plugin's MCP server in
# the interactive session only, and no reliable env flag distinguishes a worker from the
# main session, so we enforce a single instance here.
#
# The first Claude process to reach this wrapper takes a non-blocking exclusive lock and
# runs the one bot (in practice the long-lived interactive session, since it starts first
# and holds the lock for its lifetime). Every later worker fails the lock and exits 0 —
# which Claude Code treats as "this MCP server produced nothing", i.e. that worker simply
# has no Discord bot. When the lock holder exits, the lock frees for the next session.
#
# Wired in by .devcontainer/post-create.sh, which repoints the plugin's .mcp.json command
# at this script (idempotently, on every rebuild, so it survives plugin reinstalls).
set -uo pipefail

LOCK="${DISCORD_SINGLETON_LOCK:-/tmp/firestarter-discord-bot.lock}"

# Hold the lock on fd 9 for this process's lifetime (released when the bot exits).
exec 9>"$LOCK" 2>/dev/null || exit 0
flock -n 9 || exit 0

# Resolve the plugin root: Claude sets CLAUDE_PLUGIN_ROOT when launching a plugin server;
# fall back to the newest installed version dir so this keeps working across version bumps.
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d "$HOME"/.claude/plugins/cache/claude-plugins-official/discord/*/ 2>/dev/null | sort -V | tail -1)}"
[ -n "${PLUGIN_ROOT:-}" ] || exit 0

cd "$PLUGIN_ROOT" || exit 0
# Same command the plugin's own .mcp.json used (--silent keeps bun install off MCP stdout).
exec bun run --shell=bun --silent start
