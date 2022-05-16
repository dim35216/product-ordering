import time
from typing import Set
import logging
import argparse
import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import CHANGEOVER_MATRIX

class Modeler:
    """This class implements a modeler, which takes an instance of the Product Ordering problem
       and describes it in PDDL (Planning Domain Definition Language)
    """

    def __init__(self, matrix : str) -> None:
        """Constructor of PDDL modeler

        Args:
            matrix (str): path to changeover matrix
        """
        self.matrix = matrix

    def create_instance(self, products : Set[str], filename : str) -> None:
        """Modelling an Product Ordering problem instance as a classical planning problem with
        preferences with the help of PDDL

        Args:
            products (Set[str]): set of products
            filename (str): name of resulting PDDL instance file
        """
        df_matrix = pd.read_csv(self.matrix, index_col=0)
        problemname = os.path.split(filename)[-1].split('.')[0]

        result = \
f'''(define (problem ProductOrdering-{problemname})
    (:domain ProductOrdering)

(:objects'''
        for product in products:
            result += f'\n    p{product}'
        result += \
''' - product
)

(:goal
    (and
        (complete)
'''
        for product in products:
            result += f'        (worked-off p{product})\n'
        result += \
'''    )
)

(:init
'''
        for product in products:
            result += f'    (available p{product})\n'
        for product1 in products:
            for product2 in products:
                value = df_matrix[product2][int(product1)]
                result += f'    (= (changeover-time p{product1} p{product2}) {value})\n'
        result += \
''')

(:metric minimize (+ (overall-changeover-time)))

)
'''

        with open(filename, 'w', encoding='utf-8') as filehandle:
            filehandle.write(result)

#-----------------------------------------------
# Main
#-----------------------------------------------
parser = argparse.ArgumentParser(
    description='Model a Product Ordering problem instance in PDDL.' + \
    'Please give the following command line arguments: ' + \
    'python [./]modeler.py <filename> -p <products>'
    )
parser.add_argument('filename', type=str, help='name of resulting PDDL file')
parser.add_argument('-p', '--products', nargs='+')

if __name__ == '__main__':
    args = parser.parse_args()
    filename = args.filename
    products = args.products
    logging.basicConfig(level=logging.INFO)
    logging.info('Modeler started')
    start_time = time.time()
    modeler = Modeler(CHANGEOVER_MATRIX)
    modeler.create_instance(products, filename)
    if not os.path.exists(filename):
        logging.error('Modelling was not possible')
        sys.exit(1)
    logging.info('Modeler ended after %ss', str(time.time() - start_time))
