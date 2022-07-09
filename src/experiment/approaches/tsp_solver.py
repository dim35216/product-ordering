"""Approach for solving the Product Ordering approach:
Interpretation of problem instance as TSP and usage of the concorde tsp solver
"""
from typing import *
import logging
import subprocess
import time
import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import PRODUCT_PROPERTIES, CONCORDE_EXE, PROJECT_FOLDER, \
    INSTANCES_FOLDER, TIMEOUT, INF
sys.path.append(PROJECT_FOLDER)
from src.experiment.utils import get_changeover_matrix, create_tsp_instance, \
    interpret_tsp_solution, transform_symmetric

LOGGER = logging.getLogger('experiment')

def build_graph(products : Set[str], start : Union[str, None] = None, \
    end : Union[str, None] = None, cyclic : bool = False,
    consider_constraints : Union[None, int] = None) \
    -> Union[List[Dict[str, Dict[str, int]]], Dict[str, Dict[str, int]]]:
    """Building a graph instance for the given changeover matrix, whereas only the products in
    the given set are taken into account, such that the graph instance won't be bigger than
    necessary. Additionally a start and end product can be given. For the construction of a graph
    with option cyclic, an additional node V is included. If the option cyclic is not given, the
    additional node V is substituted by a start and an end node, which are not connected to each
    other. For the edges between the added node(s) and the remaining product nodes, the following
    rules apply:
    If a start product is specified:
      The node V is connected with an outgoing arc to the start product with cost 0
      To all remaining nodes, the node V is connected with an outgoing arc of cost INF
    Else:
      The node V is connected to all other nodes with an outgoing arc of cost 0

    If an end product is specified:
      The node V is connected with an ingoing arc to the end product with cost 0
      To all remaining nodes, the node V is connected with an ingoing arc of cost INF
    Else:
      The node V is connected to all other nodes with an ingoing arc of cost 0

    Args:
        products (Set[str]): set of products
        start (Union[str, None], optional): start product. Defaults to None.
        end (Union[str, None], optional): end product. Defaults to None.
        cyclic (bool, optional): model as cyclic graph instance. Defaults to False.
        consider_side_constraints (bool, optional): consider the campaigns of products. Defaults to False.

    Returns:
        Dict[str, Dict[str, int]]: graph instance
    """
    assert start is None or start in products
    assert end is None or end in products
    df_matrix, campaigns_order = get_changeover_matrix(products, consider_constraints)
    df_properties = pd.read_csv(PRODUCT_PROPERTIES, dtype={'Product': str}).set_index('Product')

    if consider_constraints >= 4:
        LOGGER.error('These constraints haven\'t been implemented yet!')

    edge_weights : Dict[str, Dict[str, int]] = {}
    for product1 in products:
        edge_weights[product1] = {}
        for product2 in products:
            distance = df_matrix.at[product1, product2]
            if distance < INF:
                edge_weights[product1][product2] = distance

    if cyclic:
        edge_weights['v'] = {}
    else:
        edge_weights['start'] = {}
        edge_weights['end'] = {}

    if start is None:
        for product in products:
            campaign_order = campaigns_order[df_properties.at[product, 'Campaign']]
            if not (consider_constraints is None or consider_constraints >= 1) \
                or campaign_order == 0:
                if cyclic:
                    edge_weights['v'][product] = 0
                else:
                    edge_weights['start'][product] = 0
    else:
        if consider_constraints is None or consider_constraints >= 1:
            campaign_order = campaigns_order[df_properties.at[start, 'Campaign']]
            assert campaign_order == 0
        if cyclic:
            edge_weights['v'][start] = 0
        else:
            edge_weights['start'][start] = 0

    max_campaign = max([value for _, value in campaigns_order.items()])
    if end is None:
        for product in products:
            campaign_order = campaigns_order[df_properties.at[product, 'Campaign']]
            if not (consider_constraints is None or consider_constraints >= 1) \
                or campaign_order == max_campaign:
                if cyclic:
                    edge_weights[product]['v'] = 0
                else:
                    edge_weights[product]['end'] = 0
    else:
        if consider_constraints is None or consider_constraints >= 1:
            campaign_order = campaigns_order[df_properties.at[end, 'Campaign']]
            assert campaign_order == max_campaign
        if cyclic:
            edge_weights[end]['v'] = 0
        else:
            edge_weights[end]['end'] = 0
    
    return edge_weights

def run_concorde(products : Set[str], run : int, start : Union[str, None] = None, \
    end : Union[str, None] = None, consider_constraints : Union[None, int] = None) \
    -> Tuple[List[str], bool]:
    """Computing the Product Ordering problem using the concorde tsp solver. Therefore it's
    necessary to transform the asymmetric problem instance to a symmetric one, and save the
    instance in the tsplib95 format.

    Args:
        products (Set[str]): set of products
        run (int): id of run
        start (Union[str, None], optional): start product. Defaults to None.
        end (Union[str, None], optional): end product. Defaults to None.

    Returns:
        Tuple[List[str], bool]: optimal product order, flag for timeout occurred
    """
    edge_weights = build_graph(products, start, end, cyclic=True, consider_constraints=consider_constraints)

    start_time = time.time()
    sym_edge_weights = transform_symmetric(edge_weights)
    instance, products_list = create_tsp_instance(sym_edge_weights)

    filename_tsp = os.path.join(INSTANCES_FOLDER, 'tsp', f'instance_{len(products)}_{run}.tsp')

    instance.save(filename_tsp)

    filename_sol = os.path.join(INSTANCES_FOLDER, 'tsp', f'instance_{len(products)}_{run}.sol')

    try:
        args = [CONCORDE_EXE, '-f', '-x', '-o', filename_sol, filename_tsp]
        subprocess.run(args, capture_output=True, text=True, timeout=TIMEOUT - time.time() + start_time)
    except subprocess.TimeoutExpired:
        LOGGER.info('The time limit is exceeded.')
        return [], True

    assert os.path.exists(filename_sol)
    order = interpret_tsp_solution(filename_sol, products_list)

    return order, False
