import os
from chronon_core.reproduce import run_reproduce

def test_reproduce_creates_reports(tmp_path):
    # Create a dummy config in tmp_path
    cfg_path = tmp_path / "test_config.yml"
    out_dir = tmp_path / "reports"
    
    with open(cfg_path, "w") as f:
        f.write(f"""
seed: 123
out_dir: {str(out_dir).replace(os.sep, '/')}
dataset:
  kind: toy
  n: 50
  eps: 0.001
analysis:
  hac: newey_west
  alpha: 0.05
        """)
        
    run_reproduce(str(cfg_path))
    
    assert out_dir.exists()
    assert (out_dir / "results.json").exists()
    assert (out_dir / "checksums.sha256").exists()
    assert (out_dir / "RUN_REPORT.md").exists()
