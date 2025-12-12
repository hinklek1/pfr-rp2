import unittest
import tempfile
import os
import numpy as np
from optimize_kinetics import objective_function, load_experimental_data


class TestOptimization(unittest.TestCase):

    def setUp(self):
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        self.mechanism_path = os.path.join(os.path.dirname(__file__), '..', 'mech', 'RP2_surf.yaml')

    def test_load_experimental_data(self):
        # Create mock CSV
        content = "z,deposition_rate\n0.0,0.0\n0.1,1e-6\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            csv_path = f.name
        try:
            z, dep = load_experimental_data(csv_path)
            self.assertEqual(len(z), 2)
            self.assertEqual(len(dep), 2)
            np.testing.assert_array_equal(z, [0.0, 0.1])
            np.testing.assert_array_equal(dep, [0.0, 1e-6])
        finally:
            os.unlink(csv_path)

    def test_objective_function(self):
        from src.input_parser import get_inputs
        inputs = get_inputs(self.config_path)
        # Mock exp data
        exp_z = np.array([0.0, 0.1])
        exp_dep = np.array([0.0, 1e-6])
        params = [10.0] * 4 + [50.0] * 4  # Example params
        residuals = objective_function(params, inputs, self.mechanism_path, exp_z, exp_dep)
        self.assertEqual(len(residuals), len(exp_z))
        # Should not crash, residuals should be finite
        self.assertTrue(np.all(np.isfinite(residuals)))


if __name__ == '__main__':
    unittest.main()