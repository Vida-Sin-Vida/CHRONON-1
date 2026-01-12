import yaml

def test_config_structure(tmp_path):
    cfg_content = """
seed: 42
dataset:
  kind: toy
    """
    p = tmp_path / "cfg.yml"
    p.write_text(cfg_content)
    
    with open(p) as f:
        d = yaml.safe_load(f)
        
    assert d['seed'] == 42
    assert d['dataset']['kind'] == 'toy'
