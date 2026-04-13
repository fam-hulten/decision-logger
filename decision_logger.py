#!/usr/bin/env python3

"""Decision Logger CLI.

Stores decisions in a JSON file and supports:
- add: create a new decision record
- list: show all saved decisions
- show: display one decision by id
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_DB_PATH = Path("decisions.json")


def load_decisions(db_path: Path) -> list[dict[str, Any]]:
    if not db_path.exists():
        return []

    raw = db_path.read_text(encoding="utf-8")
    if not raw.strip():
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {db_path}: {exc}") from exc

    if not isinstance(data, list):
        raise SystemExit(f"Invalid database format in {db_path}: expected a list")

    return data


def save_decisions(db_path: Path, decisions: list[dict[str, Any]]) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(decisions, indent=2, ensure_ascii=True)
    db_path.write_text(f"{payload}\n", encoding="utf-8")


def next_id(decisions: list[dict[str, Any]]) -> int:
    if not decisions:
        return 1
    return max(int(item.get("id", 0)) for item in decisions) + 1


def handle_add(args: argparse.Namespace) -> int:
    decisions = load_decisions(args.db)
    decision_id = next_id(decisions)
    record = {
        "id": decision_id,
        "title": args.title,
        "decision": args.decision,
        "context": args.context or "",
        "rationale": args.rationale or "",
        "tags": [t.strip() for t in args.tags.split(",")] if args.tags else [],
        "status": args.status or "Proposed",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    decisions.append(record)
    save_decisions(args.db, decisions)
    print(f"Added decision #{decision_id}: {args.title}")
    return 0


def handle_list(args: argparse.Namespace) -> int:
    decisions = load_decisions(args.db)
    if not decisions:
        print("No decisions logged yet.")
        return 0

    print(f"Found {len(decisions)} decision(s):")
    for item in decisions:
        print(f"- [{item['id']}] {item['title']} ({item['created_at']})")
    return 0


def handle_show(args: argparse.Namespace) -> int:
    decisions = load_decisions(args.db)
    match = next(
        (item for item in decisions if int(item.get("id", -1)) == args.id), None
    )
    if not match:
        raise SystemExit(f"Decision with id {args.id} not found")

    print(f"id: {match['id']}")
    print(f"title: {match['title']}")
    print(f"created_at: {match['created_at']}")
    print("decision:")
    print(match["decision"])
    return 0


def format_markdown_single(match: dict[str, Any]) -> str:
    date = match.get("created_at", "")[:10]
    title = match.get("title", "Untitled")
    decision = match.get("decision", "")
    rationale = match.get("rationale", "")
    status = match.get("status", "Accepted")
    tags = match.get("tags", [])

    lines = [
        f"# [{date}] {title}",
        "",
        "## Context",
        match.get("context", "N/A"),
        "",
        "## Decision",
        decision,
        "",
        "## Rationale",
        rationale or "N/A",
        "",
        f"## Status",
        f"✅ {status}" if status.lower() == "accepted" else f"⚠️ {status}",
    ]
    if tags:
        lines.extend(["", f"## Tags", ", ".join(tags)])

    return "\n".join(lines)


def handle_markdown(args: argparse.Namespace) -> int:
    decisions = load_decisions(args.db)
    if not decisions:
        print("# No decisions logged yet.")
        return 0

    if args.id:
        match = next(
            (item for item in decisions if int(item.get("id", -1)) == args.id), None
        )
        if not match:
            raise SystemExit(f"Decision with id {args.id} not found")
        print(format_markdown_single(match))
    else:
        lines = ["# Architecture Decisions", ""]
        for item in decisions:
            lines.append(format_markdown_single(item))
            lines.append("\n---\n")
        print("\n".join(lines).strip())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Log and review architecture decisions"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to JSON database file (default: {DEFAULT_DB_PATH})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new decision")
    add_parser.add_argument("title", help="Short title of the decision")
    add_parser.add_argument("decision", help="Decision details")
    add_parser.add_argument("--context", help="Context/background")
    add_parser.add_argument("--rationale", help="Why this decision was made")
    add_parser.add_argument("--tags", help="Comma-separated tags")
    add_parser.add_argument("--status", default="Proposed", help="Status (default: Proposed)")
    add_parser.set_defaults(func=handle_add)

    list_parser = subparsers.add_parser("list", help="List all decisions")
    list_parser.set_defaults(func=handle_list)

    show_parser = subparsers.add_parser("show", help="Show a decision by id")
    show_parser.add_argument("id", type=int, help="Decision id")
    show_parser.set_defaults(func=handle_show)

    md_parser = subparsers.add_parser("markdown", help="Export decisions as Markdown")
    md_parser.add_argument("--id", type=int, help="Export single decision by id")
    md_parser.set_defaults(func=handle_markdown)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
