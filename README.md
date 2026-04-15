# Decision Logger

CLI tool for documenting architecture decisions.

## Commands
- `decision-logger init` - Initialize decision directory
- `decision-logger add <title>` - Add a new decision
- `decision-logger list` - List all decisions
- `decision-logger get <slug>` - Show a specific decision

## Format
Each decision is a markdown file with:
- Context
- Decision
- Rationale
- Status
- Tags

## Usage
```bash
./decision-logger.sh list
./decision-logger.sh add "My Decision Title"
```
