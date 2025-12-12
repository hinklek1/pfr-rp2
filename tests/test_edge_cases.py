import unittest
import os
from src.model import simulate
from src.input_parser import get_inputs


class TestEdgeCases(unittest.TestCase):

    def setUp(self):
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        self.mechanism_path = os.path.join(os.path.dirname(__file__), '..', 'mech', 'RP2_surf.yaml')

    def test_simulation_with_zero_deposition(self):
        # Modify config to have no power (should have low deposition)
        inputs = get_inputs(self.config_path)
        inputs['power'] = [{'value': 0.0}, {'units': 'watts'}]  # No heat
        results, ebal = simulate(inputs, self.mechanism_path)
        self.assertIsNotNone(results)
        # Ebal might not be 1, but simulation should run
        self.assertTrue(isinstance(ebal, float))

    def test_simulation_with_modified_kinetics(self):
        inputs = get_inputs(self.config_path)
        # Modify kinetics to extreme values
        kinetic_params = [5.0, 5.0, 10.0, 10.0]  # Low A, low Ea
        results, ebal = simulate(inputs, self.mechanism_path, kinetic_params=kinetic_params)
        self.assertIsNotNone(results)
        self.assertTrue(len(results) > 0)


if __name__ == '__main__':
    unittest.main()