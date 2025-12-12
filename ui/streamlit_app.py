import streamlit as st
import tempfile
import os
import matplotlib.pyplot as plt
import numpy as np
import traceback
import io
import pandas as pd
import time
import logging

from src.model import simulate
from src.utils import validate_inputs, plot_setup, save_plot
from src.output_writer import write_results_to_csv


def main():
    st.title("RP-2 PFR Surface Deposition — Interactive UI")
    st.markdown("Configure parameters, upload mechanism, run simulation, and visualize results.")

    # Input parameters
    st.header("Simulation Parameters")
    st.markdown("Configure the PFR parameters below. Hover over inputs for help.")

    # Validation
    validation_errors = []

    col1, col2, col3 = st.columns([1,2,1])
    with col1: st.caption("Axial length of the reactor tube.")
    with col2: length_val = st.number_input("Length", value=24.0, min_value=0.1, key="length_val")
    with col3: length_unit = st.selectbox("", ["in", "m", "cm"], key="length_unit")

    # Diameter
    col1, col2, col3 = st.columns([1,2,1])
    with col1: st.caption("Inner diameter of the reactor tube.")
    with col2: diameter_val = st.number_input("Diameter", value=0.055, min_value=0.001, key="diameter_val")
    with col3: diameter_unit = st.selectbox("", ["in", "m", "cm"], key="diameter_unit")

    # Power
    col1, col2, col3 = st.columns([1,2,1])
    with col1: st.caption("Heat input power to the reactor.")
    with col2: power_val = st.number_input("Power", value=789.0, min_value=0.0, key="power_val")
    with col3: power_unit = st.selectbox("", ["watts", "W"], key="power_unit")

    # Flow
    col1, col2, col3 = st.columns([1,2,1])
    with col1: st.caption("Volumetric flow rate of the fuel mixture.")
    with col2: flow_val = st.number_input("Volumetric Flow Rate", value=53.9, min_value=0.1, key="flow_val")
    with col3: flow_unit = st.selectbox("", ["mL/min", "L/min", "m3/s"], key="flow_unit")

    # T0
    col1, col2, col3 = st.columns([1,2,1])
    with col1: st.caption("Temperature at reactor inlet.")
    with col2: T0_val = st.number_input("Inlet Temperature", value=700.0, min_value=100.0, key="T0_val")
    with col3: T0_unit = st.selectbox("", ["K", "C"], key="T0_unit")

    # P0
    col1, col2, col3 = st.columns([1,2,1])
    with col1: st.caption("Pressure at reactor inlet.")
    with col2: P0_val = st.number_input("Inlet Pressure", value=600.0, min_value=0.1, key="P0_val")
    with col3: P0_unit = st.selectbox("", ["psi", "bar", "atm"], key="P0_unit")

    # Slices
    col1, col2 = st.columns([1,3])
    with col1: st.caption("Number of axial discretization points.")
    with col2: slices = st.number_input("Number of Slices", value=101, min_value=10, step=1, key="slices")

    # Inlet comp
    col1, col2 = st.columns([1,3])
    with col1: st.caption("Gas composition at inlet.")
    with col2: inlet_comp = st.text_input("Inlet Composition", value="RP2:1.0", key="inlet_comp")

    # Initial cov
    col1, col2 = st.columns([1,3])
    with col1: st.caption("Initial surface coverages.")
    with col2: initial_cov = st.text_input("Initial Coverages", value="CC(s):1.0", key="initial_cov")

    # T_ref
    col1, col2, col3 = st.columns([1,2,1])
    with col1: st.caption("Reference temperature for density calculations.")
    with col2: T_ref = st.number_input("Reference Temperature", value=300.0, min_value=100.0, key="T_ref")
    with col3: T_ref_unit = st.selectbox("", ["K", "C"], key="T_ref_unit")

    # Validate inputs
    validation_errors = validate_inputs(
        length_val, diameter_val, power_val, flow_val, T0_val, P0_val, slices, inlet_comp, initial_cov, T_ref
    )

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        st.stop()  # Prevent running with invalid inputs

    # Construct inputs dict
    inputs = {
        'length': [{'value': length_val}, {'units': length_unit}],
        'diameter': [{'value': diameter_val}, {'units': diameter_unit}],
        'power': [{'value': power_val}, {'units': power_unit}],
        'volumetric_flow_rate': [{'value': flow_val}, {'units': flow_unit}],
        'T0': [{'value': T0_val}, {'units': T0_unit}],
        'P0': [{'value': P0_val}, {'units': P0_unit}],
        'number_of_slices': [{'value': int(slices)}, {'units': ''}],
        'inlet_composition': [{'value': inlet_comp}, {'units': ''}],
        'initial_coverages': [{'value': initial_cov}, {'units': ''}],
        'reference_temperature': [{'value': T_ref}, {'units': T_ref_unit}],
    }

    uploaded_mech = st.file_uploader("Upload Cantera mechanism YAML", type=["yaml", "yml"])

    if uploaded_mech is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as mf:
            mf.write(uploaded_mech.getvalue())
            mechanism_path = mf.name

        if st.button("Run Simulation"):
            with st.spinner("Running simulation..."):
                try:
                    start_time = time.time()
                    results, _ = simulate(inputs, mechanism_path)
                    elapsed = time.time() - start_time
                    st.success("Simulation completed.")
                    st.info(f"Simulation time: {elapsed:.2f} seconds | Slices: {len(results)}")
                    st.session_state['results'] = results
                    st.session_state['species_names'] = getattr(results, '_species_names', [])
                    # Create CSV in memory
                    with tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False) as f:
                        csv_path = write_results_to_csv(results, f.name)
                        with open(csv_path, 'r') as rf:
                            st.session_state['csv_data'] = rf.read()
                        os.unlink(csv_path)
                except Exception as e:
                     logging.error(f"Error during simulation: {e}", exc_info=True)
                     st.error(f"Error during simulation: {e}")
                     st.session_state.pop('results', None)
    else:
        st.info("Please upload the mechanism file and configure parameters to run the simulation.")

    # Visualization
    if 'results' in st.session_state:
        results = st.session_state['results']
        species_names = st.session_state.get('species_names', [])

        st.header("Results Visualization")
        plot_options = ["Temperature"] + species_names + ["Deposition Rate"]

        # Download CSV
        if 'csv_data' in st.session_state:
            st.download_button(
                label="Download CSV",
                data=st.session_state['csv_data'],
                file_name="simulation_results.csv",
                mime="text/csv"
            )

        col1, col2 = st.columns(2)

        with col1:
            selected_var1 = st.selectbox("Select variable to plot vs z (Left)", plot_options, key="var1")
            try:
                if selected_var1 == "Temperature":
                    y = results.T
                    ylabel = "Temperature (K)"
                elif selected_var1 == "Deposition Rate":
                    y = results.carbon_deposition_rate
                    ylabel = "Carbon Deposition Rate"
                else:
                    # Species composition
                    idx = species_names.index(selected_var1)
                    y = [row.TDY[2][idx] if hasattr(row, 'TDY') and len(row.TDY) > 2 and len(row.TDY[2]) > idx else 0 for row in results]
                    ylabel = f"{selected_var1} Mass Fraction"

                fig, ax = plot_setup()
                ax.plot(results.z, y)
                ax.set_xlabel("z (m)")
                ax.set_ylabel(ylabel)
                ax.set_title(f"{selected_var1} vs z")
                st.pyplot(fig)

                # Save plot button
                buf = io.BytesIO()
                fig.savefig(buf, format="png")
                buf.seek(0)
                st.download_button(
                    label="Save Plot (PNG)",
                    data=buf,
                    file_name=f"{selected_var1}_vs_z.png",
                    mime="image/png",
                    key="download1"
                )
            except Exception as e:
                st.error(f"Plotting error: {e}")

        with col2:
            selected_var2 = st.selectbox("Select variable to plot vs z (Right)", plot_options, key="var2")
            try:
                if selected_var2 == "Temperature":
                    y = results.T
                    ylabel = "Temperature (K)"
                elif selected_var2 == "Deposition Rate":
                    y = results.carbon_deposition_rate
                    ylabel = "Carbon Deposition Rate (kg/m²/s)"
                else:
                    # Species composition
                    idx = species_names.index(selected_var2)
                    y = [row.TDY[2][idx] if hasattr(row, 'TDY') and len(row.TDY) > 2 and len(row.TDY[2]) > idx else 0 for row in results]
                    ylabel = f"{selected_var2} Mass Fraction"

                fig, ax = plot_setup()
                ax.plot(results.z, y)
                ax.set_xlabel("z (m)")
                ax.set_ylabel(ylabel)
                ax.set_title(f"{selected_var2} vs z")
                st.pyplot(fig)

                # Save plot button
                buf = io.BytesIO()
                fig.savefig(buf, format="png")
                buf.seek(0)
                st.download_button(
                    label="Save Plot (PNG)",
                    data=buf,
                    file_name=f"{selected_var2}_vs_z.png",
                    mime="image/png",
                    key="download2"
                )
            except Exception as e:
                st.error(f"Plotting error: {e}")


if __name__ == '__main__':
    main()
