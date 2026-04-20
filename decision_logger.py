#!/usr/bin/env python3
"""Decision Logger CLI - Document architecture decisions."""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_repo_root() -> Path:
    """Find git repo root using git rev-parse."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        raise SystemExit("Error: Not in a git repository (or git not available)") from e


def decisions_dir(repo_root: Path) -> Path:
    """Return path to decisions directory."""
    return repo_root / "decisions"


def index_path(repo_root: Path) -> Path:
    """Return path to index.json."""
    return repo_root / "decisions_index.json"


def ensure_decisions_dir(repo_root: Path) -> Path:
    """Create decisions dir if it doesn't exist."""
    d = decisions_dir(repo_root)
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_index(repo_root: Path) -> dict:
    """Load index.json."""
    idx = index_path(repo_root)
    if idx.exists():
        return json.loads(idx.read_text(encoding="utf-8"))
    return {"decisions": []}


def save_index(repo_root: Path, data: dict) -> None:
    """Save index.json."""
    idx = index_path(repo_root)
    idx.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_slug(title: str) -> str:
    """Create URL-safe slug from title."""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
    slug = re.sub(r'[\s_]+', '-', slug)   # Spaces to hyphens
    slug = slug.strip('-')                  # Trim hyphens
    return slug[:50]                       # Max 50 chars


def handle_init(args: argparse.Namespace) -> int:
    """Initialize decisions directory and index."""
    repo_root = get_repo_root()
    ensure_decisions_dir(repo_root)
    data = load_index(repo_root)
    if data["decisions"]:
        print(f"Decision log already initialized. Found {len(data['decisions'])} decisions.")
    else:
        save_index(repo_root, {"decisions": []})
        print(f"Initialized decision log at {decisions_dir(repo_root)}/")
    return 0


def handle_add(args: argparse.Namespace) -> int:
    """Add a new decision."""
    repo_root = get_repo_root()
    ensure_decisions_dir(repo_root)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = make_slug(args.title)
    filename = f"{today}-{slug}.md"
    filepath = decisions_dir(repo_root) / filename

    if filepath.exists():
        print(f"Warning: {filename} already exists. Overwriting.")

    # Build markdown with YAML frontmatter (manual, no PyYAML)
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
    tags_json = json.dumps(tags)
    
    content = f"""---
date: {today}
title: {args.title}
status: {args.status or 'Proposed'}
tags: {tags_json}
---

## Context

{args.context or 'N/A'}

## Decision

{args.decision or 'N/A'}

## Rationale

{args.rationale or 'N/A'}
"""

    filepath.write_text(content, encoding="utf-8")
    print(f"Added: {filename}")

    # Update index
    data = load_index(repo_root)
    data["decisions"].append({
        "slug": filename[:-3],  # Without .md
        "title": args.title,
        "date": today,
        "status": args.status or "Proposed",
        "tags": tags,
    })
    save_index(repo_root, data)
    print(f"Updated index ({len(data['decisions'])} decisions total)")

    return 0


def handle_list(args: argparse.Namespace) -> int:
    """List all decisions."""
    repo_root = get_repo_root()
    d = decisions_dir(repo_root)

    if not d.exists() or not any(d.glob("*.md")):
        print("No decisions found. Run 'decision_logger.py init' first.")
        return 0

    files = sorted(d.glob("*.md"), key=lambda p: p.name, reverse=True)
    
    print(f"Found {len(files)} decision(s):\n")
    for f in files:
        # Parse frontmatter manually
        text = f.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                try:
                    fm = json.loads(parts[1].strip())
                    title = fm.get("title", f.stem)
                    date = fm.get("date", "?")
                    status = fm.get("status", "?")
                    tags = fm.get("tags", [])
                    tags_str = ", ".join(tags) if tags else ""
                    print(f"- [{date}] {title} [{status}] {tags_str}")
                    continue
                except json.JSONDecodeError:
                    pass
        # Fallback: use filename
        print(f"- {f.stem}")

    return 0


def handle_get(args: argparse.Namespace) -> int:
    """Show a single decision by slug."""
    repo_root = get_repo_root()
    d = decisions_dir(repo_root)

    # Try to find by slug or filename
    search = args.slug
    if not search.endswith(".md"):
        search = search + ".md"
    
    filepath = d / search
    if not filepath.exists():
        # Try glob pattern
        matches = list(d.glob(f"*{search}*"))
        if matches:
            filepath = matches[0]
        else:
            raise SystemExit(f"Decision '{args.slug}' not found")

    # Parse and display
    text = filepath.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter, body = parts[1].strip(), parts[2]
            try:
                fm = json.loads(frontmatter)
                print(f"# {fm.get('title', filepath.stem)}\n")
                print(f"**Date:** {fm.get('date', '?')}")
                print(f"**Status:** {fm.get('status', '?')}")
                tags = fm.get("tags", [])
                if tags:
                    print(f"**Tags:** {', '.join(tags)}")
                print()
                print(body.strip())
                return 0
            except json.JSONDecodeError:
                pass
    # Fallback: just print raw
    print(text)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Decision Logger CLI - Document architecture decisions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 decision_logger.py init
  python3 decision_logger.py add "Use PostgreSQL" --context "We need ACID" --decision "Use Postgres" --rationale "ACID compliance"
  python3 decision_logger.py list
  python3 decision_logger.py get 2026-04-20-use-postgresql
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # init
    subparsers.add_parser("init", help="Initialize decision log in repository")

    # add
    add_parser = subparsers.add_parser("add", help="Add a new decision")
    add_parser.add_argument("title", help="Short title of the decision")
    add_parser.add_argument("--context", help="Context/background")
    add_parser.add_argument("--decision", "-d", help="The decision made")
    add_parser.add_argument("--rationale", help="Why this decision was made")
    add_parser.add_argument("--tags", help="Comma-separated tags (e.g. 'architecture,api')")
    add_parser.add_argument("--status", default="Proposed", help="Status (Proposed/Accepted/Deprecated)")
    add_parser.set_defaults(func=handle_add)

    # list
    subparsers.add_parser("list", help="List all decisions").set_defaults(func=handle_list)

    # get
    get_parser = subparsers.add_parser("get", help="Show a decision by slug (filename without .md)")
    get_parser.add_argument("slug", help="Decision slug (e.g. '2026-04-20-my-decision')")
    get_parser.set_defaults(func=handle_get)

    args = parser.parse_args()

    if args.command == "init":
        return handle_init(args)

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
