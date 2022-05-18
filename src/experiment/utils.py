"""Collection of auxiliary functions for conducting a computational experiment
"""
from typing import List, Dict, Union, Set
import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from constants.constants import CHANGEOVER_MATRIX

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
    end : Union[str, None] = None, cyclic : bool = False) -> Dict[str, Dict[str, int]]:
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
        products (Set[str]): _description_
        start (Union[str, None], optional): _description_. Defaults to None.
        cyclic (bool, optional): _description_. Defaults to False.

    Returns:
        Dict[str, Dict[str, int]]: _description_
    """
    assert start is None or start in products
    assert end is None or end in products
    edge_weights : Dict[str, Dict[str, int]] = {}
    df_matrix = pd.read_csv(CHANGEOVER_MATRIX, index_col=0)
    for product1 in products:
        edge_weights[product1] = {}
        for product2 in products:
            value = df_matrix.at[int(product1), product2]
            if value < 10080:
                edge_weights[product1][product2] = value
    if cyclic:
        edge_weights['v'] = {}
    else:
        edge_weights['start'] = {}
        edge_weights['end'] = {}
    if start is None:
        for product in products:
            if cyclic:
                edge_weights['v'][product] = 0
            else:
                edge_weights['start'][product] = 0
    else:
        if cyclic:
            edge_weights['v'][start] = 0
        else:
            edge_weights['start'][start] = 0
    if end is None:
        for product in products:
            if cyclic:
                edge_weights[product]['v'] = 0
            else:
                edge_weights[product]['end'] = 0
    else:
        if cyclic:
            edge_weights[end]['v'] = 0
        else:
            edge_weights[end]['end'] = 0
    return edge_weights

def create_tsp_instance(edge_weights : Dict[str, Dict[str, int]]) -> str:
    """Modelling an Product Ordering problem instance as a logic program in Answer Set Programming

    Args:
        edge_weights (Dict[str, Dict[str, int]]): model of graph of problem instance
        filename (str): file to resulting LP instance file
    """
    result : str = ''
    for product in edge_weights:
        result += f'node({product}).\n'
    for product1 in edge_weights:
        for product2 in edge_weights[product1]:
            result += f'edge({product1}, {product2}).\n'
    for product1 in edge_weights:
        for product2 in edge_weights[product1]:
            result += f'cost({product1}, {product2}, {edge_weights[product1][product2]}).\n'

    return result
