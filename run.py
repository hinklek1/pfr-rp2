import argparse
import json
from pathlib import Path
from src.input_parser import get_inputs
from src.model import simulate
from src.plots import create_plots

def file_exists(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    else:
        return path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run RP-2 PFR with YAML inputs")
    parser.add_argument('-c', '--config', required=True, help='Path to YAML input config')
    parser.add_argument('-m', '--mechanism', required=True, help='Path to RP-2 mechanism YAML')
    parser.add_argument('-p', '--plot', required=False, action='store_true', help='Generate plots of results')
    args = parser.parse_args()

    config_path = file_exists(args.config)
    mechanism_path = file_exists(args.mechanism)

    try:
        inputs = get_inputs(config_path)
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        raise SystemExit(2)
    
    results = simulate(inputs, mechanism_path)
    
    if args.plot:
        create_plots(results, mechanism_path)
