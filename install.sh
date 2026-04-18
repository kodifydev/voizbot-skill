#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VOIZBOT_SKILL_BASE_URL:-https://raw.githubusercontent.com/kodifydev/voizbot-skill/main}"
SKILL_ROOT="${HERMES_SKILL_DIR:-$HOME/.hermes/skills/voicebot-phone-calls}"
SCRIPT_DIR="$SKILL_ROOT/scripts"
CONFIG_DIR="${VOIZBOT_CONFIG_DIR:-$HOME/.config/voizbot}"
CONFIG_PATH="$CONFIG_DIR/config.json"

mkdir -p "$SCRIPT_DIR"
mkdir -p "$CONFIG_DIR"

curl -fsSL "$BASE_URL/SKILL.md" -o "$SKILL_ROOT/SKILL.md"
curl -fsSL "$BASE_URL/scripts/voizbot_calls.py" -o "$SCRIPT_DIR/voizbot_calls.py"
chmod +x "$SCRIPT_DIR/voizbot_calls.py"

cat <<EOF
Installed Voizbot skill to:
  $SKILL_ROOT

Next steps:
1. Generate a Voizbot API token in Settings.
2. Save your config to:
  $CONFIG_PATH

Suggested config:
{
  "baseUrl": "https://api.voizbot.com/v1",
  "apiToken": "vb_...",
  "phoneNumberId": "pn_..."
}

Useful commands:
  python3 "$SCRIPT_DIR/voizbot_calls.py" numbers
  python3 "$SCRIPT_DIR/voizbot_calls.py" templates
  python3 "$SCRIPT_DIR/voizbot_calls.py" tools
  python3 "$SCRIPT_DIR/voizbot_calls.py" create --to "+34600111222" --dry-run
EOF
