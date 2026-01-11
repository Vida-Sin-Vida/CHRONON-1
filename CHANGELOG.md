# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-01-11

### Added
- **Scientific Pipeline**: New `chronon1` CLI for reproducible analysis.
- **Reproducibility**:
  - `reproduce` command with config file support.
  - Checksum verification for results.
  - Strict JSON output formatting.
  - Detailed `RUN_REPORT.md` generation.
- **Governance**: `CITATION.cff`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
- **Docker**: Containerized environment for one-click replication.
- **CI/CD**: GitHub Actions workflow for testing and reproduction.

### Changed
- Refactored project structure to separate scientific core (`chronon_core`) from demo app (`app`).
- Moved simulation logic to `scripts/generate_toy.py` to decouple from validated pipeline.
- Updated `README.md` to prioritize scientific rigor.
- Replaced `requirements.txt` with `pyproject.toml` for standard packaging.
