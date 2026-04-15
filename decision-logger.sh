#!/bin/bash
# Decision Logger CLI

DECISIONS_DIR="${DECISIONS_DIR:-$HOME/projects/studywise-workspace/docs/decisions}"

command=$1
shift

case "$command" in
  init)
    mkdir -p "$DECISIONS_DIR"
    echo "{}" > "$DECISIONS_DIR/index.json"
    echo "✓ Initialized decision directory at $DECISIONS_DIR"
    ;;
  list)
    if [ ! -d "$DECISIONS_DIR" ]; then
      echo "Error: Decisions directory not found. Run 'decision-logger init' first."
      exit 1
    fi
    echo "## Decisions"
    for f in "$DECISIONS_DIR"/*.md; do
      if [ -f "$f" ]; then
        basename "$f" .md
      fi
    done
    ;;
  add)
    title="$*"
    if [ -z "$title" ]; then
      echo "Usage: decision-logger add <title>"
      exit 1
    fi
    slug=$(echo "$title" | sed 's/[^a-zA-Z0-9]/-/g' | tr '[:upper:]' '[:lower:]')
    date=$(date +%Y-%m-%d)
    filename="${DECISIONS_DIR}/${date}-${slug}.md"
    cat > "$filename" << EOF
# [$date] $title

## Context
<!-- What is the issue or decision we're facing? -->

## Decision
<!-- What is the decision we made? -->

## Rationale
<!-- Why did we make this decision? -->

## Status
✅ Proposed

## Tags
<!-- Comma-separated tags -->
EOF
    echo "✓ Created $filename"
    ;;
  get)
    slug=$1
    if [ -z "$slug" ]; then
      echo "Usage: decision-logger get <slug>"
      exit 1
    fi
    for f in "$DECISIONS_DIR"/*${slug}*.md; do
      if [ -f "$f" ]; then
        cat "$f"
      fi
    done
    ;;
  *)
    echo "Usage: decision-logger <init|list|add|get>"
    ;;
esac
