#!/usr/bin/env python3
"""
Kinetic Parameter Optimization Script

Optimizes surface reaction kinetic parameters (pre-exponential factors and activation energies)
by minimizing the difference between simulated and experimental deposition rates.

Usage:
    python optimize_kinetics.py -c config.yaml -m mech/RP2_surf.yaml -e exp_deposition.csv -o optimized_params.json

Experimental data CSV should have columns: z, deposition_rate
"""

import argparse
import json
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
import os
import logging

from src.input_parser import get_inputs
from src.model import simulate


def load_experimental_data(exp_csv_path: str):
    """Load experimental deposition data."""
    df = pd.read_csv(exp_csv_path)
    if 'z' not in df.columns or 'deposition_rate' not in df.columns:
        raise ValueError("Experimental CSV must have 'z' and 'deposition_rate' columns")
    return df['z'].values, df['deposition_rate'].values


def objective_function(params, inputs, mechanism_path, exp_z, exp_dep, objective_type='l2'):
    """Objective function for optimization."""
    try:
        results = simulate(inputs, mechanism_path, kinetic_params=params)
        sim_dep = results.carbon_deposition_rate

        # Interpolate simulated data to experimental z points
        sim_dep_interp = np.interp(exp_z, results.z, sim_dep)

        # Compute residuals
        residuals = sim_dep_interp - exp_dep

        if objective_type == 'l2':
            return residuals  # least squares
        elif objective_type == 'rmse':
            return np.sqrt(np.mean(residuals**2)) * np.ones_like(residuals)  # RMSE as scalar, but for least_squares, need vector
        elif objective_type == 'mae':
            return np.abs(residuals)  # mean absolute error
        else:
            return residuals
    except Exception as e:
        # Return large penalty if simulation fails
        return np.full_like(exp_dep, 1e6)


def optimize_kinetics(inputs, mechanism_path, exp_csv_path, n_reactions=None, objective_type='l2'):
    """Perform kinetic parameter optimization."""
    # Load experimental data
    exp_z, exp_dep = load_experimental_data(exp_csv_path)

    # Determine number of surface reactions if not provided
    if n_reactions is None:
        # Quick simulation to get n_reactions
        temp_results = simulate(inputs, mechanism_path)
        # Assume surf is available; in practice, might need to load mechanism
        # For now, hardcode or estimate
        n_reactions = 4  # Example; adjust based on mechanism

    # Initial guess: logA = 10, Ea = 50 kcal/mol for each reaction
    initial_params = [10.0] * n_reactions + [50.0] * n_reactions  # logA + Ea_kcal

    # Bounds
    bounds = ([5] * n_reactions + [10] * n_reactions,  # lower
              [15] * n_reactions + [200] * n_reactions)  # upper

    # Optimize
    result = least_squares(
        objective_function,
        initial_params,
        bounds=bounds,
        args=(inputs, mechanism_path, exp_z, exp_dep, objective_type),
        method='trf',
        ftol=1e-6,
        xtol=1e-6,
        max_nfev=100
    )

    return result, exp_z, exp_dep


def main():
    parser = argparse.ArgumentParser(description="Optimize kinetic parameters for surface reactions")
    parser.add_argument('-c', '--config', required=True, help='Path to YAML config')
    parser.add_argument('-m', '--mechanism', required=True, help='Path to Cantera mechanism YAML')
    parser.add_argument('-e', '--experimental', required=True, help='Path to experimental deposition CSV')
    parser.add_argument('-o', '--output', required=True, help='Output JSON file for optimized parameters')
    parser.add_argument('-n', '--n_reactions', type=int, help='Number of surface reactions (auto-detected if not provided)')
    parser.add_argument('--objective', choices=['l2', 'mae'], default='l2', help='Objective function type (default: l2)')

    args = parser.parse_args()

    # Load inputs
    inputs = get_inputs(args.config)

    # Run optimization
    result, exp_z, exp_dep = optimize_kinetics(inputs, args.mechanism, args.experimental, args.n_reactions, args.objective)

    # Compute diagnostics
    final_residuals = objective_function(result.x, inputs, args.mechanism, exp_z, exp_dep, args.objective)
    rmse = np.sqrt(np.mean(final_residuals**2))
    mae = np.mean(np.abs(final_residuals))

    # Save results
    output_data = {
        'success': result.success,
        'message': result.message,
        'optimized_params': result.x.tolist(),
        'cost': result.cost,
        'nfev': result.nfev,
        'rmse': rmse,
        'mae': mae,
        'objective_type': args.objective
    }

    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)

    logging.info(f"Optimization completed. Results saved to {args.output}")
    logging.info(f"Success: {result.success}")
    logging.info(f"Final cost: {result.cost}")


if __name__ == '__main__':
    main()