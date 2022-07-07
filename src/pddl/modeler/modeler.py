from typing import Set
import time
import logging
import argparse
import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import CHANGEOVER_MATRIX, CAMPAIGNS_ORDER, PRODUCT_PROPERTIES

class Modeler:
    """This class implements a modeler, which takes an instance of the Product Ordering problem
       and describes it in PDDL (Planning Domain Definition Language)
    """

    def create_instance(self, products : Set[str], filename : str) -> None:
        """Modelling an Product Ordering problem instance as a classical planning problem with
        preferences with the help of PDDL

        Args:
            products (Set[str]): set of products
            filename (str): name of resulting PDDL instance file
        """
        df_matrix = pd.read_csv(CHANGEOVER_MATRIX, dtype={'Product': str}).set_index('Product')
        df_properties = pd.read_csv(PRODUCT_PROPERTIES, dtype={'Product': str}).set_index('Product')
        campaigns = set([df_properties.at[product, 'Campaign'] for product in products])
        df_order = pd.read_csv(CAMPAIGNS_ORDER, index_col='Campaign')

        problemname = os.path.split(filename)[-1].split('.')[0]

        result = \
f'''(define (problem ProductOrdering-{problemname})
    (:domain ProductOrdering)

(:objects'''
        for product in products:
            result += f'\n    p{product}'
        result += \
'''
    pstart
    pend - product'''
        for campaign in campaigns:
            result += f'\n    "{campaign}"'
        result += \
'''
    Start
    End - campaign
)

(:init
    (not-initialized)
'''
        for product1 in products:
            result += f'    (changeover pstart p{product1})\n'
            result += f'    (= (changeover-time pstart p{product1}) 0)\n'
            result += f'    (changeover p{product1} pend)\n'
            result += f'    (= (changeover-time p{product1} pend) 0)\n'
            for product2 in products:
                distance = df_matrix.at[product1, product2]
                if distance < 10080:
                    result += f'    (changeover p{product1} p{product2})\n'
                    result += f'    (= (changeover-time p{product1} p{product2}) {distance})\n'
        for product in products:
            result += f'    (product-campaign p{product} "{df_properties.at[product, "Campaign"]}")\n'
        result += f'    (product-campaign pstart Start)\n'
        result += f'    (product-campaign pend End)\n'
        for campaign in campaigns:
            result += f'    (campaign-switch-possible Start "{campaign}")\n'
        for campaign in campaigns:
            result += f'    (campaign-switch-possible "{campaign}" End)\n'
        for campaign1 in campaigns:
            for campaign2 in campaigns:
                order1 = df_order.at[campaign1, 'Order']
                order2 = df_order.at[campaign2, 'Order']
                if 0 <= order2 - order1 and campaign1 != campaign2:
                    result += f'    (campaign-switch-possible "{campaign1}" "{campaign2}")\n'
        result += \
''')

(:goal
    (and
        (finalized)
'''
        result += f'        (product-processed pstart)\n'
        result += f'        (product-processed pend)\n'
        for product in products:
            result += f'        (product-processed p{product})\n'
        for campaign in campaigns:
            result += f'        (campaign-processed "{campaign}")\n'
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
