"""Approach for solving the Product Ordering approach:
Modelling as PDDL instance and solving it with an optimizing PDDL solver
"""
from typing import Set, List, Union, Tuple
import logging
import subprocess
import re
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import DOMAIN_PDDL, FAST_DOWNWARD_EXE, PROJECT_FOLDER, INSTANCES_FOLDER, TIMEOUT
sys.path.append(PROJECT_FOLDER)
from src.experiment.utils import build_graph
from src.pddl.modeler.modeler import Modeler

LOGGER = logging.getLogger('experiment')

def interpret_sas_plan(filename : str) -> Tuple[int, List[str]]:
    pattern_initialize = re.compile(r'\(initialize p(\w*)\)')
    pattern_switch = re.compile(r'\(switch p(\w*) p(\w*)\)')
    pattern_finalize = re.compile(r'\(finalize p(\w*)\)')
    pattern_cost = re.compile(r'; cost = (\d*) \(general cost\)')
        
    with open(filename, 'r') as filehandle:
        lines = filehandle.readlines()

    assert len(lines) > 1
    lines = [line.rstrip() for line in lines]

    p_start = None
    p_end = None
    order = []
    opt_value = -1
    for line in lines:
        result_initialize = pattern_initialize.match(line)
        result_switch = pattern_switch.match(line)
        result_finalize = pattern_finalize.match(line)
        result_cost = pattern_cost.match(line)

        if result_initialize:
            p_start = result_initialize.group(1)
            order.append(p_start)

        if result_switch:
            product1 = result_switch.group(1)
            product2 = result_switch.group(2)
            assert order[-1] == product1
            order.append(product2)

        if result_finalize:
            p_end = result_finalize.group(1)
            assert order[-1] == p_end

        if result_cost:
            opt_value = int(result_cost.group(1))

    assert opt_value != -1

    if order[0] == 'start':
        order = order[1:]
    if order[-1] == 'end':
        order = order[:-1]

    return opt_value, order

def run_pddl_solver(products : Set[str], run : int, start : Union[str, None] = None, \
    end : Union[str, None] = None) -> Tuple[int, List[str], bool]:
    """Computing the Product Ordering problem with the help of an optimizing PDDL solver. This
    solver is named Delphi1 and is taken from the website of IPC2018. It extends the common Fast
    Downward planner such that it can handle action costs and is thus optimizing.

    Args:
        products (Set[str]): set of products
        run (int): id of run
        start (Union[str, None], optional): start product. Defaults to None.
        end (Union[str, None], optional): end product. Defaults to None.

    Returns:
        Tuple[int, List[str], bool]: objective value, optimal product order, flag for timeout \
            occurred
    """
    pddl_filename = os.path.join(INSTANCES_FOLDER, 'pddl', f'instance_{len(products)}_{run}.pddl')
    plan_filename = os.path.join(INSTANCES_FOLDER, 'pddl', f'instance_{len(products)}_{run}.plan')
    
    edge_weights = build_graph(products, start, end)

    modeler = Modeler()
    modeler.create_instance(edge_weights, pddl_filename)
    assert os.path.exists(pddl_filename)
    assert os.path.exists(DOMAIN_PDDL)

    try:
        args = [FAST_DOWNWARD_EXE, '--build release64dynamic', '--plan-file', plan_filename,
            DOMAIN_PDDL, pddl_filename, '--search "astar(lmcut())"']
        subprocess.run(args, capture_output=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        LOGGER.info('The time limit is exceeded.')
        return -1, [], True

    assert os.path.exists(plan_filename)
    opt_value, order = interpret_sas_plan(plan_filename)
    
    return opt_value, order, False
