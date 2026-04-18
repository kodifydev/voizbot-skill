#!/usr/bin/env python3
"""CLI client for the Voizbot multitenant public API."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib import error, parse, request

DEFAULT_BASE_URL = "https://api.voizbot.com/v1"
DEFAULT_CONFIG_PATH = Path.home() / ".config" / "voizbot" / "config.json"


def normalize_base_url(value: str | None) -> str:
    raw = (value or "").strip().rstrip("/")
    if not raw:
        return DEFAULT_BASE_URL
    if raw.endswith("/v1"):
        return raw
    return raw + "/v1"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def load_file_json(path: str | None) -> Any:
    if not path:
        return None
    return read_json(Path(path))


def parse_scalar(value: str) -> Any:
    lower = value.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    if lower == "null":
        return None
    try:
        if value.startswith("0") and value != "0" and not value.startswith("0."):
            raise ValueError
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def parse_metadata(values: list[str]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Invalid --meta value '{value}'. Expected KEY=VALUE")
        key, raw = value.split("=", 1)
        key = key.strip()
        if not key:
            raise SystemExit(f"Invalid --meta key in '{value}'")
        metadata[key] = parse_scalar(raw)
    return metadata


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = read_json(path)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in config file {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Config file {path} must contain a JSON object")
    return data


def resolve_runtime(args: argparse.Namespace) -> dict[str, Any]:
    config_path = Path(args.config or os.getenv("VOIZBOT_CONFIG") or DEFAULT_CONFIG_PATH)
    config = load_config(config_path)

    base_url = normalize_base_url(
        args.base_url
        or os.getenv("VOIZBOT_API_BASE_URL")
        or config.get("baseUrl")
        or config.get("apiBaseUrl")
    )
    api_token = (
        args.api_token
        or os.getenv("VOIZBOT_API_TOKEN")
        or config.get("apiToken")
    )
    phone_number_id = (
        getattr(args, "phone_number_id", None)
        or os.getenv("VOIZBOT_PHONE_NUMBER_ID")
        or config.get("phoneNumberId")
    )

    if not api_token:
        raise SystemExit(
            "Missing Voizbot API token. Pass --api-token, set VOIZBOT_API_TOKEN, or add apiToken to ~/.config/voizbot/config.json"
        )

    return {
        "base_url": base_url,
        "api_token": api_token,
        "phone_number_id": phone_number_id,
        "config_path": str(config_path),
    }


def make_request(
    method: str,
    url: str,
    api_token: str,
    *,
    json_body: dict[str, Any] | None = None,
    timeout: int = 30,
) -> Any:
    headers = {"Authorization": f"Bearer {api_token}"}
    data = None
    if json_body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(json_body).encode()

    req = request.Request(url, data=data, method=method, headers=headers)

    try:
        with request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode()
            return json.loads(body) if body else {"ok": True}
    except error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {"raw": body}
        raise SystemExit(
            json.dumps(
                {
                    "ok": False,
                    "status": exc.code,
                    "url": url,
                    "error": payload,
                },
                ensure_ascii=False,
                indent=2,
            )
        ) from exc


def read_text_file(path: str | None) -> str | None:
    if not path:
        return None
    return Path(path).read_text()


def merge_text(primary: str | None, file_value: str | None) -> str | None:
    return file_value if file_value is not None else primary


def cmd_numbers(args: argparse.Namespace) -> Any:
    runtime = resolve_runtime(args)
    return make_request("GET", f"{runtime['base_url']}/phone-numbers", runtime["api_token"], timeout=args.timeout)


def cmd_templates(args: argparse.Namespace) -> Any:
    runtime = resolve_runtime(args)
    return make_request("GET", f"{runtime['base_url']}/outbound-templates", runtime["api_token"], timeout=args.timeout)


def cmd_tools(args: argparse.Namespace) -> Any:
    runtime = resolve_runtime(args)
    return make_request("GET", f"{runtime['base_url']}/function-tools", runtime["api_token"], timeout=args.timeout)


def cmd_calls(args: argparse.Namespace) -> Any:
    runtime = resolve_runtime(args)
    query = parse.urlencode({"limit": args.limit, "filter": args.filter})
    return make_request("GET", f"{runtime['base_url']}/calls?{query}", runtime["api_token"], timeout=args.timeout)


def cmd_call(args: argparse.Namespace) -> Any:
    runtime = resolve_runtime(args)
    call_id = parse.quote(args.call_id, safe="")
    return make_request("GET", f"{runtime['base_url']}/calls/{call_id}", runtime["api_token"], timeout=args.timeout)


def cmd_transcript(args: argparse.Namespace) -> Any:
    runtime = resolve_runtime(args)
    call_id = parse.quote(args.call_id, safe="")
    return make_request("GET", f"{runtime['base_url']}/calls/{call_id}/transcript", runtime["api_token"], timeout=args.timeout)


def cmd_create(args: argparse.Namespace) -> Any:
    runtime = resolve_runtime(args)
    phone_number_id = args.phone_number_id or runtime["phone_number_id"]
    if not phone_number_id:
        raise SystemExit(
            "Missing phoneNumberId. Pass --phone-number-id, set VOIZBOT_PHONE_NUMBER_ID, or add phoneNumberId to your Voizbot config file."
        )

    system_prompt = merge_text(args.system_prompt, read_text_file(args.system_prompt_file))
    extra_system_prompt = merge_text(
        args.extra_system_prompt,
        read_text_file(args.extra_system_prompt_file),
    )
    metadata: dict[str, Any] = {}
    file_metadata = load_file_json(args.metadata_file)
    if file_metadata is not None:
        if not isinstance(file_metadata, dict):
            raise SystemExit("--metadata-file must contain a JSON object")
        metadata.update(file_metadata)
    metadata.update(parse_metadata(args.meta))

    custom_tools = load_file_json(args.custom_tools_file)
    if custom_tools is not None and not isinstance(custom_tools, list):
        raise SystemExit("--custom-tools-file must contain a JSON array")

    payload: dict[str, Any] = {
        "phoneNumberId": phone_number_id,
        "to": args.to,
        "dryRun": args.dry_run,
    }
    if args.template_id:
        payload["templateId"] = args.template_id
    if system_prompt:
        payload["systemPrompt"] = system_prompt
    if extra_system_prompt:
        payload["extraSystemPrompt"] = extra_system_prompt
    if args.voice_model:
        payload["voiceModel"] = args.voice_model
    if metadata:
        payload["metadata"] = metadata
    if args.function_tool_id:
        payload["functionToolIds"] = args.function_tool_id
    if args.extra_function_tool_id:
        payload["extraFunctionToolIds"] = args.extra_function_tool_id
    if custom_tools is not None:
        payload["customTools"] = custom_tools

    return make_request(
        "POST",
        f"{runtime['base_url']}/calls/outbound",
        runtime["api_token"],
        json_body=payload,
        timeout=args.timeout,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interact with the Voizbot public API")
    parser.add_argument("--config", help=f"Path to config JSON (default: {DEFAULT_CONFIG_PATH})")
    parser.add_argument("--base-url", help="Voizbot API base URL, with or without /v1")
    parser.add_argument("--api-token", help="Voizbot API token")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds")

    subparsers = parser.add_subparsers(dest="command", required=True)

    numbers = subparsers.add_parser("numbers", help="List phone numbers available to your organization")
    numbers.set_defaults(func=cmd_numbers)

    templates = subparsers.add_parser("templates", help="List outbound templates")
    templates.set_defaults(func=cmd_templates)

    tools = subparsers.add_parser("tools", help="List function tools")
    tools.set_defaults(func=cmd_tools)

    calls = subparsers.add_parser("calls", help="List calls")
    calls.add_argument("--filter", choices=["all", "active", "recent"], default="all")
    calls.add_argument("--limit", type=int, default=20)
    calls.set_defaults(func=cmd_calls)

    call = subparsers.add_parser("call", help="Get one call by id")
    call.add_argument("call_id")
    call.set_defaults(func=cmd_call)

    transcript = subparsers.add_parser("transcript", help="Get one call transcript by id")
    transcript.add_argument("call_id")
    transcript.set_defaults(func=cmd_transcript)

    create = subparsers.add_parser("create", help="Create a new outbound call")
    create.add_argument("--to", required=True, help="Destination phone number in E.164 format")
    create.add_argument("--phone-number-id", help="Phone number id to place the call from")
    create.add_argument("--template-id", help="Outbound template id")
    create.add_argument("--system-prompt", help="Direct system prompt for this call")
    create.add_argument("--system-prompt-file", help="Read the direct system prompt from a file")
    create.add_argument("--extra-system-prompt", help="Append extra instructions after the template/direct prompt")
    create.add_argument("--extra-system-prompt-file", help="Read the extra prompt from a file")
    create.add_argument("--voice-model", help="Override the voice model for this call")
    create.add_argument("--function-tool-id", action="append", default=[], help="Attach function tool ids explicitly")
    create.add_argument("--extra-function-tool-id", action="append", default=[], help="Add extra function tool ids on top of the template")
    create.add_argument("--custom-tools-file", help="JSON file with an array of inline custom tools")
    create.add_argument("--metadata-file", help="JSON file with metadata object")
    create.add_argument("--meta", action="append", default=[], help="Metadata entry in KEY=VALUE format")
    create.add_argument("--dry-run", action="store_true", help="Validate and create the call record without placing a real call")
    create.set_defaults(func=cmd_create)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
