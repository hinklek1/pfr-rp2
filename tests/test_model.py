import unittest
import os
from src.model import simulate
from src.input_parser import get_inputs


class TestModelSimulation(unittest.TestCase):

    def test_simulation_runs_without_error(self):
        # Use the existing config.yaml
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        mechanism_path = os.path.join(os.path.dirname(__file__), '..', 'mech', 'RP2_surf.yaml')

        inputs = get_inputs(config_path)
        results = simulate(inputs, mechanism_path)

        # Basic checks
        self.assertIsNotNone(results)
        self.assertTrue(hasattr(results, 'z'))
        self.assertTrue(hasattr(results, 'T'))
        self.assertTrue(len(results.z) > 0)
        self.assertTrue(len(results.T) > 0)

    def test_simulation_with_kinetic_params(self):
        # Test with dummy kinetic params
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        mechanism_path = os.path.join(os.path.dirname(__file__), '..', 'mech', 'RP2_surf.yaml')

        inputs = get_inputs(config_path)
        # Dummy params: 2 reactions, logA and Ea
        kinetic_params = [10, 11, 20, 21]  # logA1, logA2, Ea1_kcal, Ea2_kcal
        results = simulate(inputs, mechanism_path, kinetic_params=kinetic_params)

        self.assertIsNotNone(results)
        self.assertTrue(hasattr(results, 'z'))


if __name__ == '__main__':
    unittest.main()