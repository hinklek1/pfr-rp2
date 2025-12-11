import json
import os
import numpy as np
import pandas as pd


def _as_list(x):
    try:
        return list(x)
    except Exception:
        return [x]


def write_results_to_csv(soln, csv_path: str) -> str:
    # Enhanced writer: outputs T, Y, and other fields per slice
    n = len(soln)
    z = getattr(soln, 'z', None)
    rows = []
    for i in range(n):
        row = {'slice': i}
        if z is not None:
            row['z'] = z[i]
        tdy = getattr(soln[i], 'TDY', None)
        if tdy is not None:
            row['TDY'] = json.dumps(_as_list(tdy))
            try:
                row['T'] = float(tdy[0])
            except Exception:
                row['T'] = None
        else:
            row['TDY'] = None
            row['T'] = None
        # gas composition
        if hasattr(soln[i], 'Y'):
            yv = getattr(soln[i], 'Y')
            row['Y'] = json.dumps(_as_list(yv))
        elif hasattr(soln[i], 'composition'):
            comp = getattr(soln[i], 'composition')
            if isinstance(comp, dict):
                row['Y'] = json.dumps(list(comp.values()))
            else:
                row['Y'] = json.dumps(_as_list(comp))
        else:
            row['Y'] = None
        # surface data
        for field in ['surf_coverages','surf_rates','carbon_deposition_rate']:
            if hasattr(soln[i], field):
                val = getattr(soln[i], field)
                if isinstance(val, (list, tuple, np.ndarray)):
                    row[field] = json.dumps(list(val))
                else:
                    row[field] = val
            else:
                row[field] = None
        rows.append(row)
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(csv_path) or '.', exist_ok=True)
    df.to_csv(csv_path, index=False)
    return csv_path
