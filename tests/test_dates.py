import unittest
from src.cleaning_dates import parse_single_date

class TestDateNormalization(unittest.TestCase):
    def test_date_variants(self):
        res1 = parse_single_date('2025-08-10')
        self.assertEqual(res1[0], '2025-08-10')
        self.assertFalse(res1[3])

        res2 = parse_single_date('10-Apr-2025')
        self.assertEqual(res2[0], '2025-04-10')
        self.assertFalse(res2[3])

        res3 = parse_single_date('21-04-2025')
        self.assertEqual(res3[0], '2025-04-21')
        self.assertFalse(res3[3])

        res4 = parse_single_date('16.08.2025')
        self.assertEqual(res4[0], '2025-08-16')
        self.assertFalse(res4[3])

if __name__ == '__main__':
    unittest.main()
