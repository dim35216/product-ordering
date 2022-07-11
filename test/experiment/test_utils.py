import unittest
import os
import sys
from pprint import pprint
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))
from src.experiment.utils import calculate_oct, build_graph, create_lp_instance

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

    def test_build_graph(self):
        products = ['23545', '16215', '12020', '15951', '23151', '23547']
        edge_weights_list = build_graph(products)
        pprint(edge_weights_list)
        control_edge_weights_list = [{
            '12020': {'23151': 90},
            '15951': {'12020': 90, '16215': 15},
            '16215': {'12020': 90, '15951': 15},
            '23151': {'23547': 480},
            '23545': {'15951': 30, '16215': 30},
            '23547': {},
            'end': {},
            'start': {'23545': 0}
        }, {
            '12020': {'15951': 90, '16215': 90},
            '15951': {'16215': 15, '23151': 90},
            '16215': {'15951': 15, '23151': 90},
            '23151': {'23547': 480},
            '23545': {'12020': 30},
            '23547': {},
            'end': {},
            'start': {'23545': 0}
        }]

        self.assertListEqual(edge_weights_list, control_edge_weights_list)

        products = ['23545', '16215', '12020', '15951', '23151', '23547']
        edge_weights = build_graph(products, consider_campaigns=False)
        control_edge_weights = {
            '12020': {'15951': 90,
                        '16215': 90,
                        '23151': 90,
                        '23545': 180,
                        '23547': 480,
                        'end': 0},
            '15951': {'12020': 90,
                        '16215': 15,
                        '23151': 90,
                        '23545': 180,
                        '23547': 480,
                        'end': 0},
            '16215': {'12020': 90,
                        '15951': 15,
                        '23151': 90,
                        '23545': 180,
                        '23547': 480,
                        'end': 0},
            '23151': {'12020': 300,
                        '15951': 300,
                        '16215': 300,
                        '23545': 180,
                        '23547': 480,
                        'end': 0},
            '23545': {'12020': 30,
                        '15951': 30,
                        '16215': 30,
                        '23151': 30,
                        '23547': 30,
                        'end': 0},
            '23547': {'12020': 480,
                        '15951': 480,
                        '16215': 480,
                        '23151': 480,
                        '23545': 180,
                        'end': 0},
            'end': {},
            'start': {'12020': 0,
                        '15951': 0,
                        '16215': 0,
                        '23151': 0,
                        '23545': 0,
                        '23547': 0}
        }

        self.assertDictEqual(edge_weights, control_edge_weights)

    def test_create_lp_instance(self):
        edge_weights = {
            '12020': {'15951': 90,
                        '16215': 90,
                        '23151': 90,
                        '23545': 180,
                        '23547': 480,
                        'end': 0},
            '15951': {'12020': 90,
                        '16215': 15,
                        '23151': 90,
                        '23545': 180,
                        '23547': 480,
                        'end': 0},
            '16215': {'12020': 90,
                        '15951': 15,
                        '23151': 90,
                        '23545': 180,
                        '23547': 480,
                        'end': 0},
            '23151': {'12020': 300,
                        '15951': 300,
                        '16215': 300,
                        '23545': 180,
                        '23547': 480,
                        'end': 0},
            '23545': {'12020': 30,
                        '15951': 30,
                        '16215': 30,
                        '23151': 30,
                        '23547': 30,
                        'end': 0},
            '23547': {'12020': 480,
                        '15951': 480,
                        '16215': 480,
                        '23151': 480,
                        '23545': 180,
                        'end': 0},
            'end': {},
            'start': {'12020': 0,
                        '15951': 0,
                        '16215': 0,
                        '23151': 0,
                        '23545': 0,
                        '23547': 0}
        }
        result = create_lp_instance(edge_weights)
        print(result)

if __name__ == '__main__':
    unittest.main()
