"""Approach for solving the Product Ordering approach:
Formulation of the problem instance as an Integer Linear Program
"""
from typing import Set, List, Dict, Tuple
from itertools import chain, combinations, permutations
import logging
import os
import sys
from ortools.linear_solver import pywraplp
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import PROJECT_FOLDER
sys.path.append(PROJECT_FOLDER)
from src.experiment.utils import calculate_oct, build_graph

LOGGER = logging.getLogger('experiment')

def create_model(edge_weights : Dict[str, Dict[str, int]]) -> Tuple[pywraplp.Solver, \
    Dict[str, Dict[str, pywraplp.Variable]]]:
    """Creating an ILP model of the Product Ordering problem for a Google OR-Tools LP solver

    Args:
        edge_weights (Dict[str, Dict[str, int]]): model of graph of problem instance

    Returns:
        Tuple[pywraplp.Solver, Dict[str, Dict[str, pywraplp.Variable]]]: Google OR-Tools LP \
            solver and dictionary of all variables
    """
    solver = pywraplp.Solver.CreateSolver('SCIP')

    delta_plus : Dict[str, List[pywraplp.Variable]] = {}
    delta_minus : Dict[str, List[pywraplp.Variable]] = {}
    for product in edge_weights:
        delta_plus[product] = []
        delta_minus[product] = []

    variables : Dict[str, Dict[str, pywraplp.Variable]] = {}
    for product1 in edge_weights:
        variables[product1] = {}
        for product2 in edge_weights[product1]:
            var = solver.BoolVar(f'x_{product1}_{product2}')
            variables[product1][product2] = var
            delta_plus[product1].append(var)
            delta_minus[product2].append(var)

    for product in edge_weights:
        constraint = solver.RowConstraint(1, 1, f'sum_outgoing_{product}')
        for var in delta_plus[product]:
            constraint.SetCoefficient(var, 1)

    for product in edge_weights:
        constraint = solver.RowConstraint(1, 1, f'sum_ingoing_{product}')
        for var in delta_minus[product]:
            constraint.SetCoefficient(var, 1)

    for subset in chain.from_iterable(combinations(list(edge_weights.keys()), r) \
        for r in range(2, len(edge_weights.keys()))):
        constraint = solver.RowConstraint(0, len(subset) - 1, '')
        for combination in combinations(list(subset), 2):
            for permutation in permutations(combination):
                product1, product2 = permutation
                if product2 in variables[product1]:
                    constraint.SetCoefficient(variables[product1][product2], 1)

    objective = solver.Objective()
    for product1 in edge_weights:
        for product2 in edge_weights[product1]:
            objective.SetCoefficient(variables[product1][product2], \
                float(edge_weights[product1][product2]))
    objective.SetMinimization()

    return solver, variables

def _print_variables(variables : Dict[str, Dict[str, pywraplp.Variable]]) -> None:
    """Auxiliary function for logging all variables of the ILP model

    Args:
        variables (Dict[str, Dict[str, pywraplp.Variable]]): dictionary of all variables
    """
    for product1, values in variables.items():
        for product2, var in values.items():
            LOGGER.debug('x[%s][%s] = %s', product1, product2, var.SolutionValue())

def extract_order(variables : Dict[str, Dict[str, pywraplp.Variable]]) -> List[str]:
    """Analyzing the solution values of the ILP model's variables for extracting the order of
    products

    Args:
        variables (Dict[str, Dict[str, pywraplp.Variable]]): dictionary of all variables

    Returns:
        List[str]: extracted order of products
    """
    _print_variables(variables)

    order = []
    cur_product = 'v'
    for product, var in variables[cur_product].items():
        value = var.solution_value()
        assert value in [0, 1]
        if value == 1:
            cur_product = product
            order.append(product)
    while cur_product != 'v':
        for product, var in variables[cur_product].items():
            value = var.solution_value()
            assert value in [0, 1]
            if value == 1:
                cur_product = product
                order.append(product)

    assert len(order) > 0
    order = order[:-1]

    return order

def run_ilp(products : Set[str]) -> Tuple[List[str], int, int]:
    """Computing the Product Ordering problem as an ILP using Google OR-Tools

    Args:
        products (Set[str]): set of products

    Returns:
        Tuple[List[str], int, int]: minimal overall changeover time, optimal product order, \
            number of variables, number of constraints
    """
    edge_weights = build_graph(products, cyclic=True)
    solver, variables = create_model(edge_weights)

    status = solver.Solve()
    LOGGER.debug('Solution status: %s', status)

    if status != pywraplp.Solver.OPTIMAL:
        LOGGER.info('The problem does not have an optimal solution.')
        return [], -1, -1

    order = extract_order(variables)

    opt_value = solver.Objective().Value()
    assert opt_value == calculate_oct(order)
    LOGGER.debug('Objective value = %s', str(opt_value))

    num_variables = solver.NumVariables()
    num_constraints = solver.NumConstraints()

    return order, num_variables, num_constraints
