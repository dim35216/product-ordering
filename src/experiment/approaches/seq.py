"""Approach for solving the Product Ordering approach:
Interpretation of problem instance as TSP and usage of sequential encoding
"""
from typing import Set, Tuple, List
import logging
import time
import os
import sys
import clingo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import TSP_ENCODING, PROJECT_FOLDER, TIMEOUT
sys.path.append(os.path.abspath(PROJECT_FOLDER))
from src.experiment.approaches.tsp import interpret_clingo
from src.experiment.utils import calculate_oct, build_graph, create_lp_instance, ModelHelper

LOGGER = logging.getLogger('experiment')

def run_seq_encoding(products : Set[str], run : int) -> Tuple[List[int], int, int, bool]:
    """Computing the Product Ordering problem as a logic program using the perfect TSP encoding,
    but the start and end product is specified explicitly; as a consequence, the solver runs O(n^2)
    times; in each run, the Product Ordering problem instance has to transformed into a TSP
    instance using a little additional logic program

    Args:
        products (Set[str]): set of products
        run (int): id of run
        start (Union[str, None], optional): start product. Defaults to None.
        end (Union[str, None], optional): end product. Defaults to None.

    Returns:
        Tuple[List[str], int, int, bool]: optimal product order, number of ground rules, number \
            of calculated models, flag for timeout occurred
    """
    overall_rules = 0
    overall_models = 0
    min_oct = 10080
    min_order = []
    start_time = time.time()
    for product1 in products:
        for product2 in products:
            if product1 != product2:
                edge_weights = build_graph(products, start=product1, end=product2, cyclic=True)
                instance = create_lp_instance(edge_weights)

                filename = os.path.join(PROJECT_FOLDER, 'experiments', 'instances', 'tsp',
                    f'instance_{len(products)}_{run}_{product1}_{product2}.lp')
                with open(filename, 'w') as filehandle:
                    filehandle.write(instance)

                ctl = clingo.Control()
                ctl.load(TSP_ENCODING)
                ctl.add('base', [], instance)
                ctl.ground([('base', [])])

                modelHelper = ModelHelper()
                solve_handle : clingo.SolveHandle
                with ctl.solve(on_model=modelHelper.on_model, on_finish=modelHelper.on_finish,
                    async_=True) as solve_handle: # type: ignore
                    while not solve_handle.wait(timeout=10.0):
                        if time.time() - start_time > TIMEOUT:
                            break

                if not modelHelper.exhausted:
                    LOGGER.info('The time limit is exceeded.')
                    return [], -1, -1, True

                if not modelHelper.optimal:
                    LOGGER.info('The problem does not have an optimal solution.')
                    return [], -1, -1, False

                order = interpret_clingo(modelHelper.symbols)
                assert len(order) == len(products)

                rules = int(ctl.statistics['problem']['lp']['rules'])
                models = int(ctl.statistics['summary']['models']['enumerated'])

                overall_rules += rules
                overall_models += models

                cur_oct = calculate_oct(order)
                if cur_oct < min_oct:
                    min_oct = cur_oct
                    min_order = order

    return min_order, overall_rules, overall_models, False
