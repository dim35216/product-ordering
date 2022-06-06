from typing import Dict
import time
import logging
import argparse
import os
import sys

class Modeler:
    """This class implements a modeler, which takes an instance of the Product Ordering problem
       and describes it in PDDL (Planning Domain Definition Language)
    """

    def create_instance(self, edge_weights : Dict[str, Dict[str, int]], filename : str) -> None:
        """Modelling an Product Ordering problem instance as a classical planning problem with
        preferences with the help of PDDL

        Args:
            products (Set[str]): set of products
            filename (str): name of resulting PDDL instance file
        """
        problemname = os.path.split(filename)[-1].split('.')[0]

        result = \
f'''(define (problem ProductOrdering-{problemname})
    (:domain ProductOrdering)

(:objects'''
        for product in edge_weights:
            result += f'\n    p{product}'
        result += \
''' - product
)

(:init
    (not-initialized)
'''
        for product in edge_weights:
            result += f'    (to-be-processed p{product})\n'
        for product1 in edge_weights:
            for product2 in edge_weights[product1]:
                result += f'    (changeover p{product1} p{product2})\n'
        for product1 in edge_weights:
            for product2 in edge_weights[product1]:
                distance = edge_weights[product1][product2]
                result += f'    (= (changeover-time p{product1} p{product2}) {distance})\n'
        result += \
''')

(:goal
    (and
        (finalized)
'''
        for product in edge_weights:
            result += f'        (processed p{product})\n'
        result += \
'''    )
)

(:metric minimize (total-cost))

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
    modeler = Modeler()
    modeler.create_instance(products, filename)
    if not os.path.exists(filename):
        logging.error('Modelling was not possible')
        sys.exit(1)
    logging.info('Modeler ended after %ss', str(time.time() - start_time))
