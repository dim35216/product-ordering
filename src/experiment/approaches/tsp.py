"""Approach for solving the Product Ordering approach:
Interpretation of problem instance as TSP and usage of perfect encoding
"""
from typing import Sequence, Set, List, Tuple, Union
import logging
import re
import os
import sys
import clingo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import TSP_ENCODING, PROJECT_FOLDER
sys.path.append(PROJECT_FOLDER)
from src.experiment.utils import build_graph, create_tsp_instance

def interpret_clingo(symbols : Sequence[clingo.Symbol]) -> List[str]:
    """Parsing the command line output of the answer set solver clingo for extracting the
    resulting order of products for the TSP encoding

    Args:
        symbols (Sequence[clingo.Symbol]): set of symbols outputted by clingo

    Returns:
        List[str]: optimal product order
    """
    pattern_cycle = re.compile(r'cycle\((\d*),(\d*)\)')
    pattern_start = re.compile(r'cycle\(v,(\d*)\)')
    pattern_end = re.compile(r'cycle\((\d*),v\)')

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

def run_tsp_encoding(products : Set[str], run : int, start : Union[str, None] = None, \
    end : Union[str, None] = None) -> Tuple[int, List[str], int, int]:
    """Computing the Product Ordering problem as a logic program using the perfect TSP encoding;
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
    instance = create_tsp_instance(edge_weights)

    filename = os.path.join(PROJECT_FOLDER, 'experiments', 'instances', 'tsp',
        f'instance_{len(products)}_{run}.lp')
    with open(filename, 'w') as filehandle:
        filehandle.write(instance)

    ctl = clingo.Control()
    ctl.load(TSP_ENCODING)
    ctl.add('base', [], instance)
    ctl.ground([('base', [])])
    solve_handle = ctl.solve(yield_=True)
    assert isinstance(solve_handle, clingo.SolveHandle)
    model = None
    for model in solve_handle:
        pass
    if model is None:
        logging.error('The problem does not have an optimal solution.')
        return -1, [], -1, -1
    order = interpret_clingo(model.symbols(shown=True))
    assert len(order) == len(products)

    rules = int(ctl.statistics['problem']['lp']['rules'])
    opt_value = int(ctl.statistics['summary']['costs'][0])
    models = int(ctl.statistics['summary']['models']['enumerated'])

    return opt_value, order, rules, models
