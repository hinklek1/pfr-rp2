# RP-2 PFR Surface Deposition Model

A Cantera-based plug-flow reactor (PFR) model simulating RP-2 fuel decomposition with surface reactions and carbon deposition.

## Features
- Gas-phase and surface chemistry modeling
- Configurable reactor parameters (length, diameter, power, etc.)
- Energy balance with bulk deposition enthalpy
- Output to CSV with per-species composition columns
- Command-line interface and Streamlit web UI
- Kinetic parameter optimization support

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv pfr_env
   source pfr_env/bin/activate  # On Windows: pfr_env\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure Cantera mechanism file (`mech/RP2_surf.yaml`) is present.

## Usage

### Command Line
Run simulations with YAML config and mechanism:
```bash
python run.py -c config.yaml -m mech/RP2_surf.yaml -o results.csv -p
```
- `-c`: Path to config YAML
- `-m`: Path to Cantera mechanism YAML
- `-o`: Output CSV path (optional)
- `-p`: Generate plots

### Web UI
Launch interactive interface:
```bash
streamlit run ui/streamlit_app.py
```
Upload config and mechanism files, run simulation, view results and plots.

### Config Format
Example `config.yaml`:
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

## Testing
Run tests:
```bash
python -m unittest tests.test_model tests.test_input_parser
```

## Dependencies
- cantera
- pint
- numpy
- pandas
- matplotlib
- streamlit
- pyyaml