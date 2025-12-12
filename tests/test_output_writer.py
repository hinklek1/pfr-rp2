import unittest
import tempfile
import os
import pandas as pd
from src.output_writer import write_results_to_csv
from src.model import simulate
from src.input_parser import get_inputs


class TestOutputWriter(unittest.TestCase):

    def setUp(self):
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        self.mechanism_path = os.path.join(os.path.dirname(__file__), '..', 'mech', 'RP2_surf.yaml')

    def test_write_csv_includes_expected_columns(self):
        inputs = get_inputs(self.config_path)
        results, _ = simulate(inputs, self.mechanism_path)

        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            csv_path = write_results_to_csv(results, f.name)

        try:
            df = pd.read_csv(csv_path)
            expected_cols = ['slice', 'z', 'T', 'TDY']
            for col in expected_cols:
                self.assertIn(col, df.columns)
            # Check species columns exist (from _species_names)
            species_names = getattr(results, '_species_names', [])
            for sp in species_names[:3]:  # Check first few
                self.assertIn(sp, df.columns)
        finally:
            os.unlink(csv_path)

    def test_write_csv_has_correct_rows(self):
        inputs = get_inputs(self.config_path)
        results, _ = simulate(inputs, self.mechanism_path)

        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            csv_path = write_results_to_csv(results, f.name)

        try:
            df = pd.read_csv(csv_path)
            self.assertEqual(len(df), len(results))
        finally:
            os.unlink(csv_path)


if __name__ == '__main__':
    unittest.main()