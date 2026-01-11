[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17842188.svg)](https://doi.org/10.5281/zenodo.17842188)
![CI Status](https://github.com/username/chronon-1/actions/workflows/ci.yml/badge.svg)

# CHRONON-1

## What it is
CHRONON-1 is a scientific reproducibility pipeline and validation suite for the Chronon Protocol, studying time modulation effects on quantum systems. It provides both a rigorous reproducible core and a demonstration GUI.

## Quickstart

### Installation
```bash
pip install -e .
```

### Reproduce Results (Scientific Pipeline)
Run the standard reproducibility pipeline (generates toy data automatically):
```bash
chronon1 reproduce --config configs/toy.yml
```
This generates a hash-anchored report in `reports/RUN_REPORT.md` and `results.json`.

## Scientific Pipeline vs GUI

### Scientific Pipeline (`chronon_core/`)
The primary artifact. Deterministic, seeded, and auditable.
- Run validation: `chronon1 reproduce --config configs/toy.yml`
- CLI help: `chronon1 --help`

### GUI / Demo (`app/`)
Secondary demonstration and interactive exploration.
- Launch: `chronon-gui` (if installed) or via script.
- *Note: The GUI is for exploration; use the CLI for reproducible science.*

## External Audit Mode
To run the analysis on your own "blinded" or external dataset without generating any data, use the template config:

1.  Place your dataset in `data/EXTERNAL/your_data.csv`.
2.  Edit `configs/public_dataset_template.yml` to point to it and set the expected SHA256 of the source file.
3.  Run:
    ```bash
    chronon1 reproduce --config configs/public_dataset_template.yml
    ```

## Reproducibility
Every run generates cryptographically verifiable outputs in `reports/`:
- `RUN_REPORT.md`: Metadata (git commit, OS, lib versions, time, seed).
- `results.json`: Raw numerical outputs (canonicalized).
- `checksums.sha256`: Hash of the results for verification.

To verify a run against expected data (Golden Record):
```bash
sha256sum -c reports/checksums.sha256
```
See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for detailed guarantees.

## Docker (One-click Replication)
To reproduce the analysis in an isolated environment:
```bash
docker compose up --build
```
Artifacts will be available in `./reports`.

## Project Structure
- `chronon_core/` : Scientific library and CLI (Protocol, Field, Analyzer).
- `scripts/` : Simulation and utility scripts (decoupled from core).
- `app/` : Graphical User Interface (CustomTkinter) and backend.
- `configs/` : YAML configurations for reproducible runs.
- `data/` : Dataset storage (git-ignored).
- `reports/` : Output artifacts (git-ignored).
- `tests/` : Automated test suite.

## How to Cite
Please see [CITATION.cff](CITATION.cff).

**Benjamin Brécheteau** (2025). _CHRONON-1: Progressive Validation of a Local Tempo Field_.
DOI: [10.5281/zenodo.17842188](https://doi.org/10.5281/zenodo.17842188)

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for install and style guidelines.

## License
MIT License. See [LICENSE](LICENSE) for details.
