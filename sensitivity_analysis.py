#!/usr/bin/env python3
"""
Sensitivity Analysis for Surface Reaction Kinetic Parameters

Computes local sensitivities of PFR outputs to changes in surface reaction
kinetic parameters (pre-exponential factors and activation energies).

Usage:
    python sensitivity_analysis.py -c config.yaml -m mech/RP2_surf.yaml -o sensitivity.json --delta 0.01
"""

import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
import os
from typing import Dict, List

from src.input_parser import get_inputs
from src.model import simulate
from src.utils import plot_setup, save_plot


def compute_sensitivity(inputs: Dict, mechanism_path: str, base_params: List[float],
                       param_idx: int, delta: float = 0.01) -> Dict:
    """
    Compute sensitivity for a single parameter using finite differences.

    Args:
        inputs: Configuration dict
        mechanism_path: Path to mechanism
        base_params: Baseline kinetic parameters
        param_idx: Index of parameter to perturb
        delta: Relative perturbation size

    Returns:
        Dict with sensitivity data
    """
    # Baseline simulation
    results_base, _ = simulate(inputs, mechanism_path, base_params)
    base_deposition = results_base.carbon_deposition_rate
    base_temp = results_base.T

    # Perturbed parameters
    params_plus = base_params.copy()
    params_minus = base_params.copy()
    params_plus[param_idx] *= (1 + delta)
    params_minus[param_idx] *= (1 - delta)

    # Perturbed simulations
    results_plus, _ = simulate(inputs, mechanism_path, params_plus)
    results_minus, _ = simulate(inputs, mechanism_path, params_minus)

    plus_deposition = results_plus.carbon_deposition_rate
    minus_deposition = results_minus.carbon_deposition_rate
    plus_temp = results_plus.T
    minus_temp = results_minus.T

    # Sensitivity coefficients (central difference)
    dep_sens = (plus_deposition - minus_deposition) / (2 * delta * base_params[param_idx])
    temp_sens = (plus_temp - minus_temp) / (2 * delta * base_params[param_idx])

    return {
        'param_idx': param_idx,
        'param_value': base_params[param_idx],
        'deposition_sensitivity': dep_sens.tolist(),
        'temperature_sensitivity': temp_sens.tolist(),
        'z': results_base.z.tolist()
    }


def run_sensitivity_analysis(inputs: Dict, mechanism_path: str, delta: float = 0.01,
                           n_reactions: int = None) -> Dict:
    """
    Run full sensitivity analysis for all surface reaction parameters.
    """
    # Determine number of reactions
    if n_reactions is None:
        temp_results, _ = simulate(inputs, mechanism_path)
        n_reactions = 4  # Default; could be auto-detected

    # Baseline parameters (same as optimization)
    base_params = [10.0] * n_reactions + [50.0] * n_reactions

    sensitivities = []
    for i in range(2 * n_reactions):
        sens = compute_sensitivity(inputs, mechanism_path, base_params, i, delta)
        sensitivities.append(sens)

    return {
        'baseline_params': base_params,
        'delta': delta,
        'n_reactions': n_reactions,
        'sensitivities': sensitivities
    }


def plot_sensitivities(sens_data: Dict, output_dir: str = 'sensitivity_plots'):
    """
    Generate plots for sensitivity analysis.
    """
    os.makedirs(output_dir, exist_ok=True)

    z = sens_data['sensitivities'][0]['z']  # Assume same z for all
    n_params = len(sens_data['sensitivities'])

    # Deposition sensitivity
    fig, ax = plot_setup((10, 6))
    for i, sens in enumerate(sens_data['sensitivities']):
        label = f'Param {i} ({sens["param_value"]:.1f})'
        ax.plot(z, sens['deposition_sensitivity'], label=label)
    ax.set_xlabel('z (m)')
    ax.set_ylabel('Sensitivity (dDep/dParam)')
    ax.set_title('Deposition Rate Sensitivity')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    save_plot(fig, 'deposition_sensitivity.png', output_dir)

    # Temperature sensitivity
    fig, ax = plot_setup((10, 6))
    for i, sens in enumerate(sens_data['sensitivities']):
        label = f'Param {i} ({sens["param_value"]:.1f})'
        ax.plot(z, sens['temperature_sensitivity'], label=label)
    ax.set_xlabel('z (m)')
    ax.set_ylabel('Sensitivity (dTemp/dParam)')
    ax.set_title('Temperature Sensitivity')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    save_plot(fig, 'temperature_sensitivity.png', output_dir)


def main():
    parser = argparse.ArgumentParser(description="Sensitivity analysis for surface reaction kinetics")
    parser.add_argument('-c', '--config', required=True, help='Path to YAML config')
    parser.add_argument('-m', '--mechanism', required=True, help='Path to Cantera mechanism YAML')
    parser.add_argument('-o', '--output', required=True, help='Output JSON file')
    parser.add_argument('--delta', type=float, default=0.01, help='Relative perturbation size (default: 0.01)')
    parser.add_argument('-n', '--n_reactions', type=int, help='Number of surface reactions')
    parser.add_argument('--plots', action='store_true', help='Generate sensitivity plots')

    args = parser.parse_args()

    # Load inputs
    inputs = get_inputs(args.config)

    # Run analysis
    sens_data = run_sensitivity_analysis(inputs, args.mechanism, args.delta, args.n_reactions)

    # Save results
    with open(args.output, 'w') as f:
        json.dump(sens_data, f, indent=2)

    print(f"Sensitivity analysis completed. Results saved to {args.output}")

    # Generate plots if requested
    if args.plots:
        plot_dir = os.path.splitext(args.output)[0] + '_plots'
        plot_sensitivities(sens_data, plot_dir)
        print(f"Plots saved to {plot_dir}/")


if __name__ == '__main__':
    main()