import argparse
import json
from pathlib import Path
import os
from src.input_parser import get_inputs
from src.model import simulate
from src.plots import create_plots
from src.output_writer import write_results_to_csv
from src.output_data_exports import (
    export_temperature_vs_z,
    export_deposition_vs_z,
    export_composition_vs_z,
)


def file_exists(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    return str(p)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run RP-2 PFR with YAML inputs")
    parser.add_argument('-c', '--config', required=True, help='Path to YAML input config')
    parser.add_argument('-m', '--mechanism', required=True, help='Path to RP-2 mechanism YAML')
    parser.add_argument('-p', '--plot', required=False, action='store_true', help='Generate default plots (temperature, deposition)')
    parser.add_argument('--variables', required=False, help='Comma-separated list of variables to plot (implies plotting)')
    parser.add_argument('-o', '--output', required=False, help='Path to output results CSV')
    args = parser.parse_args()

    config_path = file_exists(args.config)
    mechanism_path = file_exists(args.mechanism)

    try:
        inputs = get_inputs(config_path)
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        raise SystemExit(2)
    
    results, ebal = simulate(inputs, mechanism_path)
    
    csv_path = args.output if args.output else os.path.join(os.getcwd(), 'data', 'results.csv')
    os.makedirs(os.path.dirname(csv_path) or '.', exist_ok=True)

    # Write the main aggregated CSV
    write_results_to_csv(results, csv_path)

    # Write additional per-z outputs for easier plotting/analysis
    base_dir = os.path.dirname(csv_path) or '.'
    try:
        export_temperature_vs_z(results, os.path.join(base_dir, 'temperature_vs_z.csv'))
        export_deposition_vs_z(results, os.path.join(base_dir, 'deposition_vs_z.csv'))
        export_composition_vs_z(results, os.path.join(base_dir, 'composition_vs_z.csv'))
    except Exception as e:
        # Do not fail the whole run just because extra exports fail
        print(json.dumps({"export_error": str(e)}, indent=2))

    print(json.dumps({"output_csv": csv_path}, indent=2))

    if args.variables:
        variables = [v.strip() for v in args.variables.split(',')]
        create_plots(results, mechanism_path, variables=variables)
    elif args.plot:
        create_plots(results, mechanism_path)
