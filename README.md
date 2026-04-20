# Decision Logger

CLI tool for documenting architecture decisions.

## Installation

```bash
git clone https://github.com/fam-hulten/decision-logger.git
cd decision-logger
```

## Usage

```bash
# Initialize in a git repo (creates decisions/ directory + index.json)
python3 decision_logger.py init

# Add a decision (all flags except --title are optional)
python3 decision_logger.py add "Use PostgreSQL" \
  --context "We need ACID compliance for transactions" \
  --decision "Use PostgreSQL as primary database" \
  --rationale "ACID compliance, well-supported, good performance" \
  --tags "database,architecture" \
  --status "Accepted"

# List all decisions
python3 decision_logger.py list

# Show a single decision
python3 decision_logger.py get 2026-04-20-use-postgresql
```

## File Format

Each decision is saved as `decisions/YYYY-MM-DD-slug.md`:

```markdown
---
date: 2026-04-20
title: Use PostgreSQL
status: Accepted
tags: ["database", "architecture"]
---

## Context

We need ACID compliance for transactions.

## Decision

Use PostgreSQL as primary database.

## Rationale

ACID compliance, well-supported, good performance.
```

## index.json

All decisions are also indexed in `decisions_index.json`:

```json
{
  "decisions": [
    {
      "slug": "2026-04-20-use-postgresql",
      "title": "Use PostgreSQL",
      "date": "2026-04-20",
      "status": "Accepted",
      "tags": ["database", "architecture"]
    }
  ]
}
```

## Requirements

- Python 3.7+
- Git (uses `git rev-parse --show-toplevel` to find repo root)
- No external dependencies (standard library only)
