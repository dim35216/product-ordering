"""Answer Set Planning approach for solving the Product Ordering approach:
Modelling as PDDL instance and translating it into a logic program
"""
from typing import Sequence, Set, List, Tuple, Union
import logging
import re
import os
import sys
import clingo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import DOMAIN_PDDL, PROJECT_FOLDER
sys.path.append(os.path.abspath(PROJECT_FOLDER))
from src.experiment.utils import build_graph
from src.pddl.modeler.modeler import Modeler
from src.pddl.translator.translator import Translator

LOGGER = logging.getLogger('experiment')

def interpret_clingo(symbols : Sequence[clingo.Symbol], timesteps : int) -> List[str]:
    """Parsing the command line output of the answer set solver clingo for extracting the
    resulting order of products for the Answer Set Planning encoding

    Args:
        symbols (Sequence[clingo.Symbol]): set of symbols outputted by clingo
        timesteps (int): number of timesteps in the planning problem

    Returns:
        List[str]: optimal product order
    """
    pattern_initialize = re.compile(r'occ\(initialize\(p(\w*)\),(\d*)\)')
    pattern_switch = re.compile(r'occ\(switch\(p(\w*),p(\w*)\),(\d*)\)')
    pattern_finalize = re.compile(r'occ\(finalize\(p(\w*)\),(\d*)\)')

    p_start = None
    p_end = None
    order = [''] * (timesteps - 1)
    for symbol in symbols:
        atom = str(symbol)
        result_initialize = pattern_initialize.match(atom)
        result_switch = pattern_switch.match(atom)
        result_finalize = pattern_finalize.match(atom)

        if result_initialize:
            p_start = result_initialize.group(1)
            time = int(result_initialize.group(2))
            assert time == 1

        if result_switch:
            product1 = result_switch.group(1)
            product2 = result_switch.group(2)
            time = int(result_switch.group(3))
            order[time - 2] = product1
            order[time - 1] = product2

        if result_finalize:
            p_end = result_finalize.group(1)
            time = int(result_finalize.group(2))
            assert time == timesteps

    assert '' not in order
    assert order[0] == p_start
    assert order[0] == 'start'
    assert order[-1] == p_end
    assert order[-1] == 'end'
    order = order[1:-1]

    return order

def run_asp(products : Set[str], run : int, start : Union[str, None] = None, \
    end : Union[str, None] = None) -> Tuple[int, List[str], int, int]:
    """Computing the Product Ordering problem as a logic program using the Answer Set Planning
    approach; first, the problem is understood as a classical planning problem with preferences
    and this is encoded in the planning problem description language PDDL; the PDDL instance is
    translated into a logic program, which is solved by an answer set solver; the used PDDL to LP
    translator is implemented within this project as well

    Args:
        products (Set[str]): set of products
        run (int): id of run
        start (Union[str, None], optional): start product. Defaults to None.
        end (Union[str, None], optional): end product. Defaults to None.

    Returns:
        Tuple[int, List[str], int, int]: minimal overall changeover time, optimal product order, \
            number of ground rules, number of calculated models
    """
    pddl_filename = os.path.join(PROJECT_FOLDER, 'experiments', 'instances', 'asp',
        f'instance_{len(products)}_{run}.pddl')
    LOGGER.debug('pddl_filename: %s', pddl_filename)
    lp_filename = f'{pddl_filename}.lp'

    edge_weights = build_graph(products, start, end)

    modeler = Modeler()
    modeler.create_instance(edge_weights, pddl_filename)
    assert os.path.exists(pddl_filename)
    assert os.path.exists(DOMAIN_PDDL)

    timesteps = len(products) + 3

    translator = Translator()
    logic_program = translator.translate(domain=DOMAIN_PDDL, problem=pddl_filename,
                                         timesteps=timesteps)
    assert logic_program is not None

    with open(lp_filename, 'w') as filehandle:
        filehandle.write(logic_program)

    ctl = clingo.Control()
    ctl.add('base', [], logic_program)
    ctl.ground([('base', [])])
    solve_handle = ctl.solve(yield_=True)
    assert isinstance(solve_handle, clingo.SolveHandle)
    model = None
    for model in solve_handle:
        pass
    if model is None:
        LOGGER.info('The problem does not have an optimal solution.')
        return -1, [], -1, -1
    order = interpret_clingo(model.symbols(shown=True), timesteps)
    assert len(order) == len(products)

    rules = int(ctl.statistics['problem']['lp']['rules'])
    opt_value = int(ctl.statistics['summary']['costs'][0])
    models = int(ctl.statistics['summary']['models']['enumerated'])

    return opt_value, order, rules, models
