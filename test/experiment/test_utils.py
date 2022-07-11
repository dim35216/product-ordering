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
            {'12020': {'12020': 10000000,
                    '15951': 90000,
                    '16215': 90000,
                    '23151': 300000,
                    '23545': 30000,
                    '23547': 480000},
            '15951': {'12020': 90000,
                    '15951': 10000000,
                    '16215': 15000,
                    '23151': 300000,
                    '23545': 30000,
                    '23547': 480000},
            '16215': {'12020': 90000,
                    '15951': 15000,
                    '16215': 10000000,
                    '23151': 300000,
                    '23545': 30000,
                    '23547': 480000},
            '23151': {'12020': 90000,
                    '15951': 90000,
                    '16215': 90000,
                    '23151': 10000000,
                    '23545': 30000,
                    '23547': 480000},
            '23545': {'12020': 180000,
                    '15951': 180000,
                    '16215': 180000,
                    '23151': 180000,
                    '23545': 10000000,
                    '23547': 180000},
            '23547': {'12020': 480000,
                    '15951': 480000,
                    '16215': 480000,
                    '23151': 480000,
                    '23545': 30000,
                    '23547': 10000000}}
        campaigns_order_0 = \
            {'Blau': -1, 'Rot': -1, 'Wochenendreinigung': -1, 'Sterilisation_zu_Wochenbeginn': -1, 'Grapefruit': -1}
        df_matrix, campaigns_order = get_changeover_matrix(products, consider_constraints=0)
        self.assertDictEqual(df_matrix.to_dict(), matrix_dict_0)
        self.assertDictEqual(campaigns_order, campaigns_order_0)

        matrix_dict_None = \
            {'12020': {'12020': 10000000,
                    '15951': 1000090,
                    '16215': 1090000,
                    '23151': 1000300,
                    '23545': 1030000,
                    '23547': 1480000},
            '15951': {'12020': 1000090,
                    '15951': 10000000,
                    '16215': 15,
                    '23151': 1000300,
                    '23545': 1030000,
                    '23547': 1480000},
            '16215': {'12020': 1000090,
                    '15951': 15000,
                    '16215': 10000000,
                    '23151': 1000300,
                    '23545': 1030000,
                    '23547': 1480000},
            '23151': {'12020': 1000090,
                    '15951': 1000090,
                    '16215': 1090000,
                    '23151': 10000000,
                    '23545': 1030000,
                    '23547': 1480000},
            '23545': {'12020': 1000180,
                    '15951': 1000180,
                    '16215': 1180000,
                    '23151': 1000180,
                    '23545': 10000000,
                    '23547': 1180000},
            '23547': {'12020': 1000480,
                    '15951': 1000480,
                    '16215': 1480000,
                    '23151': 1000480,
                    '23545': 1030000,
                    '23547': 10000000}}
        campaigns_order_None = \
            {'Rot': 3, 'Wochenendreinigung': 3, 'Sterilisation_zu_Wochenbeginn': 3, 'Blau': 3, 'Grapefruit': 3}
        df_matrix, campaigns_order = get_changeover_matrix(products, consider_constraints=None)
        self.assertDictEqual(df_matrix.to_dict(), matrix_dict_None)
        self.assertDictEqual(campaigns_order, campaigns_order_None)

    def test_build_graph(self):
        products = {'23545', '16215', '12020', '15951', '23151', '23547'}
        edge_weights = build_graph(products, consider_constraints=0)
        # pprint(edge_weights)
        control_edge_weights = \
            {'12020': {'15951': 90000,
                    '16215': 90000,
                    '23151': 90000,
                    '23545': 180000,
                    '23547': 480000,
                    'end': 0},
            '15951': {'12020': 90000,
                    '16215': 15000,
                    '23151': 90000,
                    '23545': 180000,
                    '23547': 480000,
                    'end': 0},
            '16215': {'12020': 90000,
                    '15951': 15000,
                    '23151': 90000,
                    '23545': 180000,
                    '23547': 480000,
                    'end': 0},
            '23151': {'12020': 300000,
                    '15951': 300000,
                    '16215': 300000,
                    '23545': 180000,
                    '23547': 480000,
                    'end': 0},
            '23545': {'12020': 30000,
                    '15951': 30000,
                    '16215': 30000,
                    '23151': 30000,
                    '23547': 30000,
                    'end': 0},
            '23547': {'12020': 480000,
                    '15951': 480000,
                    '16215': 480000,
                    '23151': 480000,
                    '23545': 180000,
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
