import matplotlib.pyplot as plt
import numpy as np
from typing import Any, Dict, Optional


def _safe_get(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default)


def _to1d(a):
    if a is None:
        return None
    arr = np.asarray(a)
    if arr.ndim > 1:
        arr = arr.ravel()
    return arr


def create_plots(results: Any, mechanism_path: str, output_dir: Optional[str] = None) -> Dict[str, str]:
    # Attempt to extract common plotted series from the Cantera SolutionArray
    z = _safe_get(results, 'z', None)
    dep = _safe_get(results, 'carbon_deposition_rate', None) or _safe_get(results, 'Cdep', None)
    T = None
    if hasattr(results, 'TDY'):
        T = getattr(results, 'TDY')
    elif hasattr(results, 'T'):
        T = getattr(results, 'T')

    out_dir = output_dir or __import__('os').path.dirname(mechanism_path)
    import os
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    plots = {}

    # Deposition plot
    z_arr = _to1d(z)
    dep_arr = _to1d(dep)
    if z_arr is not None and dep_arr is not None and z_arr.size > 0 and dep_arr.size > 0 and z_arr.shape[0] == dep_arr.shape[0]:
        plt.figure()
        plt.plot(z_arr, dep_arr, label='deposition rate')
        plt.xlabel('z (m)')
        plt.ylabel('deposition rate')
        plt.title('Deposition Rate vs. Length')
        out_path = os.path.join(out_dir, 'deposition_vs_z.png')
        plt.savefig(out_path, dpi=150)
        plots['deposition_vs_z'] = out_path
        plt.close()

    # Temperature plot
    T_arr = _to1d(T)
    if z_arr is not None and T_arr is not None and z_arr.size > 0 and T_arr.size > 0 and z_arr.shape[0] == T_arr.shape[0]:
        plt.figure()
        plt.plot(z_arr, T_arr, label='temperature')
        plt.xlabel('z (m)')
        plt.ylabel('temperature (K)')
        plt.title('Temperature Profile')
        out_path = os.path.join(out_dir, 'temperature_vs_z.png')
        plt.savefig(out_path, dpi=150)
        plots['temperature_vs_z'] = out_path
        plt.close()

    return plots
