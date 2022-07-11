"""Approach for solving the Product Ordering approach:
Interpretation of problem instance as TSP, transformation into a linear program and usage of
perfect and bad encoding
"""
from typing import Sequence, Set, List, Tuple, Union, Dict, Any
import logging
import time
import re
import os
import sys
import clingo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import PERFECT_TSP_ENCODING, BAD_TSP_ENCODING, PROJECT_FOLDER, TIMEOUT
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
    pattern_cycle = re.compile(r'cycle\((\w*),(\w*)\)')
    pattern_start = re.compile(r'cycle\(v,(\w*)\)')
    pattern_end = re.compile(r'cycle\((\w*),v\)')

    start = None
    end = None
    order_dict = {}
    for symbol in symbols:
        atom = str(symbol)
        result_cycle = pattern_cycle.match(atom)
        result_start = pattern_start.match(atom)
        result_end = pattern_end.match(atom)

        if result_cycle:
            product1 = result_cycle.group(1)
            product2 = result_cycle.group(2)
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

def run_clingo(products : Set[str], run : int, start : Union[str, None] = None, \
    end : Union[str, None] = None, encoding : str = 'perfect') -> \
    Tuple[int, List[str], Dict[str, Any], bool]:
    """Computing the Product Ordering problem as a logic program using the perfect or bad TSP
    encoding

    Args:
        products (Set[str]): set of products
        run (int): id of run
        start (Union[str, None], optional): start product. Defaults to None.
        end (Union[str, None], optional): end product. Defaults to None.

    Returns:
        Tuple[int, List[str], Dict[str, Any], bool]: objective value, optimal product order, \
            dictionary of clingo statistics, flag for timeout occurred
    """
    assert encoding in ['perfect', 'bad']

    edge_weights = build_graph(products, start, end, cyclic=True)
    instance = create_lp_instance(edge_weights)

    filename = os.path.join(PROJECT_FOLDER, 'experiments', 'instances', 'lp',
        f'instance_{len(products)}_{run}.lp')
    if not os.path.exists(filename):
        with open(filename, 'w') as filehandle:
            filehandle.write(instance)

    ctl = clingo.Control()
    if encoding == 'perfect':
        ctl.load(PERFECT_TSP_ENCODING)
    else:
        ctl.load(BAD_TSP_ENCODING)
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
        return -1, [], {}, True

    if not modelHelper.optimal:
        LOGGER.info('The problem does not have an optimal solution.')
        return -1, [], {}, False

    order = interpret_clingo(modelHelper.symbols)
    assert len(order) == len(products)

    opt_value = int(ctl.statistics['summary']['costs'][0])

    constraints = int(ctl.statistics['problem']['generator']['constraints'])
    complexity = int(ctl.statistics['problem']['generator']['complexity'])
    vars = int(ctl.statistics['problem']['generator']['vars'])

    atoms = int(ctl.statistics['problem']['lp']['atoms'])
    bodies = int(ctl.statistics['problem']['lp']['bodies'])
    rules = int(ctl.statistics['problem']['lp']['rules'])

    choices = int(ctl.statistics['solving']['solvers']['choices'])
    conflicts = int(ctl.statistics['solving']['solvers']['conflicts'])
    restarts = int(ctl.statistics['solving']['solvers']['restarts'])

    models = int(ctl.statistics['summary']['models']['enumerated'])

    stats = {
        'Constraints': constraints,
        'Complexity': complexity,
        'Vars': vars,
        'Atoms': atoms,
        'Bodies': bodies,
        'Rules': rules,
        'Choices': choices,
        'Conflicts': conflicts,
        'Restarts': restarts,
        'Models': models
    }

    return opt_value, order, stats, False