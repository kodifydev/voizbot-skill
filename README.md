# Voizbot Skill

Public skill bundle for AI agents that need to place and inspect Voizbot outbound phone calls through the multitenant public API.

## Included

- `SKILL.md` — publishable skill definition in the expected skills.sh-style format
- `scripts/voizbot_calls.py` — standalone Python CLI for the Voizbot public API
- `install.sh` — installer that drops the skill into `~/.hermes/skills/voicebot-phone-calls`
- `examples/config.example.json` — minimal local config example

## Quick install

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
python3 ~/.hermes/skills/voicebot-phone-calls/scripts/voizbot_calls.py numbers
python3 ~/.hermes/skills/voicebot-phone-calls/scripts/voizbot_calls.py templates
python3 ~/.hermes/skills/voicebot-phone-calls/scripts/voizbot_calls.py tools
python3 ~/.hermes/skills/voicebot-phone-calls/scripts/voizbot_calls.py create --to "+34600000000" --dry-run
```

## Notes

- The skill identifier remains `voicebot-phone-calls` to match the existing Voizbot public bundle slug.
- The API base is `https://api.voizbot.com/v1`.
- The installer and script can be used standalone without the full Voizbot monorepo.
