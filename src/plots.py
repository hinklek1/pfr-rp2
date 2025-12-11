import matplotlib.pyplot as plt
import numpy as np
from typing import Any, Dict, Optional


def _safe_get(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default)


def create_plots(results: Any, mechanism_path: str, output_dir: Optional[str] = None) -> Dict[str, str]:
    # Attempt to extract common plotted series from the Cantera SolutionArray
    # The 'results' object is expected to have sliced data appended during simulation.
    z = _safe_get(results, 'z', None)
    dep = _safe_get(results, 'carbon_deposition_rate', None) or _safe_get(results, 'Cdep', None)
    T = None
    if hasattr(results, 'TDY'):
        T = getattr(results, 'TDY')
    elif hasattr(results, 'T'):
        T = getattr(results, 'T')

    import os
    out_dir = output_dir or os.path.dirname(mechanism_path)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    plots = {}

    if z is not None and dep is not None:
        plt.figure()
        try:
            plt.plot(np.asarray(z), np.asarray(dep), label='deposition rate')
            plt.xlabel('z (m)')
            plt.ylabel('deposition rate')
            plt.title('Deposition Rate vs. Length')
            out_path = os.path.join(out_dir, 'deposition_vs_z.png')
            plt.savefig(out_path, dpi=150)
            plots['deposition_vs_z'] = out_path
        finally:
            plt.close()

    if z is not None and T is not None:
        plt.figure()
        try:
            plt.plot(np.asarray(z), np.asarray(T), label='temperature')
            plt.xlabel('z (m)')
            plt.ylabel('temperature (K)')
            plt.title('Temperature Profile')
            out_path = os.path.join(out_dir, 'temperature_vs_z.png')
            plt.savefig(out_path, dpi=150)
            plots['temperature_vs_z'] = out_path
        finally:
            plt.close()

    return plots
