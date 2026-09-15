import unittest
from src.cleaning_mdm import clean_quantity_and_unit, clean_cost

class TestMDMCleaning(unittest.TestCase):
    def test_units_conversion(self):
        # 1 Bag = 50 KG
        qty_kg, unit_clean, method, inferred = clean_quantity_and_unit(2, 'bags')
        self.assertEqual(qty_kg, 100.0)
        self.assertEqual(unit_clean, 'KG')

        # 16100 Grams = 16.1 KG
        qty_kg2, unit_clean2, method2, inferred2 = clean_quantity_and_unit(16100, 'Grams')
        self.assertEqual(qty_kg2, 16.1)

        # Embedded string "14.9 kg"
        qty_kg3, unit_clean3, method3, inferred3 = clean_quantity_and_unit('14.9 kg', None)
        self.assertEqual(qty_kg3, 14.9)

    def test_cost_cleaning(self):
        self.assertEqual(clean_cost('₹644'), 644.0)
        self.assertEqual(clean_cost('Rs. 1,600'), 1600.0)
        self.assertEqual(clean_cost('336/-'), 336.0)

if __name__ == '__main__':
    unittest.main()
