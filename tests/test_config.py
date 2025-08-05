from shared.config_loader import load_config

def test_config_loads():
    config = load_config()
    assert isinstance(config, dict)
    assert "global" in config
