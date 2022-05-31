"""Approach for solving the Product Ordering approach:
Interpretation of problem instance as TSP and usage of bad encoding
"""
from typing import Set, Tuple, List, Union
import logging
import os
import sys
import clingo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import BAD_ENCODING, PROJECT_FOLDER
sys.path.append(os.path.abspath(PROJECT_FOLDER))
from src.experiment.approaches.tsp import interpret_clingo
from src.experiment.utils import build_graph, create_lp_instance

LOGGER = logging.getLogger('experiment')

def run_bad_encoding(products : Set[str], run : int, start : Union[str, None] = None, \
    end : Union[str, None] = None) -> Tuple[int, List[str], int, int]:
    """Computing the Product Ordering problem as a logic program using the bad TSP encoding;
    therefore the Product Ordering problem instance has to transformed into a TSP instance using
    a little additional logic program

    Args:
        products (Set[str]): set of products
        run (int): id of run
        start (Union[str, None], optional): start product. Defaults to None.
        end (Union[str, None], optional): end product. Defaults to None.

    Returns:
        Tuple[int, List[str], int, int]: objective value, optimal product order, number of ground \
            rules, number of calculated models
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
    solve_handle = ctl.solve(yield_=True)
    assert isinstance(solve_handle, clingo.SolveHandle)
    model = None
    for model in solve_handle:
        pass
    if model is None:
        LOGGER.info('The problem does not have an optimal solution.')
        return -1, [], -1, -1
    order = interpret_clingo(model.symbols(shown=True))
    assert len(order) == len(products)

    rules = int(ctl.statistics['problem']['lp']['rules'])
    opt_value = int(ctl.statistics['summary']['costs'][0])
    models = int(ctl.statistics['summary']['models']['enumerated'])

    return opt_value, order, rules, models
