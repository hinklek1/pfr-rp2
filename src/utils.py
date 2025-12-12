"""
Utility functions for the PFR project.
"""

import logging
import matplotlib.pyplot as plt
import numpy as np


def setup_logging(level=logging.INFO):
    """Set up logging with consistent format."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def validate_inputs(length_val, diameter_val, power_val, flow_val, T0_val, P0_val, slices, inlet_comp, initial_cov, T_ref):
    """Validate input parameters and return list of errors."""
    errors = []
    if length_val <= 0:
        errors.append("Length must be positive.")
    if diameter_val <= 0:
        errors.append("Diameter must be positive.")
    if power_val < 0:
        errors.append("Power must be non-negative.")
    if flow_val <= 0:
        errors.append("Flow rate must be positive.")
    if T0_val < 0:
        errors.append("Inlet temperature must be positive.")
    if P0_val <= 0:
        errors.append("Inlet pressure must be positive.")
    if slices < 10:
        errors.append("Number of slices must be at least 10.")
    if not inlet_comp.strip():
        errors.append("Inlet composition cannot be empty.")
    if not initial_cov.strip():
        errors.append("Initial coverages cannot be empty.")
    if T_ref < 0:
        errors.append("Reference temperature must be positive.")
    return errors


def plot_setup(figsize=(5, 3)):
    """Set up matplotlib figure and axis."""
    fig, ax = plt.subplots(figsize=figsize)
    return fig, ax


def save_plot(fig, filename, output_dir, dpi=150):
    """Save plot to file."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    return path


def calculate_metrics(residuals):
    """Calculate RMSE and MAE from residuals."""
    rmse = np.sqrt(np.mean(residuals**2))
    mae = np.mean(np.abs(residuals))
    return rmse, mae


def interpolate_data(x_sim, y_sim, x_exp):
    """Interpolate simulated data to experimental points."""
    return np.interp(x_exp, x_sim, y_sim)