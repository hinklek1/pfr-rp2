import yaml
from typing import Dict, Any

def get_inputs(config_path: str) -> Dict[str, Any]:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
