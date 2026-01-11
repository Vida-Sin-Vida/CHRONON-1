# Reproducibility Guarantees

CHRONON-1 is designed to be bitwise reproducible across platforms. This document outlines the mechanisms used to guarantee this and the known limitations.

## Determinism Mechanisms

1.  **Fixed Seeds**: `numpy.random.seed` is set explicitly in the configuration (default `123`). This controls simulation generation and bootstrap resampling.
2.  **Dataset Integrity**: 
    - Input datasets are hashed (SHA-256) upon loading.
    - If the input hash changes, the run is considered different.
3.  **Strict Serialization**:
    - JSON outputs use `sort_keys=True` to ensure consistent key ordering.
    - `NumpyEncoder` handles float/int conversion standardly.
4.  **Golden Record**:
    - The golden checksum (`tests/golden/toy_checksums.sha256`) explicitly hashes the **canonicalized** output files:
        - `results.json`: Encodes the primary numerical findings. Keys are sorted alphabetically.
    - **Note**: Visual artifacts (PNG plots) are NOT included in the strict checksum validation as rendering can vary slightly between OS backends (e.g. anti-aliasing pixels).
5.  **Canonical Paths**: File paths in reports are relative or canonical to avoid environment leakage.

## Factors That May Affect Determinism

Despite best efforts, the following can introduce variance:

1.  **Floating Point Arithmetic**: 
    - Differences in CPU architecture (x86 vs ARM) or OS (Linux vs Windows) can caus slight deviations in floating point operations.
    - `numpy` and `pandas` rely on underlying BLAS/LAPACK libraries which may differ.
    - **Mitigation**: We use standard 64-bit floats and regression tests tolerances. However, `results.json` equality assumes identical math libraries.
    - **Version Sensitivity**: `RUN_REPORT.md` now logs exact versions of `numpy`, `pandas`, `scipy`, and `statsmodels` to help diagnose environment drift.
2.  **Time Handling**:
    - All timestamps are handled as UTC.
    - Mixing unaware and aware timestamps is prevented by schema validation.

## Verification

To verify that your installation is producing the expected "Golden" results for the reference toy dataset:

```bash
# 1. Run the reproduction
chronon1 reproduce --config configs/toy.yml

# 2. Check the hash against the golden record
chk_ref=$(cat tests/golden/toy_checksums.sha256 | awk '{print $1}')
chk_run=$(cat reports/checksums.sha256 | awk '{print $1}')

if [ "$chk_ref" = "$chk_run" ]; then
    echo "SUCCESS: Results match golden record."
else
    echo "WARNING: Checksum mismatch! Expected $chk_ref, got $chk_run"
fi
```
