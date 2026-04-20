#!/usr/bin/env python3
"""Decision Logger CLI - Manage architecture decisions with YAML frontmatter."""

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_repo_root() -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        raise SystemExit("Not in a git repository") from e


def decisions_dir(repo_root: Path) -> Path:
    return repo_root / ".decisions"


def ensure_decisions_dir(repo_root: Path) -> Path:
    d = decisions_dir(repo_root)
    d.mkdir(parents=True, exist_ok=True)
    return d


def format_frontmatter(data: dict) -> str:
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def parse_frontmatter(content: str) -> tuple[dict, str]:
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    frontmatter = {}
    for line in parts[1].strip().split("\n"):
        if ": " in line:
            key, value = line.split(": ", 1)
            if value.startswith("- "):
                frontmatter[key] = [
                    v[2:] for v in value.split("\n") if v.startswith("- ")
                ]
            else:
                frontmatter[key] = value
        elif line.strip():
            parts_line = line.split(":")
            if len(parts_line) >= 2:
                frontmatter[parts_line[0]] = ":".join(parts_line[1:]).strip()
    return frontmatter, parts[2].lstrip("\n")


def handle_init(args: argparse.Namespace) -> int:
    repo_root = get_repo_root()
    d = ensure_decisions_dir(repo_root)
    index_path = d / "index.md"
    if index_path.exists():
        print(f"Decision log already initialized at {index_path}")
        return 0
    index_path.write_text("# Decision Log\n\n", encoding="utf-8")
    print(f"Initialized decision log at {index_path}")
    return 0


def handle_add(args: argparse.Namespace) -> int:
    repo_root = get_repo_root()
    d = decisions_dir(repo_root)
    if not d.exists():
        raise SystemExit(
            "Decision log not initialized. Run 'decision_logger.py init' first."
        )

    decision_id = 1
    for f in d.glob("*.md"):
        frontmatter, _ = parse_frontmatter(f.read_text(encoding="utf-8"))
        if "id" in frontmatter:
            decision_id = max(decision_id, int(frontmatter["id"]) + 1)

    slug = "".join(c if c.isalnum() or c in "- " else "" for c in args.title.lower())[
        :50
    ].strip()
    filename = d / f"{decision_id:04d}-{slug}.md"

    frontmatter = {
        "id": decision_id,
        "title": args.title,
        "date": datetime.now(timezone.utc).isoformat()[:10],
        "status": args.status or "Proposed",
        "tags": [t.strip() for t in args.tags.split(",")] if args.tags else [],
    }

    body = f"# {args.title}\n\n## Context\n{args.context or 'N/A'}\n\n## Decision\n{args.decision}\n\n## Rationale\n{args.rationale or 'N/A'}\n"

    filename.write_text(format_frontmatter(frontmatter) + body, encoding="utf-8")
    print(f"Added decision #{decision_id}: {args.title}")
    return 0


def handle_list(args: argparse.Namespace) -> int:
    repo_root = get_repo_root()
    d = decisions_dir(repo_root)
    if not d.exists():
        raise SystemExit("No decisions found. Run 'decision_logger.py init' first.")

    files = sorted(d.glob("*.md"), key=lambda p: p.name, reverse=True)
    if not files:
        print("No decisions logged yet.")
        return 0

    print(f"Found {len(files)} decision(s):")
    for f in files:
        content = f.read_text(encoding="utf-8")
        frontmatter, _ = parse_frontmatter(content)
        title = frontmatter.get("title", f.stem)
        date = frontmatter.get("date", "unknown")
        status = frontmatter.get("status", "unknown")
        print(f"- [{date}] {title} ({status})")
    return 0


def handle_get(args: argparse.Namespace) -> int:
    repo_root = get_repo_root()
    d = decisions_dir(repo_root)
    if not d.exists():
        raise SystemExit("No decisions found. Run 'decision_logger.py init' first.")

    decision_id = args.id
    pattern = f"{decision_id:04d}-*.md"
    matches = list(d.glob(pattern))

    if not matches:
        raise SystemExit(f"Decision #{decision_id} not found")

    content = matches[0].read_text(encoding="utf-8")
    _, body = parse_frontmatter(content)
    print(body)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Decision Logger CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Initialize decision log in repository")

    add_parser = subparsers.add_parser("add", help="Add a new decision")
    add_parser.add_argument("title", help="Short title of the decision")
    add_parser.add_argument("decision", help="Decision details")
    add_parser.add_argument("--context", help="Context/background")
    add_parser.add_argument("--rationale", help="Why this decision was made")
    add_parser.add_argument("--tags", help="Comma-separated tags")
    add_parser.add_argument(
        "--status", default="Proposed", help="Status (default: Proposed)"
    )
    add_parser.set_defaults(func=handle_add)

    subparsers.add_parser("list", help="List all decisions").set_defaults(
        func=handle_list
    )

    get_parser = subparsers.add_parser("get", help="Show a decision by id")
    get_parser.add_argument("id", type=int, help="Decision id")
    get_parser.set_defaults(func=handle_get)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init":
        return handle_init(args)

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
