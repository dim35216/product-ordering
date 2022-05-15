import time
from typing import Set
import pandas as pd
import logging
import os
import sys

class Modeler:
    def __init__(self, matrix):
        self.matrix = matrix

    def create_instance(self, products : Set[str], filename : str) -> None:
        """Modelling an Product Ordering problem instance as a classical planning problem with
        preferences with the help of PDDL

        Args:
            products (Set[str]): set of products
            filename (str): name of resulting PDDL instance file
        """
        df_matrix = pd.read_csv(self.matrix, index_col=0)

        result = \
f'''(define (problem ProductOrdering-{filename})
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

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(result)
        return

#-----------------------------------------------
# Main
#-----------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Please give the following command line arguments: ' + \
            'python [./]modeler.py <products> <filename>')
        sys.exit(1)
    products = sys.argv[1]
    filename = sys.argv[2]
    logging.basicConfig(level=logging.INFO)
    logging.info('Modeler started')
    start_time = time.time()
    modeler = Modeler()
    pi = modeler.create_instance(products, filename)
    if not os.path.exists(filename):
        logging.error('Modelling was not possible')
        exit(1)
    logging.info('Translator ended after %ss', str(time.time() - start_time))
