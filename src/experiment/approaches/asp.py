import subprocess
import re
import os
import logging
from typing import Set, List, Tuple
import pandas as pd
import sys
sys.path.append(os.path.abspath('..'))
from constants import CHANGEOVER_MATRIX, DOMAIN_PDDL, PROJECT_FOLDER, TIMEOUT
sys.path.append(os.path.abspath(PROJECT_FOLDER))
from src.translator.translator import Translator

def create_instance(products : Set[str], filename : str) -> None:
    """Modelling an Product Ordering problem instance as a classical planning problem with
    preferences with the help of PDDL

    Args:
        products (Set[str]): set of products
        filename (str): name of resulting PDDL instance file
    """
    df_matrix = pd.read_csv(CHANGEOVER_MATRIX, index_col=0)

    result = \
f'''(define (problem ProductOrdering-{filename})
    (:domain ProductOrdering)

(:objects'''
    for product in products:
        result += f'\n    p{product}'
    result += \
''' - product
)

(:goal
    (and
        (complete)
'''
    for product in products:
        result += f'        (worked-off p{product})\n'
    result += \
'''    )
)

(:init
'''
    for product in products:
        result += f'    (available p{product})\n'
    for product1 in products:
        for product2 in products:
            value = df_matrix[product2][int(product1)]
            result += f'    (= (changeover-time p{product1} p{product2}) {value})\n'
    result += \
''')

(:metric minimize (+ (overall-changeover-time)))

)
'''

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(result)
    return

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
    
    opt_value = None
    p_start = None
    p_end = None
    order = [None] * (timesteps - 1)
    for line in cmd_output.split('\n'):
        result_initialize = pattern_initialize.match(line)
        result_switch = pattern_switch.match(line)
        result_finalize = pattern_finalize.match(line)
        result_opt = pattern_opt.match(line)
        
        if result_initialize:
            p_start = result_initialize.group(1)
            t = int(result_initialize.group(2))
            assert t == 1
        
        if result_switch:
            p1 = result_switch.group(1)
            p2 = result_switch.group(2)
            t = int(result_switch.group(3))
            order[t - 2] = p1
            order[t - 1] = p2

        if result_finalize:
            p_end = result_finalize.group(1)
            t = int(result_finalize.group(2))
            assert t == timesteps

        if result_opt:
            opt_value = result_opt.group(1)

    assert opt_value is not None
    assert None not in order
    assert p_start == order[0]
    assert p_end == order[-1]

    return opt_value, order

def run_asp(products : Set[str], run : int) -> Tuple[int, List[int], int]:
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
    create_instance(products, pddl_filename)
    assert os.path.exists(pddl_filename)
    assert os.path.exists(DOMAIN_PDDL)

    timesteps = len(products) + 1

    logging.debug('pddl_filename: %s', pddl_filename)
    translator = Translator()
    Pi = translator.translate(domain=DOMAIN_PDDL, problem=pddl_filename, timesteps=timesteps)
    assert Pi is not None
    with open(lp_filename, 'w') as f:
        f.write(Pi)

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
