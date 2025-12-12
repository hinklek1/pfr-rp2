import json
import os
import numpy as np
import pandas as pd


def _to_python(obj):
    if isinstance(obj, dict):
        return {k: _to_python(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_python(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.generic):
        return obj.item()
    return obj


def _derive_species_names(soln):
    # Prefer explicit names if available
    if hasattr(soln, 'species_names'):
        sn = getattr(soln, 'species_names')
        if isinstance(sn, (list, tuple)):
            return [str(n) for n in sn]
    # Try to derive from first slice composition
    if len(soln) > 0:
        comp = getattr(soln[0], 'composition', None)
        if isinstance(comp, dict):
            return sorted(str(k) for k in comp.keys())
        Y0 = getattr(soln[0], 'Y', None)
        if isinstance(Y0, (list, tuple, np.ndarray)):
            return [f'species_{i}' for i in range(len(Y0))]
        # If Y is a JSON string, try to parse it to get length
        if isinstance(Y0, str):
            try:
                parsed = json.loads(Y0)
                if isinstance(parsed, (list, tuple, np.ndarray)):
                    return [f'species_{i}' for i in range(len(parsed))]
            except Exception:
                pass
        try:
            if Y0 is not None and hasattr(Y0, '__len__'):
                n = len(Y0)
                if n > 0:
                    return [f'species_{i}' for i in range(n)]
        except Exception:
            pass
    return None


def write_results_to_csv(soln, csv_path: str) -> str:
    """Serialize per-slice results to CSV with per-species composition columns when available."""
    n = len(soln)
    z = getattr(soln, 'z', None)
    species_names = _derive_species_names(soln)
    rows = []
    for i in range(n):
        row = {'slice': i}
        if z is not None:
            row['z'] = z[i]
        # TDY
        tdy = getattr(soln[i], 'TDY', None)
        if tdy is not None:
            row['TDY'] = json.dumps(_to_python(tdy))
            try:
                row['T'] = float(tdy[0])
            except Exception:
                row['T'] = None
        else:
            row['TDY'] = None
            row['T'] = None

        if species_names is not None:
            for sp in species_names:
                row[sp] = None
            comp = getattr(soln[i], 'composition', None)
            if isinstance(comp, dict):
                for k, v in comp.items():
                    key = str(k)
                    if key in species_names:
                        row[key] = v
            else:
                # Try to populate from Y when available
                Y = getattr(soln[i], 'Y', None)
                # If Y is a JSON string, parse it
                Y_list = None
                if isinstance(Y, str):
                    try:
                        parsed = json.loads(Y)
                        if isinstance(parsed, (list, tuple, np.ndarray)):
                            Y_list = list(parsed)
                    except Exception:
                        Y_list = None
                elif isinstance(Y, (list, tuple, np.ndarray)):
                    Y_list = list(Y)
                if Y_list is not None:
                    for idx, val in enumerate(Y_list):
                        if idx < len(species_names):
                            row[species_names[idx]] = val
        else:
            if hasattr(soln[i], 'Y'):
                row['Y'] = json.dumps(_to_python(getattr(soln[i], 'Y')))
            elif hasattr(soln[i], 'composition'):
                comp = getattr(soln[i], 'composition')
                row['Y'] = json.dumps(_to_python(comp))
            else:
                row['Y'] = None

        for field in ['surf_coverages','surf_rates','carbon_deposition_rate']:
            if hasattr(soln[i], field):
                val = getattr(soln[i], field)
                if isinstance(val, np.ndarray):
                    row[field] = json.dumps(val.tolist())
                else:
                    row[field] = val
            else:
                row[field] = None
        rows.append(row)

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(csv_path) or '.', exist_ok=True)
    df.to_csv(csv_path, index=False)
    return csv_path
