#!/usr/bin/env python3
"""Decision Logger CLI - Document architectural decisions."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

DECISIONS_DIR = Path(__file__).parent / "decisions"
INDEX_FILE = DECISIONS_DIR / "index.json"


def ensure_dir():
    DECISIONS_DIR.mkdir(exist_ok=True)
    if not INDEX_FILE.exists():
        INDEX_FILE.write_text(json.dumps([], indent=2))


def slugify(title: str) -> str:
    date = datetime.now().strftime("%Y-%m-%d")
    slug = title.lower().replace(" ", "-")
    return f"{date}-{slug}"


def load_index():
    return json.loads(INDEX_FILE.read_text())


def save_index(index):
    INDEX_FILE.write_text(json.dumps(index, indent=2))


def cmd_add(title: str):
    ensure_dir()
    slug = slugify(title)
    filepath = DECISIONS_DIR / f"{slug}.md"
    
    if filepath.exists():
        print(f"Decision already exists: {slug}")
        return 1
    
    content = f"""# {title}

## Context
<!-- Why was this decision made? -->

## Decision
<!-- What was decided? -->

## Rationale
<!-- Why this approach? -->

## Status
✅ Accepted

## Tags
<!-- architecture, backend, frontend, etc. -->
"""
    filepath.write_text(content.strip())
    
    index = load_index()
    index.append({
        "slug": slug,
        "title": title,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "status": "Accepted"
    })
    save_index(index)
    
    print(f"Created: {slug}")
    return 0


def cmd_list():
    ensure_dir()
    index = load_index()
    
    if not index:
        print("No decisions found. Run: decision-logger add <title>")
        return 0
    
    print("## Decisions\n")
    for item in sorted(index, key=lambda x: x.get("date", ""), reverse=True):
        print(f"- **{item['title']}** ({item['date']}) - {item['status']}")
        print(f"  `{item['slug']}`")
    
    return 0


def cmd_show(slug: str):
    ensure_dir()
    filepath = DECISIONS_DIR / f"{slug}.md"
    
    if not filepath.exists():
        print(f"Decision not found: {slug}")
        return 1
    
    print(filepath.read_text())
    return 0


def main():
    parser = argparse.ArgumentParser(description="Decision Logger CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    add_parser = subparsers.add_parser("add", help="Add new decision")
    add_parser.add_argument("title", help="Decision title")
    
    subparsers.add_parser("list", help="List all decisions")
    
    show_parser = subparsers.add_parser("show", help="Show decision")
    show_parser.add_argument("slug", help="Decision slug")
    
    args = parser.parse_args()
    
    if args.command == "add":
        return cmd_add(args.title)
    elif args.command == "list":
        return cmd_list()
    elif args.command == "show":
        return cmd_show(args.slug)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())