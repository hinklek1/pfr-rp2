import json
import os
import numpy as np
import pandas as pd


def _as_list(x):
    try:
        return list(x)
    except Exception:
        return [x]


def export_temperature_vs_z(soln, csv_path: str) -> str:
    n = len(soln)
    z = getattr(soln, 'z', None)
    rows = []
    for i in range(n):
        if z is None:
            # cannot compute z; skip
            continue
        row = {'slice': i, 'z': z[i]}
        tdy = getattr(soln[i], 'TDY', None)
        if tdy is not None:
            try:
                row['T'] = float(tdy[0])
            except Exception:
                row['T'] = None
        else:
            row['T'] = None
        rows.append(row)
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(csv_path) or '.', exist_ok=True)
    df.to_csv(csv_path, index=False)
    return csv_path


def export_deposition_vs_z(soln, csv_path: str) -> str:
    n = len(soln)
    z = getattr(soln, 'z', None)
    dep_vals = getattr(soln, 'carbon_deposition_rate', None)
    rows = []
    for i in range(n):
        if z is None:
            continue
        val = None
        if dep_vals is not None:
            try:
                val = float(dep_vals[i])
            except Exception:
                val = None
        rows.append({'slice': i, 'z': z[i], 'carbon_deposition_rate': val})
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(csv_path) or '.', exist_ok=True)
    df.to_csv(csv_path, index=False)
    return csv_path


def export_composition_vs_z(soln, csv_path: str) -> str:
    n = len(soln)
    z = getattr(soln, 'z', None)
    rows = []
    for i in range(n):
        if z is None:
            continue
        row = {'slice': i, 'z': z[i]}
        if hasattr(soln[i], 'Y'):
            yv = getattr(soln[i], 'Y')
            row['Y'] = _as_list(yv)
        else:
            row['Y'] = None
        rows.append(row)
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(csv_path) or '.', exist_ok=True)
    df.to_csv(csv_path, index=False)
    return csv_path
