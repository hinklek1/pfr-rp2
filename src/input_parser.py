import yaml
from typing import Dict, Any
from collections.abc import Mapping


def _validate_list_of_pair(param_value, param_name: str) -> bool:
    # Expect a list like:
    #   - value: ...
    #   - units: ...
    # i.e., at least two entries with a value and a units item.
    if not isinstance(param_value, list) or len(param_value) == 0:
        raise ValueError(f"Input '{param_name}' must be a non-empty list of dicts.")
    if len(param_value) < 2:
        raise ValueError(f"Input '{param_name}' must contain at least two entries: 'value' and 'units'.")
    has_value = any(isinstance(it, Mapping) and 'value' in it for it in param_value)
    has_units = any(isinstance(it, Mapping) and 'units' in it for it in param_value)
    if not (has_value and has_units):
        raise ValueError(f"Input '{param_name}' must include both 'value' and 'units' entries.")
    return True


def validate_inputs(data: Dict[str, Any]) -> None:
    required = ['length','diameter','power','volumetric_flow_rate','T0','P0','number_of_slices','inlet_composition','initial_coverages','reference_temperature']
    for key in required:
        if key not in data:
            raise ValueError(f"Missing required input: '{key}'")
        _validate_list_of_pair(data[key], key)
    return None


def get_inputs(config_path: str) -> Dict[str, Any]:
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
    if data is None:
        raise ValueError("Config file is empty or invalid YAML.")
    # Validate basic input structure
    validate_inputs(data)
    return data
