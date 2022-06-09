"""Answer Set Planning approach for solving the Product Ordering approach:
Modelling as PDDL instance and translating it into a logic program
"""
from typing import Dict, Sequence, Set, List, Tuple, Union, Any
import logging
import time
import re
import os
import sys
import clingo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import DOMAIN_PDDL, PROJECT_FOLDER, INSTANCES_FOLDER, TIMEOUT
sys.path.append(os.path.abspath(PROJECT_FOLDER))
from src.experiment.utils import build_graph, ModelHelper
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
    end : Union[str, None] = None) -> Tuple[int, List[str], Dict[str, Any], bool]:
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
        Tuple[int, List[str], Dict[str, Any], bool]: minimal overall changeover time, optimal \
            product order, dictionary of clingo statistics, flag for timeout occurred
    """
    pddl_filename = os.path.join(INSTANCES_FOLDER, 'pddl', f'instance_{len(products)}_{run}.pddl')
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

    order = interpret_clingo(modelHelper.symbols, timesteps)
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
