from typing import Dict
import time
import logging
import argparse
import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import CHANGEOVER_MATRIX, CAMPAIGNS_ORDER

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
        df_matrix = pd.read_csv(CHANGEOVER_MATRIX, index_col=0)
        campaigns = set([df_matrix.at[int(product), 'Campaign']
            for product in edge_weights.keys() - ['start', 'end']])
        df_order = pd.read_csv(CAMPAIGNS_ORDER, index_col='Campaign')

        problemname = os.path.split(filename)[-1].split('.')[0]

        result = \
f'''(define (problem ProductOrdering-{problemname})
    (:domain ProductOrdering)

(:objects'''
        for product in edge_weights:
            result += f'\n    p{product}'
        result += \
''' - product'''
        for campaign in campaigns:
            result += f'\n    {campaign.replace(" ", "_").replace("ü", "ue")}'
        result += \
'''
    Start
    End - campaign
)

(:init
    (not-initialized)
'''
        for product1 in edge_weights:
            for product2 in edge_weights[product1]:
                result += f'    (changeover p{product1} p{product2})\n'
        for product1 in edge_weights:
            for product2 in edge_weights[product1]:
                distance = edge_weights[product1][product2]
                result += f'    (= (changeover-time p{product1} p{product2}) {distance})\n'
        for product in edge_weights:
            if product not in ['start', 'end']:
                campaign = df_matrix.at[int(product), 'Campaign']
                result += f'    (product-campaign p{product} {campaign.replace(" ", "_").replace("ü", "ue")})\n'
            else:
                result += f'    (product-campaign p{product} {product.capitalize()})\n'
        for campaign in campaigns:
            result += f'    (campaign-switch-possible Start {campaign.replace(" ", "_").replace("ü", "ue")})\n'
        for campaign in campaigns:
            result += f'    (campaign-switch-possible {campaign.replace(" ", "_").replace("ü", "ue")} End)\n'
        for campaign1 in campaigns:
            for campaign2 in campaigns:
                order1 = df_order.at[campaign1, 'Order']
                order2 = df_order.at[campaign2, 'Order']
                if 0 <= order2 - order1 and campaign1 != campaign2:
                    result += f'    (campaign-switch-possible {campaign1.replace(" ", "_").replace("ü", "ue")} {campaign2.replace(" ", "_").replace("ü", "ue")})\n'
        result += \
''')

(:goal
    (and
        (finalized)
'''
        for product in edge_weights:
            result += f'        (product-processed p{product})\n'
        for campaign in campaigns:
            result += f'        (campaign-processed {campaign.replace(" ", "_").replace("ü", "ue")})\n'
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
