"""Approach for solving the Product Ordering approach:
Formulation of the problem instance as an Integer Linear Program
"""
from typing import Set, List, Dict, Tuple
from itertools import chain, combinations, permutations
import logging
import os
import sys
from docplex.mp.model import Model
from docplex.mp.dvar import Var
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import PROJECT_FOLDER, TIMEOUT
sys.path.append(PROJECT_FOLDER)
from src.experiment.utils import calculate_oct, build_graph

LOGGER = logging.getLogger('experiment')

def create_model(edge_weights : Dict[str, Dict[str, int]]) -> Tuple[Model, \
    Dict[str, Dict[str, Var]]]:
    """Creating an ILP model of the Product Ordering problem for a Google OR-Tools LP solver

    Args:
        edge_weights (Dict[str, Dict[str, int]]): model of graph of problem instance

    Returns:
        Tuple[Model, Dict[str, Dict[str, Var]]]: DOcplex model and dictionary of all variables
    """
    model = Model('product-ordering')

    delta_plus : Dict[str, List[Var]] = {}
    delta_minus : Dict[str, List[Var]] = {}
    for product in edge_weights:
        delta_plus[product] = []
        delta_minus[product] = []

    variables : Dict[str, Dict[str, Var]] = {}
    for product1 in edge_weights:
        variables[product1] = {}
        for product2 in edge_weights[product1]:
            var = model.binary_var(f'x_{product1}_{product2}')
            variables[product1][product2] = var
            delta_plus[product1].append(var)
            delta_minus[product2].append(var)

    for product in edge_weights:
        linear_expr = model.linear_expr()
        for var in delta_plus[product]:
            linear_expr.add_term(var, 1)
        model.add_constraint(linear_expr == 1, f'sum_outgoing_{product}')

    for product in edge_weights:
        linear_expr = model.linear_expr()
        for var in delta_minus[product]:
            linear_expr.add_term(var, 1)
        model.add_constraint(linear_expr == 1, f'sum_ingoing_{product}')

    for subset in chain.from_iterable(combinations(list(edge_weights.keys()), r) \
        for r in range(2, len(edge_weights.keys()))):
        linear_expr = model.linear_expr()
        for combination in combinations(list(subset), 2):
            for permutation in permutations(combination):
                product1, product2 = permutation
                if product2 in variables[product1]:
                    linear_expr.add_term(variables[product1][product2], 1)
        model.add_constraint(0 <= linear_expr, f'subtour_elimination_ge_{subset}')
        model.add_constraint(linear_expr <= len(subset) - 1, f'subtour_elimination_le_{subset}')

    linear_expr = model.linear_expr()
    for product1 in edge_weights:
        for product2 in edge_weights[product1]:
            linear_expr.add_term(variables[product1][product2], \
                float(edge_weights[product1][product2]))
    model.minimize(linear_expr)

    return model, variables

def _print_variables(variables : Dict[str, Dict[str, Var]]) -> None:
    """Auxiliary function for logging all variables of the ILP model

    Args:
        variables (Dict[str, Dict[str, Var]]): dictionary of all variables
    """
    for product1, values in variables.items():
        for product2, var in values.items():
            LOGGER.debug('x[%s][%s] = %s', product1, product2, var.solution_value)

def extract_order(variables : Dict[str, Dict[str, Var]]) -> List[str]:
    """Analyzing the solution values of the ILP model's variables for extracting the order of
    products

    Args:
        variables (Dict[str, Dict[str, Var]]): dictionary of all variables

    Returns:
        List[str]: extracted order of products
    """
    _print_variables(variables)

    order = []
    cur_product = 'v'
    for product, var in variables[cur_product].items():
        value = var.solution_value
        assert value in [0, 1]
        if value == 1:
            cur_product = product
            order.append(product)
    while cur_product != 'v':
        for product, var in variables[cur_product].items():
            value = var.solution_value
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
    model, variables = create_model(edge_weights)

    model.set_time_limit(TIMEOUT)
    solve_solution = model.solve()
    LOGGER.debug('Solution status: %s', solve_solution)

    if solve_solution is None:
        LOGGER.info('The problem does not have an optimal solution ot the time limit is exceeded.')
        return [], -1, -1

    order = extract_order(variables)

    opt_value = solve_solution.get_objective_value()
    assert opt_value == calculate_oct(order)
    LOGGER.debug('Objective value = %s', str(opt_value))

    num_variables = model.number_of_variables
    num_constraints = model.number_of_constraints

    return order, num_variables, num_constraints
