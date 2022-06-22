"""Approach for solving the Product Ordering approach:
Interpretation of problem instance as TSP and usage of perfect encoding
"""
from typing import Sequence, Set, List, Tuple, Union
import logging
import time
import re
import os
import sys
import clingo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import PO_ENCODING, PROJECT_FOLDER, TIMEOUT
sys.path.append(PROJECT_FOLDER)
from src.experiment.utils import build_graph, create_lp_instance, ModelHelper

LOGGER = logging.getLogger('experiment')

def interpret_clingo(symbols : Sequence[clingo.Symbol]) -> List[str]:
    """Parsing the command line output of the answer set solver clingo for extracting the
    resulting order of products for the TSP encoding

    Args:
        symbols (Sequence[clingo.Symbol]): set of symbols outputted by clingo

    Returns:
        List[str]: optimal product order
    """
    pattern_switch = re.compile(r'switch\((\w*),(\w*)\)')
    pattern_start = re.compile(r'switch\(v,(\w*)\)')
    pattern_end = re.compile(r'switch\((\w*),v\)')

    start = None
    end = None
    order_dict = {}
    for symbol in symbols:
        atom = str(symbol)
        result_switch = pattern_switch.match(atom)
        result_start = pattern_start.match(atom)
        result_end = pattern_end.match(atom)

        if result_switch:
            product1 = result_switch.group(1)
            product2 = result_switch.group(2)
            assert product1 not in order_dict
            order_dict[product1] = product2

        if result_start:
            start = result_start.group(1)

        if result_end:
            end = result_end.group(1)

    assert start is not None
    assert end is not None

    order = []
    current = start
    while current != end:
        order.append(current)
        current = order_dict[current]
    order.append(end)

    return order

def run_logic_program(products : Set[str], run : int, start : Union[str, None] = None, \
    end : Union[str, None] = None) -> Tuple[int, List[str], int, int, bool]:
    """Computing the Product Ordering problem as a logic program using the perfect TSP encoding;
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
    edge_weights = build_graph(products, start, end, cyclic=True, consider_campaigns=False)
    instance = create_lp_instance(edge_weights)

    filename = os.path.join(PROJECT_FOLDER, 'experiments', 'instances', 'lp',
        f'instance_{len(products)}_{run}.lp')
    if not os.path.exists(filename):
        with open(filename, 'w') as filehandle:
            filehandle.write(instance)

    ctl = clingo.Control()
    ctl.load(PO_ENCODING)
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
