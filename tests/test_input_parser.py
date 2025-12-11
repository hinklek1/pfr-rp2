import unittest
import os
import tempfile
from src.input_parser import get_inputs


class TestInputParserValidation(unittest.TestCase):

    def _write_yaml(self, content: str) -> str:
        fd, path = tempfile.mkstemp(suffix='.yaml', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)
        except Exception:
            os.remove(path)
            raise
        return path

    def test_valid_config_parses(self):
        content = (
            "length:\n"
            " - value: 24.0\n"
            " - units: 'in'\n\n"
            "diameter:\n"
            " - value: 0.055\n"
            " - units: 'in'\n\n"
            "power:\n"
            " - value: 789\n"
            " - units: 'watts'\n\n"
            "volumetric_flow_rate:\n"
            " - value: 53.9\n"
            " - units: 'mL/min'\n\n"
            "T0:\n"
            " - value: 700\n"
            " - units: 'K'\n\n"
            "P0:\n"
            " - value: 600\n"
            " - units: 'psi'\n\n"
            "number_of_slices:\n"
            " - value: 101\n"
            " - units: 'unitless'\n"
        )
        path = self._write_yaml(content)
        try:
            data = get_inputs(path)
            self.assertIsInstance(data, dict)
            for key in ['length','diameter','power','volumetric_flow_rate','T0','P0','number_of_slices']:
                self.assertIn(key, data)
        finally:
            os.remove(path)

    def test_missing_key_raises(self):
        content = (
            "length:\n - value: 24.0\n - units: 'in'\n"
        )
        path = self._write_yaml(content)
        try:
            with self.assertRaises(ValueError) as cm:
                get_inputs(path)
            self.assertIn("Missing required input: 'diameter'", str(cm.exception))
        finally:
            os.remove(path)

    def test_malformed_list_raises(self):
        content = (
            "length:\n - value: 24.0\n"
        )
        path = self._write_yaml(content)
        try:
            with self.assertRaises(ValueError):
                get_inputs(path)
        finally:
            os.remove(path)

    def test_empty_list_raises(self):
        content = (
            "length: []\n"
        )
        path = self._write_yaml(content)
        try:
            with self.assertRaises(ValueError):
                get_inputs(path)
        finally:
            os.remove(path)


if __name__ == '__main__':
    unittest.main()
