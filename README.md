# Decision Logger

CLI tool for documenting architectural decisions in Markdown + JSON index.

## Install

```bash
git clone https://github.com/fam-hulten/decision-logger.git
cd decision-logger
chmod +x decision_logger.py
```

## Usage

```bash
# Add new decision
python3 decision_logger.py add "Your decision title"

# List all decisions
python3 decision_logger.py list

# Show specific decision
python3 decision_logger.py show <slug>
```

## Format

Each decision is a Markdown file in `decisions/`:
- Context: Why was this decision made?
- Decision: What was decided?
- Rationale: Why this approach?
- Status: Accepted/Deprecated/Superseded
- Tags: architecture, backend, etc.

## Example

```bash
python3 decision_logger.py add "Recall Service owns SRS state"
python3 decision_logger.py show 2026-04-21-recall-service-owns-srs-state
```

## Repo

https://github.com/fam-hulten/decision-logger