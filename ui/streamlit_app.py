import streamlit as st
import tempfile
import os
import matplotlib.pyplot as plt
import numpy as np

from src.model import simulate


def main():
    st.title("RP-2 PFR Surface Deposition — Interactive UI")
    st.markdown("Configure parameters, upload mechanism, run simulation, and visualize results.")

    # Input parameters
    st.header("Simulation Parameters")
    col1, col2 = st.columns(2)
    with col1:
        length_val = st.number_input("Length", value=24.0, min_value=0.1)
        length_unit = st.selectbox("Length Units", ["in", "m", "cm"], key="length_unit")
        diameter_val = st.number_input("Diameter", value=0.055, min_value=0.001)
        diameter_unit = st.selectbox("Diameter Units", ["in", "m", "cm"], key="diameter_unit")
        power_val = st.number_input("Power", value=789.0, min_value=0.0)
        power_unit = st.selectbox("Power Units", ["watts", "W"], key="power_unit")
        flow_val = st.number_input("Volumetric Flow Rate", value=53.9, min_value=0.1)
        flow_unit = st.selectbox("Flow Units", ["mL/min", "L/min", "m3/s"], key="flow_unit")
    with col2:
        T0_val = st.number_input("Inlet Temperature", value=700.0, min_value=100.0)
        T0_unit = st.selectbox("T0 Units", ["K", "C"], key="T0_unit")
        P0_val = st.number_input("Inlet Pressure", value=600.0, min_value=0.1)
        P0_unit = st.selectbox("P0 Units", ["psi", "bar", "atm"], key="P0_unit")
        slices = st.number_input("Number of Slices", value=101, min_value=10, step=1)
        inlet_comp = st.text_input("Inlet Composition", value="RP2:1.0")
        initial_cov = st.text_input("Initial Coverages", value="CC(s):1.0")
        T_ref = st.number_input("Reference Temperature", value=300.0, min_value=100.0)
        T_ref_unit = st.selectbox("T_ref Units", ["K", "C"], key="T_ref_unit")

    # Construct inputs dict
    inputs = {
        'length': [{'value': length_val, 'units': length_unit}],
        'diameter': [{'value': diameter_val, 'units': diameter_unit}],
        'power': [{'value': power_val, 'units': power_unit}],
        'volumetric_flow_rate': [{'value': flow_val, 'units': flow_unit}],
        'T0': [{'value': T0_val, 'units': T0_unit}],
        'P0': [{'value': P0_val, 'units': P0_unit}],
        'number_of_slices': [{'value': int(slices), 'units': ''}],
        'inlet_composition': [{'value': inlet_comp, 'units': ''}],
        'initial_coverages': [{'value': initial_cov, 'units': ''}],
        'reference_temperature': [{'value': T_ref, 'units': T_ref_unit}],
    }

    uploaded_mech = st.file_uploader("Upload Cantera mechanism YAML", type=["yaml", "yml"])

    if uploaded_mech is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as mf:
            mf.write(uploaded_mech.getvalue())
            mechanism_path = mf.name

        if st.button("Run Simulation"):
            try:
                results = simulate(inputs, mechanism_path)
                st.success("Simulation completed.")
                st.session_state['results'] = results
                st.session_state['species_names'] = getattr(results, '_species_names', [])
            except Exception as e:
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
        selected_var = st.selectbox("Select variable to plot vs z", plot_options)

        if selected_var == "Temperature":
            y = results.T
            ylabel = "Temperature (K)"
        elif selected_var == "Deposition Rate":
            y = results.carbon_deposition_rate
            ylabel = "Carbon Deposition Rate"
        else:
            # Species composition
            idx = species_names.index(selected_var)
            y = [row.Y[idx] if hasattr(row, 'Y') and len(row.Y) > idx else 0 for row in results]
            ylabel = f"{selected_var} Mass Fraction"

        fig, ax = plt.subplots()
        ax.plot(results.z, y)
        ax.set_xlabel("z (m)")
        ax.set_ylabel(ylabel)
        ax.set_title(f"{selected_var} vs z")
        st.pyplot(fig)


if __name__ == '__main__':
    main()
