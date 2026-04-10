# Decision Logger

CLI for documenting architecture decisions.

## Usage

Run the CLI directly with Python:

```bash
python decision_logger.py --help
```

### Add a decision

```bash
python decision_logger.py add "Use Postgres" "Postgres is reliable and supports JSONB."
```

### List decisions

```bash
python decision_logger.py list
```

### Show one decision

```bash
python decision_logger.py show 1
```

By default, data is stored in `decisions.json` in the current directory.
Use `--db` to point at a different file:

```bash
python decision_logger.py --db data/decisions.json list
```
