import pandas as pd
import os
import logging
from ortools.linear_solver import pywraplp
from itertools import chain, combinations, permutations
from typing import Set, List, Dict, Tuple
import sys
sys.path.append(os.path.abspath('..'))
from constants import CHANGEOVER_MATRIX, TIMEOUT

def create_model(products : Set[str], start : str, end : str) -> Tuple[pywraplp.Solver, Dict[str, Dict[str, pywraplp.Variable]]]:
    """Creating an ILP model of the Product Ordering problem for a Google OR-Tools LP solver

    Args:
        products (Set[str]): set of products
        start (str): start product
        end (str): end product

    Returns:
        Tuple[pywraplp.Solver, Dict[str, Dict[str, pywraplp.Variable]]]: Google OR-Tools LP solver and dictionary of all variables
    """
    df = pd.read_csv(CHANGEOVER_MATRIX, index_col=0)

    cost = {}
    for product1 in products:
        cost[product1] = {}
        for product2 in products:
            if product1 != product2:
                value = float(df[product2][int(product1)])
                cost[product1][product2] = value

    solver = pywraplp.Solver.CreateSolver('SCIP')

    delta_plus = {}
    delta_minus = {}
    for product in products:
        delta_plus[product] = []
        delta_minus[product] = []
    
    x = {}
    for p1 in products:
        x[p1] = {}
        for p2 in products:
            if p1 != p2:
                var = solver.BoolVar(f'x_{p1}_{p2}')
                x[p1][p2] = var
                delta_plus[p1].append(var)
                delta_minus[p2].append(var)

    for product in products:
        if product != end:
            constraint = solver.RowConstraint(1, 1, f'flow_conservation_plus_{product}')
            for var in delta_plus[product]:
                constraint.SetCoefficient(var, 1)
    constraint = solver.RowConstraint(0, 0, f'flow_conservation_plus_end_{product}')
    for var in delta_plus[end]:
        constraint.SetCoefficient(var, 1)
        
    for product in products:
        if product != start:
            constraint = solver.RowConstraint(1, 1, f'flow_conservation_minus_{product}')
            for var in delta_minus[product]:
                constraint.SetCoefficient(var, 1)
    constraint = solver.RowConstraint(0, 0, f'flow_conservation_minus_start_{product}')
    for var in delta_minus[start]:
        constraint.SetCoefficient(var, 1)

    for s in chain.from_iterable(combinations(list(products), r) for r in range(2, len(products))):
        constraint = solver.RowConstraint(0, len(s) - 1, '')
        for c in combinations(list(s), 2):
            for p in permutations(c):
                p1, p2 = p
                constraint.SetCoefficient(x[p1][p2], 1)

    objective = solver.Objective()
    for p1 in products:
        for p2 in products:
            if p1 != p2:
                objective.SetCoefficient(x[p1][p2], cost[p1][p2])
    objective.SetMinimization()

    return solver, x

def _print_variables(x : Dict[str, Dict[str, pywraplp.Variable]]) -> None:
    """Auxiliary function for logging all variables of the ILP model

    Args:
        x (Dict[str, Dict[str, pywraplp.Variable]]): dictionary of all variables
    """
    for p1, values in x.items():
        for p2, var in values.items():
            logging.debug(f'x[{p1}][{p2}] = {var.SolutionValue()}')

def extract_order(x : Dict[str, Dict[str, pywraplp.Variable]], start : str, end : str) -> List[str]:
    """Analyzing the solution values of the ILP model's variables for extracting the order of products

    Args:
        x (Dict[str, Dict[str, pywraplp.Variable]]): dictionary of all variables
        start (str): start product
        end (str): end product

    Returns:
        List[str]: extracted order of products
    """
    logging.debug(f'start = {start}')
    logging.debug(f'end = {end}')
    _print_variables(x)
    
    order = [start]
    cur_product = start
    while cur_product != end:
        for product, var in x[cur_product].items():
            value = var.solution_value()
            assert value in [0, 1]
            if value == 1:
                cur_product = product
                order.append(product)

    return order

def run_ilp(products : Set[str]) -> Tuple[int, List[str], int, int]:
    """Computing the Product Ordering problem as an ILP using Google OR-Tools

    Args:
        products (Set[str]): set of products

    Returns:
        Tuple[int, List[str], int, int]: minimal overall changeover time, optimal product order, number of variables, number of constraints
    """
    minOptValue : int = 10080
    minOrder : List[str] = []
    numVariables : int = 0
    numConstraints : int = 0
    for p1 in products:
        for p2 in products:
            if p1 != p2:
                solver, x = create_model(products, start=p1, end=p2)
                solver.parameters.max_time_in_seconds = TIMEOUT

                status = solver.Solve()

                logging.debug(f'Solution for start {p1} and end {p2} with status {status}')
                if status == pywraplp.Solver.OPTIMAL:
                    optValue = solver.Objective().Value()
                    logging.debug('Objective value = ' + str(optValue))

                    numVariables += solver.NumVariables()
                    numConstraints += solver.NumConstraints()

                    if optValue < minOptValue:
                        minOptValue = optValue
                        minOrder = extract_order(x, start=p1, end=p2)
                        logging.debug('MinOrder: ' + str(minOrder))
                else:
                    logging.error('The problem does not have an optimal solution.')
                    return -1, [], -1, -1

    return minOptValue, minOrder, numVariables, numConstraints
