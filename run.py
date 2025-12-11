import argparse
import json
from pathlib import Path
import os
from src.input_parser import get_inputs
from src.model import simulate
from src.plots import create_plots
from src.output_writer import write_results_to_csv


def file_exists(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    return str(p)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run RP-2 PFR with YAML inputs")
    parser.add_argument('-c', '--config', required=True, help='Path to YAML input config')
    parser.add_argument('-m', '--mechanism', required=True, help='Path to RP-2 mechanism YAML')
    parser.add_argument('-p', '--plot', required=False, action='store_true', help='Generate plots of results')
    parser.add_argument('-o', '--output', required=False, help='Path to output results CSV')
    args = parser.parse_args()

    config_path = file_exists(args.config)
    mechanism_path = file_exists(args.mechanism)

    try:
        inputs = get_inputs(config_path)
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        raise SystemExit(2)
    
    results = simulate(inputs, mechanism_path)
    
    csv_path = args.output if args.output else os.path.join(os.getcwd(), 'output', 'results.csv')
    os.makedirs(os.path.dirname(csv_path) or '.', exist_ok=True)
    write_results_to_csv(results, csv_path)
    print(json.dumps({"output_csv": csv_path}, indent=2))
    
    if args.plot:
        create_plots(results, mechanism_path)
