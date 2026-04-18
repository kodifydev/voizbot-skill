---
name: voicebot-phone-calls
description: Place and inspect Voizbot outbound phone calls through the multitenant public API when the user wants an agent to call a person or business, follow up a call, or review its transcript and outcome.
version: 2.0.0
---

# Voizbot Phone Calls

Use this skill when the user wants the agent to call a person or business through Voizbot, or when they need the current status, transcript, or outcome of an existing call.

This version is for the multitenant public API. Do not use the legacy gateway token workflow.

## What changed

- Auth is now the Voizbot API token generated in Settings.
- The public API base is `https://api.voizbot.com/v1`.
- Outbound calls require `phoneNumberId`.
- Calls, templates, tools, transcripts, and phone numbers are organization-scoped.
- The returned `jobId` is the call id you can reuse with the read endpoints.

## Requirements

Before placing calls, make sure all of this is true:

1. The organization already has a valid Voizbot API token.
2. At least one phone number exists in Voizbot.
3. If the call needs a template or function tools, they are already created in Voizbot.

## Recommended local config

Create `~/.config/voizbot/config.json`:

```json
{
  "baseUrl": "https://api.voizbot.com/v1",
  "apiToken": "vb_...",
  "phoneNumberId": "pn_..."
}
```

The bundled script also accepts environment variables:

- `VOIZBOT_API_BASE_URL`
- `VOIZBOT_API_TOKEN`
- `VOIZBOT_PHONE_NUMBER_ID`
- `VOIZBOT_CONFIG`

CLI arguments override config and env vars.

## Core workflow

1. Confirm the call target and objective.
2. If needed, inspect available resources first:
   - `numbers` to discover phone numbers and copy a `phoneNumberId`
   - `templates` to find outbound templates
   - `tools` to find reusable function tools
3. Build a short, explicit call prompt.
4. Launch the call with `create`.
5. Keep the returned `jobId` / call id.
6. Poll `call <id>` until the call is finished if the user wants the result.
7. Use `transcript <id>` when you need the full transcript payload.
8. Summarize the outcome in plain language.

## Prompt guidance

Keep the prompt practical and narrow. Usually include:

- who the assistant is
- the concrete goal
- relevant context
- hard constraints
- the exact close condition before ending the call

Pattern:

```text
You are Juan's assistant calling on his behalf.
Goal: confirm an appointment for next week.
Context: Juan is available Tuesday after 16:00 and Wednesday before 13:00.
Constraints: do not commit to any other time; if there is no slot, ask for the earliest alternative.
Close condition: repeat the final date, local time, and next step before ending the call.
```

## Script commands

### List phone numbers

```bash
python3 ~/.hermes/skills/voicebot-phone-calls/scripts/voizbot_calls.py numbers
```

Use this first if you do not already know the `phoneNumberId`.

### List outbound templates

```bash
python3 ~/.hermes/skills/voicebot-phone-calls/scripts/voizbot_calls.py templates
```

### List function tools

```bash
python3 ~/.hermes/skills/voicebot-phone-calls/scripts/voizbot_calls.py tools
```

### Start a call

```bash
python3 ~/.hermes/skills/voicebot-phone-calls/scripts/voizbot_calls.py create \
  --to "+34600111222" \
  --phone-number-id "pn_123" \
  --template-id "out_tpl_sales" \
  --extra-system-prompt "If they agree, offer Tuesday at 18:30 first." \
  --meta leadId=lead_7821 \
  --meta owner=Juan
```

Useful options:

- `--system-prompt`
- `--system-prompt-file`
- `--extra-system-prompt`
- `--extra-system-prompt-file`
- `--template-id`
- `--voice-model`
- `--function-tool-id`
- `--extra-function-tool-id`
- `--custom-tools-file`
- `--meta KEY=VALUE`
- `--metadata-file`
- `--dry-run`

### List recent calls

```bash
python3 ~/.hermes/skills/voicebot-phone-calls/scripts/voizbot_calls.py calls --filter recent --limit 10
```

### Get one call

```bash
python3 ~/.hermes/skills/voicebot-phone-calls/scripts/voizbot_calls.py call call_abc123
```

### Get one transcript

```bash
python3 ~/.hermes/skills/voicebot-phone-calls/scripts/voizbot_calls.py transcript call_abc123
```

## Monitoring guidance

- For active calls, avoid tight polling loops.
- Start with waits around 45-60 seconds.
- If the call is still ringing or clearly ongoing, keep waits long.
- If the user wants the final answer without asking again, delegate monitoring to a subagent that polls until the call reaches a final status.
- Final statuses usually include `completed`, `busy`, `no-answer`, `failed`, or `canceled`.

## Reporting back to the user

When the call is still running, report:

- current status
- elapsed time if visible
- whether there is already transcript data

When the call is finished, report:

- final status
- the concrete agreement, appointment, or blocker
- any exact date/time/price mentioned
- the next action the user should know

If the transcript contains a specific commitment, quote it clearly.

## Safety notes

- Do not place a real call unless the user explicitly asked for that call.
- If the phone number, target person, or objective is unclear, stop and ask.
- Prefer `--dry-run` if you only need to validate payload assembly.
- Prefer the public Voizbot API and this script over legacy `/calls/jobs` routes and old gateway tokens.
