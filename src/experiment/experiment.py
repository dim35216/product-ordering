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
from typing import Set, Dict, Any
import logging
import math
import random
import time
import os
import sys
from joblib import Parallel, delayed
import pandas as pd
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from approaches.clingo import run_clingo
from approaches.concorde import run_concorde
from approaches.asp import run_asp
from approaches.ilp import run_ilp
from approaches.pddl import run_pddl_solver
from utils import setup_logger, calculate_oct
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from constants.constants import CHANGEOVER_MATRIX, PROJECT_FOLDER, RESULTS_FILE

LOGGER = logging.getLogger('experiment')

# Dict of flags for timeouts occurred
timeouts : Dict[str, Dict[int, bool]] = {}

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
    df_matrix = pd.read_csv(CHANGEOVER_MATRIX, index_col=0)
    products = df_matrix.columns.to_list()
    random.seed(42)
    seed = random.randint(run * 100 + 1, (run + 1) * 100)
    random.seed(seed)
    samples = set(random.sample(products, sample_size))
    return samples

def run_experiment(sample_size : int, run : int, approach : str) -> None:
    """Run an experiment instance for the given input, which is independent from the other
    instances and can be runned in parallel. The result of the experiment is then just appended
    to the results file

    Args:
        sample_size (int): number of products
        run (int): id of run
        approach (str): used solving approach
    """
    setup_logger()

    LOGGER.info('run_experiment(%s, %s, %s) started', sample_size, run, approach)
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
        'Timeout': False
    }

    if approach in ['clingo', 'clingo-bad']:
        encoding = 'perfect'
        if approach == 'clingo-bad':
            encoding = 'bad'
        temp = time.time()
        opt_value, order, stats, timeout = run_clingo(products, run, encoding=encoding)
        temp = time.time() - temp
        result['Time'] = temp
        result['OptValue'] = opt_value
        result['C'] = calculate_oct(order)
        result['ClingoStats'] = stats
        result['Timeout'] = timeout

    elif approach == 'concorde':
        temp = time.time()
        order, timeout = run_concorde(products, run)
        temp = time.time() - temp
        result['Time'] = temp
        result['C'] = calculate_oct(order)
        result['Timeout'] = timeout

    elif approach == 'asp':
        temp = time.time()
        opt_value, order, stats, timeout = run_asp(products, run)
        temp = time.time() - temp
        result['Time'] = temp
        result['OptValue'] = opt_value
        result['C'] = calculate_oct(order)
        result['ClingoStats'] = stats
        result['Timeout'] = timeout

    elif approach == 'ilp':
        temp = time.time()
        order, num_variables, num_constraints, timeout = run_ilp(products)
        temp = time.time() - temp
        result['Time'] = temp
        result['C'] = calculate_oct(order)
        result['Variables'] = num_variables
        result['Constraints'] = num_constraints
        result['Timeout'] = timeout

    elif approach == 'pddl':
        temp = time.time()
        opt_value, order, timeout = run_pddl_solver(products, run)
        temp = time.time() - temp
        result['Time'] = temp
        result['OptValue'] = opt_value
        result['C'] = calculate_oct(order)
        result['Timeout'] = timeout

    else:
        LOGGER.info('Approach %s is unknown', approach)

    timeouts[approach][sample_size] = timeouts[approach][sample_size] and result['Timeout']

    with open(RESULTS_FILE, 'a', encoding='utf-8') as filehandle:
        filehandle.write('{}\n'.format(
            ','.join([
                sample_size,
                run,
                approach,
                result['Time'],
                result['OptValue'],
                result['C'],
                result['ClingoStats']['Constraints'],
                result['ClingoStats']['Complexity'],
                result['ClingoStats']['Vars'],
                result['ClingoStats']['Atoms'],
                result['ClingoStats']['Bodies'],
                result['ClingoStats']['Rules'],
                result['ClingoStats']['Choices'],
                result['ClingoStats']['Conflicts'],
                result['ClingoStats']['Restarts'],
                result['ClingoStats']['Models'],
                result['Variables'],
                result['Constraints'],
                result['Timeout']
            ])
        ))
    
    LOGGER.info('run_experiment(%s, %s, %s) ended', sample_size, run, approach)

if __name__ == '__main__':
    setup_logger()

    # List of solving approaches
    approaches = [
        'concorde',
        'clingo',
        'clingo-bad',
        'pddl',
        'asp',
        'ilp'
    ]

    # Make and clean instances folders
    subfolders = ['tsp', 'pddl', 'lp']
    instances_folder = os.path.join(PROJECT_FOLDER, 'experiments', 'instances')
    if not os.path.isdir(instances_folder):
        os.mkdir(instances_folder)
    for subfolder in subfolders:
        folder = os.path.join(instances_folder, subfolder)
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

    numProducts = list(range(6, 72, 1))
    runs = list(range(4))

    for approach in approaches:
        timeouts[approach] = {}
        for n in numProducts:
            timeouts[approach][n] = True
            Parallel(n_jobs=-1, require='sharedmem')(delayed(run_experiment)(n, run, approach) \
                for run in runs)
            if timeouts[approach][n]:
                LOGGER.info('All %d runs for approach %s exceeded the time limit; the sample ' + \
                    'size %d won\'t be increased anymore', len(runs), approach, n)
                break
