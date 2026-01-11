# Contributing to CHRONON-1

## Installation
1. Clone the repo.
2. Install in editable mode:
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests
```bash
pytest
```

## Reproducibility
Ensure your changes do not break reproducibility.
Run:
```bash
chronon1 reproduce --config configs/toy.yml
```
And check that `reports/` outputs are generated.

## Style Guide
We use `ruff` for linting.
```bash
ruff check .
```

## Pull Requests
- Open an issue first.
- Link PR to issue.
- Ensure CI passes.
