import json
import os
import numpy as np
import pandas as pd

def write_results_to_csv(soln, csv_path: str) -> str:
    n = len(soln)
    z = getattr(soln, 'z', None)
    rows = []
    for i in range(n):
        row = {'slice': i}
        if z is not None:
            row['z'] = z[i]
        for field in ['TDY','surf_coverages','surf_rates','carbon_deposition_rate']:
            if hasattr(soln[i], field):
                val = getattr(soln[i], field)
                if isinstance(val, (list, tuple, np.ndarray)):
                    row[field] = json.dumps(val.tolist() if hasattr(val, 'tolist') else list(val))
                else:
                    row[field] = val
            else:
                row[field] = None
        rows.append(row)
    try:
        df = pd.DataFrame(rows)
        os.makedirs(os.path.dirname(csv_path) or '.', exist_ok=True)
        df.to_csv(csv_path, index=False)
    except Exception:
        with open(csv_path, 'w') as f:
            headers = ['slice','z','TDY','surf_coverages','surf_rates','carbon_deposition_rate']
            f.write(','.join(headers) + '\n')
            for r in rows:
                f.write(','.join([str(r.get(h,'')) for h in headers]) + '\n')
    return csv_path
