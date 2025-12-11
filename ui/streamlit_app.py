import streamlit as st
import tempfile
import os

from src.input_parser import get_inputs
from src.model import simulate
from src.plots import create_plots


def main():
    st.title("RP-2 PFR Surface Deposition — Interactive UI")
    st.markdown("This UI lets you run the Cantera-based PFR model with surface reactions and visualize results.")

    uploaded_config = st.file_uploader("Upload YAML config", type=["yaml", "yml"])
    uploaded_mech = st.file_uploader("Upload Cantera mechanism YAML", type=["yaml", "yml"])

    if uploaded_config is not None and uploaded_mech is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as cf:
            cf.write(uploaded_config.getvalue())
            config_path = cf.name
        with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as mf:
            mf.write(uploaded_mech.getvalue())
            mechanism_path = mf.name

        if st.button("Run Simulation"):
            try:
                inputs = get_inputs(config_path)
                results = simulate(inputs, mechanism_path)
                st.success("Simulation completed.")
                # Deposition summary if available
                if hasattr(results, 'carbon_deposition_rate'):
                    dep = results.carbon_deposition_rate
                    if hasattr(dep, '__len__') and len(dep) > 0:
                        st.write(f"Deposited units across {len(dep)} slices (sample): {dep[:5]}...")
            except Exception as e:
                st.error(f"Error during simulation: {e}")
            try:
                plots = create_plots(results, mechanism_path)
                for label, path in plots.items():
                    st.image(path, caption=label, width=700)
            except Exception as e:
                st.warning(f"Plotting failed: {e}")
    else:
        st.info("Please upload both config and mechanism files to run the simulation.")


if __name__ == '__main__':
    main()
