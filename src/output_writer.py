import json
import os
import numpy as np
import pandas as pd


def _to_python_list(x):
    # Convert numpy types / arrays to Python primitives
    try:
        lst = list(x)
    except Exception:
        lst = [x]
    result = []
    for item in lst:
        if isinstance(item, np.generic):
            result.append(item.item())
        elif isinstance(item, np.ndarray):
            result.append(item.tolist())
        else:
            result.append(item)
    return result


def _collect_species_names(soln):
    names = set()
    try:
        for i in range(len(soln)):
            comp = getattr(soln[i], 'composition', None)
            if isinstance(comp, dict):
                for k in comp.keys():
                    names.add(str(k))
    except Exception:
        pass
    if names:
        return sorted(names)
    return None


def write_results_to_csv(soln, csv_path: str) -> str:
    """Serialize per-slice results into a CSV.
    - Always export slice, z, TDY, T
    - If composition dicts are available across slices, export per-species columns with headers named after species
    - Always export surface-related fields if present
    """
    n = len(soln)
    z = getattr(soln, 'z', None)
    species_names = _collect_species_names(soln)
    rows = []
    for i in range(n):
        row = {'slice': i}
        if z is not None:
            row['z'] = z[i]
        # TDY
        tdy = getattr(soln[i], 'TDY', None)
        if tdy is not None:
            row['TDY'] = json.dumps(_to_python_list(tdy))
            try:
                Tval = float(tdy[0])
                row['T'] = Tval
            except Exception:
                row['T'] = None
        else:
            row['TDY'] = None
            row['T'] = None

        # Composition per-species if available
        if species_names is not None:
            # Initialize per-species columns
            for sp in species_names:
                row[sp] = None
            comp = getattr(soln[i], 'composition', None)
            if isinstance(comp, dict):
                for k, v in comp.items():
                    if str(k) in species_names:
                        row[str(k)] = v
        else:
            # Fallback: legacy Y column
            if hasattr(soln[i], 'Y'):
                row['Y'] = json.dumps(_to_python_list(getattr(soln[i], 'Y')))
            elif hasattr(soln[i], 'composition'):
                comp = getattr(soln[i], 'composition')
                if isinstance(comp, dict):
                    row['Y'] = json.dumps(comp)
                else:
                    row['Y'] = json.dumps(_to_python_list(comp))
            else:
                row['Y'] = None

        # Surface data
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
