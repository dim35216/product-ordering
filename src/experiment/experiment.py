"""Computational experiment for comparing different approaches for computing the Product
Ordering problem. These approaches are:
- Using the Answer Set Planning approach
- Transforming the Product Ordering problem instance into a TSP instance
    - Using the perfect TSP encoding
    - Using the bad TSP encoding
    - Using the perfect TSP encoding, but computing the problem sequentially for each
    combination of start and end product
- Using the ILP approach
"""
from typing import *
import logging
import math
import random
import time
import os
import sys
from joblib import Parallel, delayed
import pandas as pd
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from approaches.logic_program import run_clingo
from approaches.tsp_solver import run_concorde
from approaches.asp import run_asp
from approaches.ilp import run_ilp
from approaches.pddl_solver import run_fast_downward
from utils import setup_logger, calculate_oct
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from constants.constants import CHANGEOVER_MATRIX, INSTANCES_FOLDER, RESULTS_FILE

LOGGER = logging.getLogger('experiment')

# Dict of flags for timeouts occurred
timeouts : Dict[Union[None, int], Dict[str, Dict[int, bool]]] = {}

def select_random_set_of_product(sample_size : int, run : int) -> Set[str]:
    """Auxiliary function for selecting a random set of n products out of all products in the
    changeover matrix; with the help of the run id, the random selection becomes reproducible,
    because with the help of the run id a seed for the selection is generated

    Args:
        sample_size (int): number of products in sample
        run (int): id of run

    Returns:
        Set[str]: set of products
    """
    df_matrix = pd.read_csv(CHANGEOVER_MATRIX, dtype={'Product': str}).set_index('Product')
    products = list(df_matrix.index)
    random.seed(42)
    seed = random.randint(run * 100 + 1, (run + 1) * 100)
    random.seed(seed)
    samples = set(random.sample(products, sample_size))
    return samples

def run_experiment(sample_size : int, run : int, approach : str, \
    consider_constraints : Union[None, int] = None) -> None:
    """Run an experiment instance for the given input, which is independent from the other
    instances and can be runned in parallel. The result of the experiment is then just appended
    to the results file

    Args:
        sample_size (int): number of products
        run (int): id of run
        approach (str): solving approach
        consider_constraints (Union[None, int], optional): Indicating which constraints are taken \
            into account. For 0 no additional constraints are considered, for None all are \
            considered. Defaults to None.
    """
    setup_logger()

    LOGGER.info('run_experiment(%s, %s, %s, %s) started', sample_size, run, approach, \
        consider_constraints)
    products = select_random_set_of_product(sample_size, run)
    LOGGER.debug('product samples: %s', str(products))

    result : Dict[str, Any] = {
        'Time': math.nan,
        'OptValue': math.nan,
        'C': math.nan,
        'ClingoStats': {
            'Constraints': math.nan,
            'Complexity': math.nan,
            'Vars': math.nan,
            'Atoms': math.nan,
            'Bodies': math.nan,
            'Rules': math.nan,
            'Choices': math.nan,
            'Conflicts': math.nan,
            'Restarts': math.nan,
            'Models': math.nan
        },
        'Variables': math.nan,
        'Constraints': math.nan,
        'Order': [],
        'Timeout': False
    }

    if approach == 'lp_normal':
        temp = time.time()
        opt_value, order, stats, timeout = run_clingo(products, run, encoding='normal', \
            consider_constraints=consider_constraints)
        temp = time.time() - temp
        result['Time'] = temp
        result['OptValue'] = opt_value
        result['C'] = calculate_oct(order)
        if not timeout:
            result['ClingoStats'] = stats
        result['Order'] = order
        result['Timeout'] = timeout

    elif approach == 'lp_advanced':
        temp = time.time()
        opt_value, order, stats, timeout = run_clingo(products, run, encoding='advanced', \
            consider_constraints=consider_constraints)
        temp = time.time() - temp
        result['Time'] = temp
        result['OptValue'] = opt_value
        result['C'] = calculate_oct(order)
        if not timeout:
            result['ClingoStats'] = stats
        result['Order'] = order
        result['Timeout'] = timeout

    elif approach == 'tsp':
        temp = time.time()
        order, timeout = run_concorde(products, run, consider_constraints)
        temp = time.time() - temp
        result['Time'] = temp
        result['C'] = calculate_oct(order)
        result['Order'] = order
        result['Timeout'] = timeout

    elif approach == 'pddl':
        temp = time.time()
        opt_value, order, timeout = run_fast_downward(products, run)
        temp = time.time() - temp
        result['Time'] = temp
        result['OptValue'] = opt_value
        result['C'] = calculate_oct(order)
        result['Order'] = order
        result['Timeout'] = timeout

    elif approach == 'ilp':
        temp = time.time()
        order, num_variables, num_constraints, timeout = run_ilp(products, consider_constraints)
        temp = time.time() - temp
        result['Time'] = temp
        result['C'] = calculate_oct(order)
        result['Variables'] = num_variables
        result['Constraints'] = num_constraints
        result['Order'] = order
        result['Timeout'] = timeout

    elif approach == 'asp':
        temp = time.time()
        opt_value, order, stats, timeout = run_asp(products, run)
        temp = time.time() - temp
        result['Time'] = temp
        result['OptValue'] = opt_value
        result['C'] = calculate_oct(order)
        if not timeout:
            result['ClingoStats'] = stats
        result['Order'] = order
        result['Timeout'] = timeout

    else:
        LOGGER.info('Approach %s is unknown', approach)

    timeouts[consider_constraints][approach][sample_size] = \
        timeouts[consider_constraints][approach][sample_size] and result['Timeout']

    with open(RESULTS_FILE, 'a', encoding='utf-8') as filehandle:
        filehandle.write('{}\n'.format(
            ','.join([
                str(sample_size),
                str(run),
                approach,
                str(consider_constraints),
                str(result['Time']),
                str(result['OptValue']),
                str(result['C']),
                str(result['ClingoStats']['Constraints']),
                str(result['ClingoStats']['Complexity']),
                str(result['ClingoStats']['Vars']),
                str(result['ClingoStats']['Atoms']),
                str(result['ClingoStats']['Bodies']),
                str(result['ClingoStats']['Rules']),
                str(result['ClingoStats']['Choices']),
                str(result['ClingoStats']['Conflicts']),
                str(result['ClingoStats']['Restarts']),
                str(result['ClingoStats']['Models']),
                str(result['Variables']),
                str(result['Constraints']),
                str(' '.join(result['Order'])),
                str(result['Timeout'])
            ])
        ))

    LOGGER.info('run_experiment(%s, %s, %s, %s) ended', sample_size, run, approach, \
        consider_constraints)

if __name__ == '__main__':
    setup_logger()

    # List of approaches
    approaches = [
        # 'lp_normal',
        # 'lp_advanced',
        'tsp',
        # 'pddl',
        # 'ilp',
        # 'asp',
    ]

    # Make and clean instances folders
    subfolders = ['tsp', 'pddl', 'lp']
    if not os.path.isdir(INSTANCES_FOLDER):
        os.mkdir(INSTANCES_FOLDER)
    for subfolder in subfolders:
        folder = os.path.join(INSTANCES_FOLDER, subfolder)
        if not os.path.isdir(folder):
            os.mkdir(folder)
        else:
            for file in os.listdir(folder):
                if os.path.isdir(os.path.join(folder, file)):
                    for file2 in os.listdir(os.path.join(folder, file)):
                        os.remove(os.path.join(folder, file, file2))
                    os.rmdir(os.path.join(folder, file))
                else:
                    os.remove(os.path.join(folder, file))

    numProducts = [6] # list(range(6, 72, 1))
    runs = [0] # list(range(4))
    consider_constraints_options = [3] # [0, 1, 2, 3, 4]

    for consider_constraints in consider_constraints_options:
        timeouts[consider_constraints] = {}
        for approach in approaches:
            timeouts[consider_constraints][approach] = {}
            for n in numProducts:
                timeouts[consider_constraints][approach][n] = True
                Parallel(n_jobs=-1, require='sharedmem') \
                    (delayed(run_experiment)(n, run, approach, consider_constraints) \
                    for run in runs)
                if timeouts[consider_constraints][approach][n]:
                    LOGGER.info('All %d runs for approach %s and the considered constraints ' + \
                        'option %s exceeded the time limit; the sample size %d won\'t be ' + \
                        'increased anymore', len(runs), approach, consider_constraints, n)
                    break
