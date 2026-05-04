# Voizbot Skill

Public skill bundle for AI agents that need to place and inspect Voizbot outbound phone calls through the multitenant public API.

## Included

- `SKILL.md` — publishable skill definition in the expected skills.sh-style format
- `scripts/voizbot_calls.py` — standalone Python CLI for the Voizbot public API
- `install.sh` — standalone fallback installer for environments without the skills CLI
- `examples/config.example.json` — minimal local config example

## Install

```bash
npx skills add kodifydev/voizbot-skill
```

## Fallback installer

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/kodifydev/voizbot-skill/main/install.sh)
```

## Local config

Create `~/.config/voizbot/config.json`:

```json
{
  "baseUrl": "https://api.voizbot.com/v1",
  "apiToken": "vb_...",
  "phoneNumberId": "pn_..."
}
```

## Useful commands

```bash
python3 ./scripts/voizbot_calls.py numbers
python3 ./scripts/voizbot_calls.py templates
python3 ./scripts/voizbot_calls.py tools
python3 ./scripts/voizbot_calls.py create --to "+346****0000" --dry-run
```

Run these commands from the installed `voizbot-phone-calls` skill folder.

## Notes

- The skill identifier remains `voizbot-phone-calls` to match the existing Voizbot public bundle slug.
- The API base is `https://api.voizbot.com/v1`.
- The installer and script can be used standalone without the full Voizbot monorepo.
- Marketplace categories: Communication, Speech & Transcription, Productivity & Tasks, AI & LLMs.
- Short listing description: Voizbot lets AI agents place, inspect, and audit outbound phone calls via the Voizbot API.
