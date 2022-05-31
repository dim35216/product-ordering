"""Approach for solving the Product Ordering approach:
Interpretation of problem instance as TSP and usage of bad encoding
"""
from typing import Set, Tuple, List, Union
import logging
import time
import os
import sys
import clingo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import BAD_ENCODING, PROJECT_FOLDER, TIMEOUT
sys.path.append(os.path.abspath(PROJECT_FOLDER))
from src.experiment.approaches.tsp import interpret_clingo
from src.experiment.utils import build_graph, create_lp_instance, ModelHelper

LOGGER = logging.getLogger('experiment')

def run_bad_encoding(products : Set[str], run : int, start : Union[str, None] = None, \
    end : Union[str, None] = None) -> Tuple[int, List[str], int, int, bool]:
    """Computing the Product Ordering problem as a logic program using the bad TSP encoding;
    therefore the Product Ordering problem instance has to transformed into a TSP instance using
    a little additional logic program

    Args:
        products (Set[str]): set of products
        run (int): id of run
        start (Union[str, None], optional): start product. Defaults to None.
        end (Union[str, None], optional): end product. Defaults to None.

    Returns:
        Tuple[int, List[str], int, int, bool]: objective value, optimal product order, number of \
            ground rules, number of calculated models, flag for timeout occurred
    """
    edge_weights = build_graph(products, start, end, cyclic=True)
    instance = create_lp_instance(edge_weights)

    filename = os.path.join(PROJECT_FOLDER, 'experiments', 'instances', 'bad',
        f'instance_{len(products)}_{run}.lp')
    with open(filename, 'w') as filehandle:
        filehandle.write(instance)

    ctl = clingo.Control()
    ctl.load(BAD_ENCODING)
    ctl.add('base', [], instance)
    ctl.ground([('base', [])])

    modelHelper = ModelHelper()
    start_time = time.time()
    solve_handle : clingo.SolveHandle
    with ctl.solve(on_model=modelHelper.on_model, on_finish=modelHelper.on_finish,
        async_=True) as solve_handle: # type: ignore
        while not solve_handle.wait(timeout=10.0):
            if time.time() - start_time > TIMEOUT:
                break

    if not modelHelper.exhausted:
        LOGGER.info('The time limit is exceeded.')
        return -1, [], -1, -1, True

    if not modelHelper.optimal:
        LOGGER.info('The problem does not have an optimal solution.')
        return -1, [], -1, -1, False

    order = interpret_clingo(modelHelper.symbols)
    assert len(order) == len(products)

    rules = int(ctl.statistics['problem']['lp']['rules'])
    opt_value = int(ctl.statistics['summary']['costs'][0])
    models = int(ctl.statistics['summary']['models']['enumerated'])

    return opt_value, order, rules, models, False
