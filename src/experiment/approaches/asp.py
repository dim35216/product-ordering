"""Answer Set Planning approach for solving the Product Ordering approach:
Modelling as PDDL instance and translating it into a logic program
"""
import subprocess
import re
import os
import logging
from typing import Set, List, Tuple
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import DOMAIN_PDDL, PROJECT_FOLDER, TIMEOUT
sys.path.append(os.path.abspath(PROJECT_FOLDER))
from src.pddl.modeler.modeler import Modeler
from src.pddl.translator.translator import Translator

def interpret_clingo(cmd_output : str, timesteps : int) -> Tuple[int, List[str]]:
    """Parsing the command line output of the answer set solver clingo for extracting the
    resulting order of products for the Answer Set Planning encoding

    Args:
        cmd_output (str): command line output of clingo
        timesteps (int): number of timesteps in the planning problem

    Returns:
        Tuple[int, List[str]]: minimal overall changeover time, optimal product order
    """
    pattern_initialize = re.compile(r'occ\(initialize\(p(\d*)\),(\d*)\)')
    pattern_switch = re.compile(r'occ\(switch\(p(\d*),p(\d*)\),(\d*)\)')
    pattern_finalize = re.compile(r'occ\(finalize\(p(\d*)\),(\d*)\)')
    pattern_opt = re.compile(r'Optimization: (\d*)')

    opt_value = -1
    p_start = None
    p_end = None
    order = [''] * (timesteps - 1)
    for line in cmd_output.split('\n'):
        result_initialize = pattern_initialize.match(line)
        result_switch = pattern_switch.match(line)
        result_finalize = pattern_finalize.match(line)
        result_opt = pattern_opt.match(line)

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

        if result_opt:
            opt_value = int(result_opt.group(1))

    assert opt_value != -1
    assert '' not in order
    assert p_start == order[0]
    assert p_end == order[-1]

    return opt_value, order

def run_asp(products : Set[str], run : int) -> Tuple[int, List[str], int]:
    """Computing the Product Ordering problem as a logic program using the Answer Set Planning
    approach; first, the problem is understood as a classical planning problem with preferences
    and this is encoded in the planning problem description language PDDL; the PDDL instance is
    translated into a logic program, which is solved by an answer set solver; the used PDDL to LP
    translator is implemented within this project as well

    Args:
        products (Set[str]): set of products
        run (int): id of run

    Returns:
        Tuple[int, List[int], int]: minimal overall changeover time, optimal product order, number of ground rules
    """
    pddl_filename = os.path.join(PROJECT_FOLDER, 'experiments', 'instances', 'asp',
        f'instance_{len(products)}_{run}.pddl')
    lp_filename = f'{pddl_filename}.lp'

    modeler = Modeler()
    modeler.create_instance(products, pddl_filename)
    assert os.path.exists(pddl_filename)
    assert os.path.exists(DOMAIN_PDDL)

    timesteps = len(products) + 1

    logging.debug('pddl_filename: %s', pddl_filename)
    translator = Translator()
    logic_program = translator.translate(domain=DOMAIN_PDDL, problem=pddl_filename,
                                         timesteps=timesteps)
    assert logic_program is not None
    with open(lp_filename, 'w') as filehandle:
        filehandle.write(logic_program)

    try:
        args = ['clingo', lp_filename, '--quiet=1,0', '--out-ifs=\n']
        process = subprocess.run(args, capture_output=True, text=True, check=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return -1, [], -1

    opt_value, order = interpret_clingo(process.stdout, timesteps)
    assert len(order) == len(products)

    try:
        args=['gringo', lp_filename, '--text']
        lines = subprocess.run(args, capture_output=True, check=True).stdout.count(b'\n')
    except subprocess.TimeoutExpired:
        lines = -1

    return opt_value, order, lines
