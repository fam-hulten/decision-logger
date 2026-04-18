#!/usr/bin/env python3
"""Decision Logger CLI - Manage architecture decisions."""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

DECISIONS_DIR = Path(__file__).parent / "docs" / "decisions"
INDEX_FILE = DECISIONS_DIR / "index.json"


def ensure_structure():
    DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        with open(INDEX_FILE, "w") as f:
            json.dump({"version": "1.0", "description": "Architecture decisions", "decisions": []}, f, indent=2)


def load_index():
    with open(INDEX_FILE) as f:
        return json.load(f)


def save_index(data):
    with open(INDEX_FILE, "w") as f:
        json.dump(data, f, indent=2)


def slugify(text):
    """Create URL-safe slug from text."""
    import re
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def create_decision(title, context, decision, rationale, status="Accepted", tags=None):
    """Create a new decision."""
    ensure_structure()
    
    today = datetime.now().strftime("%Y-%m-%d")
    slug = f"{today}-{slugify(title)}"
    filename = DECISIONS_DIR / f"{slug}.md"
    
    tags_str = ", ".join(tags) if tags else "architecture"
    
    content = f"""# [{today}] {title}

## Context
{context}

## Decision
{decision}

## Rationale
{rationale}

## Status
{status}

## Tags
{tags_str}
"""
    
    with open(filename, "w") as f:
        f.write(content)
    
    # Update index
    index = load_index()
    index["decisions"].append({
        "slug": slug,
        "title": title,
        "date": today,
        "status": status,
        "tags": tags or ["architecture"],
        "file": f"{slug}.md"
    })
    save_index(index)
    
    print(f"✅ Created: {filename}")
    return slug


def list_decisions():
    """List all decisions."""
    ensure_structure()
    index = load_index()
    
    if not index["decisions"]:
        print("No decisions found.")
        return
    
    print(f"# Architecture Decisions ({len(index['decisions'])} total)\n")
    
    for d in sorted(index["decisions"], key=lambda x: x["date"], reverse=True):
        print(f"## [{d['date']}] {d['title']}")
        print(f"Status: {d['status']} | Tags: {', '.join(d['tags'])}")
        print(f"File: docs/decisions/{d['file']}")
        print()


def get_decision(slug):
    """Show a specific decision."""
    filename = DECISIONS_DIR / f"{slug}.md"
    
    if not filename.exists():
        # Try without date prefix
        for f in DECISIONS_DIR.glob(f"*{slug}*"):
            filename = f
            break
        else:
            print(f"Decision not found: {slug}")
            return
    
    with open(filename) as f:
        print(f.read())


def main():
    parser = argparse.ArgumentParser(description="Decision Logger CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # add command
    add_parser = subparsers.add_parser("add", help="Add a new decision")
    add_parser.add_argument("--title", required=True, help="Decision title")
    add_parser.add_argument("--context", required=True, help="Context/background")
    add_parser.add_argument("--decision", required=True, help="The decision made")
    add_parser.add_argument("--rationale", required=True, help="Why this decision")
    add_parser.add_argument("--status", default="Accepted", help="Status (Accepted/Proposed/Deprecated)")
    add_parser.add_argument("--tags", help="Comma-separated tags")
    
    subparsers.add_parser("list", help="List all decisions")
    
    get_parser = subparsers.add_parser("get", help="Show a specific decision")
    get_parser.add_argument("slug", help="Decision slug")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "add":
        tags = args.tags.split(",") if args.tags else None
        create_decision(args.title, args.context, args.decision, args.rationale, args.status, tags)
    elif args.command == "list":
        list_decisions()
    elif args.command == "get":
        get_decision(args.slug)


if __name__ == "__main__":
    main()
