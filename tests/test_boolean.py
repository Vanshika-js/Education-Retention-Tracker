import unittest
from src.cleaning_boolean import normalize_boolean

class TestBooleanNormalization(unittest.TestCase):
    def test_true_variants(self):
        for val in ['Yes', 'Y', '1', 'Hai', 'Haan', 'Working', 'Functional', 'Available']:
            self.assertTrue(normalize_boolean(val), f"Failed for {val}")

    def test_false_variants(self):
        for val in ['No', 'N', '0', 'Nahi', 'Nahi hai', 'na', 'Kharab', 'Broken', 'Under Repair']:
            self.assertFalse(normalize_boolean(val), f"Failed for {val}")

    def test_unknown(self):
        self.assertIsNone(normalize_boolean(None))
        self.assertIsNone(normalize_boolean('random_text'))

if __name__ == '__main__':
    unittest.main()
