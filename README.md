# RP-2 Plug-Flow Reactor Surface Deposition Model

A comprehensive Cantera-based simulation tool for plug-flow reactors (PFR) modeling RP-2 fuel decomposition with gas-phase and surface chemistry, including carbon deposition. Supports parameter studies, kinetic optimization, and interactive visualization.

## Features

- **Chemical Modeling:** Full gas-phase and surface reaction kinetics using Cantera
- **Surface Deposition:** Carbon deposition tracking with energy balance
- **Flexible Configuration:** YAML-based input with unit handling via Pint
- **Multiple Interfaces:** Command-line, web UI, and optimization tools
- **Output Options:** CSV with per-species data, customizable plots
- **Kinetic Optimization:** Fit surface reaction parameters to experimental data
- **Validation & Testing:** Comprehensive test suite with CI/CD
- **Modular Design:** Reusable utilities and clean architecture

## Installation

### Prerequisites
- Python 3.8+
- Cantera (chemical kinetics library)

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd pfr_project
   ```

2. Create a virtual environment:
   ```bash
   python -m venv pfr_env
   source pfr_env/bin/activate  # On Windows: pfr_env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Verify Cantera mechanism file is present:
   ```bash
   ls mech/RP2_surf.yaml
   ```

## Usage

### Command-Line Simulation
Run PFR simulations with YAML configuration:
```bash
python run.py -c config.yaml -m mech/RP2_surf.yaml -o results.csv --variables temperature,deposition,RP2
```

**Arguments:**
- `-c, --config`: Path to YAML configuration file
- `-m, --mechanism`: Path to Cantera mechanism YAML
- `-o, --output`: Output CSV file path (optional)
- `-p, --plot`: Generate default plots (temperature, deposition)
- `--variables`: Comma-separated list of variables to plot (implies plotting)

**Example Output:**
- `results.csv`: Full simulation data with per-species columns
- PNG plots for selected variables

### Web UI
Interactive parameter input and visualization:
```bash
streamlit run ui/streamlit_app.py
```

**Features:**
- Direct parameter input with validation
- Real-time tooltips and error checking
- Side-by-side plotting with download options
- CSV and plot export

### Kinetic Parameter Optimization
Fit surface reaction kinetics to experimental deposition data:
```bash
python optimize_kinetics.py -c config.yaml -m mech/RP2_surf.yaml -e exp_data.csv -o params.json --objective mae
```

**Arguments:**
- `-c, --config`: Base configuration file
- `-m, --mechanism`: Mechanism file
- `-e, --experimental`: CSV with experimental data (columns: `z`, `deposition_rate`)
- `-o, --output`: JSON output for optimized parameters
- `-n, --n_reactions`: Number of surface reactions (auto-detected if omitted)
- `--objective`: Objective function (`l2` for least squares, `mae` for L1)

**Output:** JSON with optimized parameters, diagnostics (RMSE, MAE), and convergence info.

## Configuration

Use YAML files for simulation parameters. Example `config.yaml`:

```yaml
length: [{value: 24.0, units: 'in'}]
diameter: [{value: 0.055, units: 'in'}]
power: [{value: 789, units: 'watts'}]
volumetric_flow_rate: [{value: 53.9, units: 'mL/min'}]
T0: [{value: 700, units: 'K'}]
P0: [{value: 600, units: 'psi'}]
number_of_slices: [{value: 101, units: ''}]
inlet_composition: [{value: 'RP2:1.0', units: ''}]
initial_coverages: [{value: 'CC(s):1.0', units: ''}]
reference_temperature: [{value: 300, units: 'K'}]
```

**Parameter Descriptions:**
- `length`, `diameter`: Reactor geometry
- `power`: Heat input
- `volumetric_flow_rate`: Fuel flow rate
- `T0`, `P0`: Inlet conditions
- `number_of_slices`: Axial discretization (higher = more accurate)
- `inlet_composition`: Gas composition (e.g., 'RP2:1.0' for pure RP-2)
- `initial_coverages`: Initial surface species
- `reference_temperature`: For density calculations

## Testing

Run the comprehensive test suite:
```bash
# All tests
python -m unittest discover tests/

# With pytest
pytest tests/

# Specific test
python -m unittest tests.test_model
```

Tests cover simulation accuracy, input validation, optimization, and output formatting.

## API Reference

### Core Functions

#### `simulate(inputs, mechanism_path, kinetic_params=None, print_kinetics=False)`
Run PFR simulation.
- **Args:** Config dict, mechanism path, optional kinetic params, debug flag
- **Returns:** (results, energy_balance) tuple

#### `create_plots(results, mechanism_path, variables=None)`
Generate plots from simulation results.
- **Args:** Results object, mechanism path, optional variable list
- **Returns:** Dict of plot file paths

#### `write_results_to_csv(soln, csv_path)`
Export results to CSV.
- **Args:** Solution array, output path
- **Returns:** CSV file path

#### `optimize_kinetics(inputs, mechanism_path, exp_csv_path, objective_type='l2')`
Optimize kinetic parameters.
- **Args:** Config, mechanism, experimental CSV, objective type
- **Returns:** Optimization result and diagnostics

### Utilities (`src/utils.py`)
- `validate_inputs()`: Parameter validation
- `plot_setup()`: Matplotlib figure setup
- `calculate_metrics()`: RMSE/MAE computation
- `setup_logging()`: Logging configuration

## Development

### Project Structure
```
pfr_project/
├── src/
│   ├── model.py          # Core simulation
│   ├── input_parser.py   # YAML handling
│   ├── output_writer.py  # CSV export
│   ├── plots.py          # Plotting
│   └── utils.py          # Utilities
├── ui/
│   └── streamlit_app.py  # Web interface
├── tests/                # Test suite
├── mech/                 # Mechanism files
├── optimize_kinetics.py  # Optimization script
├── run.py                # CLI entry
├── config.yaml           # Example config
├── requirements.txt      # Dependencies
└── README.md
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure CI passes
5. Submit a pull request

### CI/CD
GitHub Actions automatically:
- Tests on Python 3.8-3.11
- Lints with flake8
- Runs on pushes/PRs

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Acknowledgments

- Built with [Cantera](https://cantera.org/) for chemical kinetics
- UI powered by [Streamlit](https://streamlit.io/)
- Unit handling via [Pint](https://pint.readthedocs.io/)