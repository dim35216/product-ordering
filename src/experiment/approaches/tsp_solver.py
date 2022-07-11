"""Approach for solving the Product Ordering approach:
Interpretation of problem instance as TSP and usage of the concorde tsp solver
"""
from typing import Set, List, Union, Tuple
import logging
import subprocess
import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import CONCORDE_EXE, PROJECT_FOLDER, INSTANCES_FOLDER, TIMEOUT
sys.path.append(PROJECT_FOLDER)
from src.experiment.utils import calculate_oct, build_graph, create_tsp_instance, \
    interpret_tsp_solution, transform_symmetric

LOGGER = logging.getLogger('experiment')

def run_concorde(products : Set[str], run : int, start : Union[str, None] = None, \
    end : Union[str, None] = None) -> Tuple[List[str], bool]:
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
    edge_weights_list = build_graph(products, start, end, cyclic=True)

    start_time = time.time()
    min_oct = 10080
    min_order = []
    for index, edge_weights in enumerate(edge_weights_list):
        sym_edge_weights = transform_symmetric(edge_weights)
        instance, products_list = create_tsp_instance(sym_edge_weights)

        filename_tsp = os.path.join(INSTANCES_FOLDER, 'tsp', f'instance_{len(products)}_{run}_{index}.tsp')

        instance.save(filename_tsp)

        filename_sol = os.path.join(INSTANCES_FOLDER, 'tsp', f'instance_{len(products)}_{run}_{index}.sol')

        try:
            args = [CONCORDE_EXE, '-f', '-x', '-o', filename_sol, filename_tsp]
            subprocess.run(args, capture_output=True, text=True, timeout=TIMEOUT - time.time() + start_time)
        except subprocess.TimeoutExpired:
            LOGGER.info('The time limit is exceeded.')
            return [], True

        assert os.path.exists(filename_sol)
        cur_order = interpret_tsp_solution(filename_sol, products_list)

        cur_oct = calculate_oct(cur_order)
        if cur_oct < min_oct:
            min_oct = cur_oct
            min_order = cur_order
    
    return min_order, False
