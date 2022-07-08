"""Approach for solving the Product Ordering approach:
Formulation of the problem instance as an Integer Linear Program
"""
from typing import *
from itertools import chain, combinations, permutations
import logging
import os
import sys
import pandas as pd
from docplex.mp.model import Model
from docplex.mp.dvar import Var
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import CHANGEOVER_MATRIX, CAMPAIGNS_ORDER, PRODUCT_PROPERTIES, \
    PROJECT_FOLDER, TIMEOUT, INF
sys.path.append(PROJECT_FOLDER)
from src.experiment.utils import calculate_oct

LOGGER = logging.getLogger('experiment')

def create_model(products : Set[str]) -> Tuple[Model, Dict[str, Dict[str, Var]]]:
    """Creating an ILP model of the Product Ordering problem for a Google OR-Tools LP solver

    Args:
        products (Set[str]): set of products

    Returns:
        Tuple[Model, Dict[str, Dict[str, Var]]]: DOcplex model and dictionary of all variables
    """
    df_matrix = pd.read_csv(CHANGEOVER_MATRIX, dtype={'Product': str}).set_index('Product')
    df_properties = pd.read_csv(PRODUCT_PROPERTIES, dtype={'Product': str}).set_index('Product')
    numCampaigns = len(set([df_properties.at[product, 'Campaign'] for product in products]))
    df_order = pd.read_csv(CAMPAIGNS_ORDER, index_col='Campaign')
    campaigns_order = df_order['Order'].to_dict()

    model = Model('product-ordering')

    delta_plus : Dict[str, List[Var]] = {'v': []}
    delta_minus : Dict[str, List[Var]] = {'v': []}
    for product in products:
        delta_plus[product] = []
        delta_minus[product] = []

    variables : Dict[str, Dict[str, Var]] = {'v': {}}
    campaigns_switch : Dict[str, Dict[str, int]] = {'v': {}}
    for product1 in products:
        var_v_product1 = model.binary_var(f'x_v_{product1}')
        variables['v'][product1] = var_v_product1
        delta_plus['v'].append(var_v_product1)
        delta_minus[product1].append(var_v_product1)
        campaigns_switch['v'] = {product1: 0}
        var_product1_v = model.binary_var(f'x_{product1}_v')
        variables[product1] = {'v': var_product1_v}
        delta_minus['v'].append(var_product1_v)
        delta_plus[product1].append(var_product1_v)
        campaigns_switch[product1] = {'v': 0}
        campaign1 = df_properties.at[product1, 'Campaign']
        for product2 in products:
            distance = df_matrix.at[product1, product2]
            if distance < INF:
                var = model.binary_var(f'x_{product1}_{product2}')
                variables[product1][product2] = var
                delta_plus[product1].append(var)
                delta_minus[product2].append(var)
                campaign2 = df_properties.at[product2, 'Campaign']
                if campaign1 == campaign2:
                    campaigns_switch[product1][product2] = 0
                else:
                    campaigns_switch[product1][product2] = 1

    for product in list(products) + ['v']:
        linear_expr = model.linear_expr()
        for var in delta_plus[product]:
            linear_expr.add_term(var, 1)
        model.add_constraint(linear_expr == 1, f'sum_outgoing_{product}')

    for product in list(products) + ['v']:
        linear_expr = model.linear_expr()
        for var in delta_minus[product]:
            linear_expr.add_term(var, 1)
        model.add_constraint(linear_expr == 1, f'sum_ingoing_{product}')

    for subset in chain.from_iterable(combinations(list(products) + ['v'], r) \
        for r in range(2, len(products) + 1)):
        linear_expr = model.linear_expr()
        for combination in combinations(list(subset), 2):
            for permutation in permutations(combination):
                product1, product2 = permutation
                if product2 in variables[product1]:
                    linear_expr.add_term(variables[product1][product2], 1)
        model.add_constraint(0 <= linear_expr, f'subtour_elimination_ge_{subset}')
        model.add_constraint(linear_expr <= len(subset) - 1, f'subtour_elimination_le_{subset}')

    for product1 in variables:
        if product1 != 'v':
            campaigns_order1 = campaigns_order[df_properties.at[product1, 'Campaign']]
            for product2 in variables[product1]:
                if product2 != 'v':
                    linear_expr = model.linear_expr()
                    campaigns_order2 = campaigns_order[df_properties.at[product2, 'Campaign']]
                    coeff = campaigns_order2 - campaigns_order1
                    linear_expr.add_term(variables[product1][product2], coeff)
                    model.add_constraint(0 <= linear_expr, f'campaigns_order_{product1}_{product2}')

    linear_expr = model.linear_expr()
    for product1 in variables:
        if product1 != 'v':
            for product2 in variables[product1]:
                if product2 != 'v':
                    coeff = campaigns_switch[product1][product2]
                    linear_expr.add_term(variables[product1][product2], coeff)
    model.add_constraint(linear_expr == numCampaigns - 1, f'campaigns_switch')

    linear_expr = model.linear_expr()
    for product1 in variables:
        for product2 in variables[product1]:
            if product1 == 'v' or product2 == 'v':
                distance = 0
            else:
                distance = df_matrix.at[product1, product2]
            linear_expr.add_term(variables[product1][product2], float(distance))
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
    counter = 0
    while cur_product != 'v' and counter < 10000:
        for product, var in variables[cur_product].items():
            value = var.solution_value
            assert value in [0, 1]
            if value == 1:
                cur_product = product
                order.append(product)
        counter += 1
    if counter == 10000:
        LOGGER.error('Infinite loop in extracting of order')

    assert len(order) > 0
    order = order[:-1]

    return order

def run_ilp(products : Set[str]) -> Tuple[List[str], int, int, bool]:
    """Computing the Product Ordering problem as an ILP using the Python API of CPLEX

    Args:
        products (Set[str]): set of products

    Returns:
        Tuple[List[str], int, int, bool]: minimal overall changeover time, optimal product order, \
            number of variables, number of constraints, flag for timeout occurred
    """
    model, variables = create_model(products)

    model.set_time_limit(TIMEOUT)
    solve_solution = model.solve()
    LOGGER.debug('Solution status: %s', solve_solution)

    if solve_solution is None:
        LOGGER.info('The problem does not have an optimal solution or the time limit is exceeded.')
        return [], -1, -1, True

    order = extract_order(variables)

    opt_value = solve_solution.get_objective_value()
    assert opt_value == calculate_oct(order)
    LOGGER.debug('Objective value = %s', str(opt_value))

    num_variables = model.number_of_variables
    num_constraints = model.number_of_constraints

    return order, num_variables, num_constraints, False
