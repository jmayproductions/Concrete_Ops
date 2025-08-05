# shared/config_loader.py

import yaml
from pathlib import Path

CONFIG_PATH = Path("config/config.yaml")

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)
