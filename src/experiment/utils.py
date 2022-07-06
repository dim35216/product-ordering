"""Collection of auxiliary functions for conducting a computational experiment
"""
from typing import *
from itertools import permutations
import logging
import tsplib95
import os
import sys
import clingo
import pandas as pd
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from constants.constants import CHANGEOVER_MATRIX, CAMPAIGNS_ORDER, PRODUCT_PROPERTIES, PRODUCT_QUANTITY

def setup_logger() -> None:
    """Auxiliary method for getting a logger, which even works in the parallelized joblib
    environment
    """
    logger = logging.getLogger('experiment')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(message)s ' + \
        '[in %(pathname)s:%(lineno)d]')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False

def calculate_oct(order: List[str], occurences : Union[Dict[str, int], None] = None) -> int:
    """Calculate the overall changeover time for a given product order and the changeover matrix

    Args:
        order (List[str]): product order
        occurences (Union[Dict[str, int], None], optional): Indicating the number of occurences \
            per product. If None, every product appears once. Defaults to None.

    Returns:
        int: overall changeover time
    """
    assert len(order) == len(set(order))
    df_matrix = pd.read_csv(CHANGEOVER_MATRIX, index_col=0)
    changeover_time = 0
    for i in range(1, len(order)):
        product1 = order[i - 1]
        product2 = order[i]
        changeover_time += df_matrix.at[int(product1), product2]
    if occurences is not None:
        for num in occurences.values():
            assert num >= 1
            changeover_time += (num - 1) * 15
    return changeover_time

def build_graph(products : Set[str], start : Union[str, None] = None, \
    end : Union[str, None] = None, cyclic : bool = False,
    consider_campaigns : bool = True) \
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
      To all remaining nodes, the node V is connected with an outgoing arc of cost 10080
    Else:
      The node V is connected to all other nodes with an outgoing arc of cost 0

    If an end product is specified:
      The node V is connected with an ingoing arc to the end product with cost 0
      To all remaining nodes, the node V is connected with an ingoing arc of cost 10080
    Else:
      The node V is connected to all other nodes with an ingoing arc of cost 0

    Args:
        products (Set[str]): set of products
        start (Union[str, None], optional): start product. Defaults to None.
        end (Union[str, None], optional): end product. Defaults to None.
        cyclic (bool, optional): model as cyclic graph instance. Defaults to False.
        consider_campaigns (bool, optional): consider the campaigns of products. Defaults to True.

    Returns:
        Dict[str, Dict[str, int]]: graph instance
    """
    assert start is None or start in products
    assert end is None or end in products
    df_matrix = pd.read_csv(CHANGEOVER_MATRIX, index_col=0)
    df_properties = pd.read_csv(PRODUCT_PROPERTIES, index_col='Product')
    campaigns = set([df_properties.at[int(product), 'Campaign'] for product in products])
    df_order = pd.read_csv(CAMPAIGNS_ORDER, index_col='Campaign')
    campaigns_order = dict((campaign, df_order['Order'].to_dict()[campaign]) for campaign in campaigns)

    if consider_campaigns:
        counter = 0
        for step in sorted(df_order['Order'].drop_duplicates().to_list()):
            step_campaigns = campaigns.intersection(df_order[df_order['Order'] == step].index.to_list())
            if len(step_campaigns) != 0:
                for campaign in campaigns:
                    campaigns_order[campaign] = counter
                counter += 1
    else:
        for campaign in campaigns_order:
            campaigns_order[campaign] = -1

    edge_weights : Dict[str, Dict[str, int]] = {}
    for product1 in products:
        edge_weights[product1] = {}
        campaign1 = df_properties.at[int(product1), 'Campaign']
        campaign_order1 = campaigns_order[campaign1]
        for product2 in products:
            campaign2 = df_properties.at[int(product2), 'Campaign']
            campaign_order2 = campaigns_order[campaign2]
            if campaign_order2 - campaign_order1 not in [0, 1]:
                continue
            distance = df_matrix.at[int(product1), product2]
            if distance < 10080:
                if campaign1 != campaign2:
                    distance = 10080
                edge_weights[product1][product2] = distance

    if cyclic:
        edge_weights['v'] = {}
    else:
        edge_weights['start'] = {}
        edge_weights['end'] = {}

    if start is None:
        for product in products:
            campaign_order = campaigns_order[df_properties.at[int(product), 'Campaign']]
            if campaign_order in [-1, 0]:
                if cyclic:
                    edge_weights['v'][product] = 0
                else:
                    edge_weights['start'][product] = 0
    else:
        campaign_order = 0
        if consider_campaigns:
            campaign = df_properties.at[int(start), 'Campaign']
            campaign_order = campaigns_order[campaign]
            assert campaign_order == 0
        if cyclic:
            edge_weights['v'][start] = 0
        else:
            edge_weights['start'][start] = 0

    if end is None:
        for product in products:
            campaign = df_properties.at[int(product), 'Campaign']
            campaign_order = campaigns_order[campaign]
            if campaign_order == len(campaigns_order):
                if cyclic:
                    edge_weights[product]['v'] = 0
                else:
                    edge_weights[product]['end'] = 0
    else:
        campaign = df_properties.at[int(end), 'Campaign']
        campaign_order = campaigns_order[campaign]
        assert campaign_order in [0, len(campaigns_order)]
        if cyclic:
            edge_weights[end]['v'] = 0
        else:
            edge_weights[end]['end'] = 0
    
    return edge_weights

def create_lp_instance(products : Set[str]) -> str:
    """Modelling a Product Ordering problem instance as a logic program in Answer Set Programming

    Args:
        products (Set[str]): set of products

    Returns:
        str: resulting LP source code
    """
    df_matrix = pd.read_csv(CHANGEOVER_MATRIX, index_col=0)
    df_order = pd.read_csv(CAMPAIGNS_ORDER, index_col='Campaign')
    df_properties = pd.read_csv(PRODUCT_PROPERTIES, index_col='Product')
    df_quantity = pd.read_csv(PRODUCT_QUANTITY, index_col='Product')

    result : str = ''
    for product in products:
        result += f'product({product}).\n'
    for product1 in products:
        for product2 in products:
            distance = df_matrix.at[int(product1), product2]
            if distance < 10080:
                result += f'changeover({product1}, {product2}).\n'
                result += f'changeover_time({product1}, {product2}, {distance}).\n'
    for product in products:
        result += f'campaign({product}, "{df_properties.at[int(product), "Campaign"]}").\n'
        result += f'volume({product}, {df_properties.at[int(product), "Volume"]}).\n'
        result += f'packaging({product}, "{df_properties.at[int(product), "Packaging"]}").\n'
        result += f'quantity({product}, {df_quantity.at[int(product), "Quantity"]}).\n'
    for campaign, order in df_order['Order'].items():
        result += f'campaign_order("{campaign}", {order}).\n'

    return result

def create_tsp_instance(edge_weights : Dict[str, Dict[str, int]]) -> \
    Tuple[tsplib95.models.StandardProblem, List[str]]:
    """Creating a Product Ordering problem instance in the tsplib95 format

    Args:
        edge_weights (Dict[str, Dict[str, int]]): model of graph of problem instance

    Returns:
        Tuple[tsplib95.models.StandardProblem, List[str]]: tsp problem instance in the tsplib95 \
            format, products in fixed listed order used in the problem instance
    """
    matrix = np.ones((len(edge_weights), len(edge_weights)), dtype=int) * 99999

    products_list = list(edge_weights)
    index_products = {}
    for index, product in enumerate(products_list):
        index_products[product] = index
    for product1 in edge_weights:
        for product2, value in edge_weights[product1].items():
            matrix[index_products[product1]][index_products[product2]] = value
    
    problem = tsplib95.models.StandardProblem(
        type='TSP',
        edge_weight_type='EXPLICIT',
        edge_weight_format='FULL_MATRIX',
        dimension=len(edge_weights),
        edge_weights=matrix
    )

    return problem, products_list

def interpret_tsp_solution(filename : str, products_list : List[str]) -> List[str]:
    """Interpreting the solution file of the concorde tsp solver in the tsplib95 format

    Args:
        filename (str): solution file
        products_list (List[str]): products in fixed listed order used in the problem instance

    Returns:
        List[str]: optimal product order
    """
    index_list = []
    with open(filename, 'r', encoding='UTF-8') as filehandle:
        lines = filehandle.readlines()
        assert len(lines) > 1
        lines = [line.rstrip() for line in lines]
        dimensions = lines[0].split(' ')
        assert (len(dimensions) == 2) and (dimensions[0] == dimensions[1])
        dimension = int(dimensions[0])
        index1, index2, _ = lines[1].split(' ')
        index_list.append(int(index1))
        index_list.append(int(index2))
        for line in lines[2:]:
            prev_index, cur_index, _ = line.split(' ')
            assert int(prev_index) == index_list[-1]
            index_list.append(int(cur_index))
        assert index_list[0] == index_list[-1]
        index_list = index_list[:-1]
        assert len(index_list) == dimension

    temp = [products_list[index] for index in index_list]
    index_v = temp.index('v')
    temp = temp[index_v:] + temp[:index_v]
    index_v_v = temp.index('v_v')
    assert temp.index('v') == 0
    assert index_v_v in [1, len(temp) - 1]
    if index_v_v == len(temp) - 1:
        temp = temp[1:] + ['v']
        temp.reverse()
    assert len(temp) % 2 == 0
    
    order = []
    for i in range(len(temp) // 2):
        assert temp[2 * i] + '_v' == temp[2 * i + 1]
        order.append(temp[2 * i])

    order = order[1:]

    return order

def transform_symmetric(edge_weights : Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, int]]:
    """Transforming an asymmetric graph instance into a symmetric one. Herby, the procedure is used
    in reference to the article https://home.engineering.iastate.edu/~rkumar/PUBS/atsp.pdf

    Args:
        edge_weights (Dict[str, Dict[str, int]]): model of asymmetric graph

    Returns:
        Dict[str, Dict[str, int]]: model of symmetric graph
    """
    sym_edge_weights : Dict[str, Dict[str, int]] = {}
    for product in edge_weights:
        sym_edge_weights[product] = {}
    for product in edge_weights:
        sym_edge_weights[product + '_v'] = {}

    edge_weights_list = []
    for product1 in edge_weights:
        for product2 in edge_weights[product1]:
            if product1 == product2:
                continue
            edge_weights_list.append(edge_weights[product1][product2])

    d_min = min(edge_weights_list)
    d_max = max(edge_weights_list)
    if 4 * d_min - 3 * d_max > 0:
        for product1 in edge_weights:
            for product2 in edge_weights[product1]:
                sym_edge_weights[product2][product1 + '_v'] = edge_weights[product1][product2]
                sym_edge_weights[product1 + '_v'][product2] = edge_weights[product1][product2]
            sym_edge_weights[product1][product1 + '_v'] = 0
            sym_edge_weights[product1 + '_v'][product1] = 0
    else:
        summand = 3 * d_max - 4 * d_min + 1
        for product1 in edge_weights:
            for product2 in edge_weights[product1]:
                sym_edge_weights[product2][product1 + '_v'] = edge_weights[product1][product2] + summand
                sym_edge_weights[product1 + '_v'][product2] = edge_weights[product1][product2] + summand
            sym_edge_weights[product1][product1 + '_v'] = 0
            sym_edge_weights[product1 + '_v'][product1] = 0

    return sym_edge_weights

class ModelHelper():
        def __init__(self):
            self.symbols = None
            self.exhausted = False
            self.optimal = False

        def on_model(self, model : clingo.Model):
            self.symbols = model.symbols(shown=True)

        def on_finish(self, solve_result : clingo.SolveResult):
            self.exhausted = solve_result.exhausted
            self.optimal = solve_result.satisfiable and solve_result.exhausted
