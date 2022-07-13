import unittest
import os
import sys
from pprint import pprint
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))
from src.experiment.utils import calculate_oct, get_changeover_matrix, create_lp_instance
from src.experiment.approaches.tsp_solver import build_graph

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

    def test_get_changeover_matrix(self):
        products = {'23545', '16215', '12020', '15951', '23151', '23547'}

        matrix_dict_0 = \
            {'12020': {'12020': 100000000,
                        '15951': 16,
                        '16215': 16,
                        '23151': 58,
                        '23545': 4,
                        '23547': 94},
                '15951': {'12020': 16,
                        '15951': 100000000,
                        '16215': 1,
                        '23151': 58,
                        '23545': 4,
                        '23547': 94},
                '16215': {'12020': 16,
                        '15951': 1,
                        '16215': 100000000,
                        '23151': 58,
                        '23545': 4,
                        '23547': 94},
                '23151': {'12020': 16,
                        '15951': 16,
                        '16215': 16,
                        '23151': 100000000,
                        '23545': 4,
                        '23547': 94},
                '23545': {'12020': 34,
                        '15951': 34,
                        '16215': 34,
                        '23151': 34,
                        '23545': 100000000,
                        '23547': 34},
                '23547': {'12020': 94,
                        '15951': 94,
                        '16215': 94,
                        '23151': 94,
                        '23545': 4,
                        '23547': 100000000}}
        campaigns_order_0 = \
            {'Blau': -1, 'Rot': -1, 'Wochenendreinigung': -1, 'Sterilisation_zu_Wochenbeginn': -1, 'Grapefruit': -1}
        df_matrix, campaigns_order = get_changeover_matrix(products, consider_constraints=0)
        self.assertDictEqual(df_matrix.to_dict(), matrix_dict_0)
        self.assertDictEqual(campaigns_order, campaigns_order_0)

        matrix_dict_None = \
            {'12020': {'12020': 100000000,
                        '15951': 2017998,
                        '16215': 2017998,
                        '23151': 100000000,
                        '23545': 2005998,
                        '23547': 100000000},
                '15951': {'12020': 2017998,
                        '15951': 100000000,
                        '16215': 1,
                        '23151': 100000000,
                        '23545': 2005998,
                        '23547': 100000000},
                '16215': {'12020': 2017998,
                        '15951': 100000000,
                        '16215': 100000000,
                        '23151': 100000000,
                        '23545': 2005998,
                        '23547': 100000000},
                '23151': {'12020': 2017998,
                        '15951': 2017998,
                        '16215': 2017998,
                        '23151': 100000000,
                        '23545': 100000000,
                        '23547': 100000000},
                '23545': {'12020': 100000000,
                        '15951': 100000000,
                        '16215': 100000000,
                        '23151': 100000000,
                        '23545': 100000000,
                        '23547': 100000000},
                '23547': {'12020': 100000000,
                        '15951': 100000000,
                        '16215': 100000000,
                        '23151': 2095998,
                        '23545': 100000000,
                        '23547': 100000000}}
        campaigns_order_None = \
            {'Rot': 1, 'Wochenendreinigung': 3, 'Sterilisation_zu_Wochenbeginn': 0, 'Blau': 1, 'Grapefruit': 2}
        df_matrix, campaigns_order = get_changeover_matrix(products, consider_constraints=None)
        # pprint(df_matrix.to_dict())
        self.assertDictEqual(df_matrix.to_dict(), matrix_dict_None)
        self.assertDictEqual(campaigns_order, campaigns_order_None)

    def test_build_graph(self):
        products = {'23545', '16215', '12020', '15951', '23151', '23547'}
        edge_weights = build_graph(products, consider_constraints=0)
        # pprint(edge_weights)
        control_edge_weights = \
            {'12020': {'15951': 16,
                        '16215': 16,
                        '23151': 16,
                        '23545': 34,
                        '23547': 94,
                        'end': 0},
                '15951': {'12020': 16,
                        '16215': 1,
                        '23151': 16,
                        '23545': 34,
                        '23547': 94,
                        'end': 0},
                '16215': {'12020': 16,
                        '15951': 1,
                        '23151': 16,
                        '23545': 34,
                        '23547': 94,
                        'end': 0},
                '23151': {'12020': 58,
                        '15951': 58,
                        '16215': 58,
                        '23545': 34,
                        '23547': 94,
                        'end': 0},
                '23545': {'12020': 4,
                        '15951': 4,
                        '16215': 4,
                        '23151': 4,
                        '23547': 4,
                        'end': 0},
                '23547': {'12020': 94,
                        '15951': 94,
                        '16215': 94,
                        '23151': 94,
                        '23545': 34,
                        'end': 0},
                'end': {},
                'start': {'12020': 0,
                        '15951': 0,
                        '16215': 0,
                        '23151': 0,
                        '23545': 0,
                        '23547': 0}}

        self.assertDictEqual(edge_weights, control_edge_weights)

    def test_create_lp_instance(self):
        products = {'23545', '16215', '12020', '15951', '23151', '23547'}
        result = create_lp_instance(products)
        # print(result)
        self.assertEqual(type(result), str)

if __name__ == '__main__':
    unittest.main()
