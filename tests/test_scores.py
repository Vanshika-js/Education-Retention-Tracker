import unittest
from src.cleaning_scores import parse_score_to_percentage

class TestScoresCleaning(unittest.TestCase):
    def test_percentage(self):
        pct, method, valid = parse_score_to_percentage('63.4%', 'pct')
        self.assertEqual(pct, 63.4)
        self.assertTrue(valid)

    def test_raw_marks(self):
        pct, method, valid = parse_score_to_percentage('21.6/50', 'Raw Marks')
        self.assertAlmostEqual(pct, 43.2)
        self.assertTrue(valid)

    def test_cgpa(self):
        pct, method, valid = parse_score_to_percentage('7.7', 'CGPA')
        self.assertAlmostEqual(pct, 73.15)
        self.assertTrue(valid)

    def test_letter_grade(self):
        pct, method, valid = parse_score_to_percentage('A+', 'Letter Grade')
        self.assertEqual(pct, 95.0)
        self.assertTrue(valid)

if __name__ == '__main__':
    unittest.main()
