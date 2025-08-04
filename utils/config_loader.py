# ZoL0 LEVEL 0
# config_loader.py – Ładowanie plików YAML
import os
from pathlib import Path

import yaml


def load_config(path):
    """
    Ładuje plik YAML i zwraca dict z konfiguracją.
    Zastępuje ${VAR} wartościami z ENV.
    """
    path = Path(path)
    with path.open("r") as f:
        config = yaml.safe_load(f)
    # Substitute environment variables for any value like ${VAR}
    for k, v in config.items():
        if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
            env_var = v[2:-1]
            config[k] = os.environ.get(env_var, v)
    return config
