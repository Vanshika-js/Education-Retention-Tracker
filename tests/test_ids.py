import unittest
from src.cleaning_ids import normalize_school_id

class TestSchoolIDNormalization(unittest.TestCase):
    def test_id_variants(self):
        self.assertEqual(normalize_school_id('SCH1001'), 'SCH1001')
        self.assertEqual(normalize_school_id('SCH-1001'), 'SCH1001')
        self.assertEqual(normalize_school_id('sch_1001'), 'SCH1001')
        self.assertEqual(normalize_school_id('S1001'), 'SCH1001')
        self.assertEqual(normalize_school_id('1001'), 'SCH1001')
        self.assertEqual(normalize_school_id('286'), 'SCH0286')
        self.assertEqual(normalize_school_id('sch0050'), 'SCH0050')

    def test_null_id(self):
        self.assertIsNone(normalize_school_id(None))

if __name__ == '__main__':
    unittest.main()
