import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))
from src.experiment.utils import calculate_oct

class TestUtils(unittest.TestCase):

    def test_calculate_oct(self):
        order = ['23545', '16215', '15951', '12021', '23446', '18920', '15097', '15231', '23614',
                 '21850', '21849', '21968', '23071', '21845', '21847', '21846', '21865', '15230',
                 '18919', '22276', '23444', '12020', '23149', '23151', '23547', '23546']
        oct = calculate_oct(order)
        self.assertEqual(oct, 35.75 * 60 - 3 * 60)

        oct = calculate_oct(order, occurences={'12020': 3})
        self.assertEqual(oct, 35.75 * 60 - 3 * 60 + 2 * 15)
        
        order = ['23545', '16215', '16215', '23547']
        self.assertRaises(AssertionError, calculate_oct, order)

if __name__ == '__main__':
    unittest.main()
