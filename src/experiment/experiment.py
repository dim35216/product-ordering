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
from typing import Set
import logging
import math
import random
import time
import os
import sys
from joblib import Parallel, delayed
import pandas as pd
from approaches.tsp import run_tsp_encoding
from approaches.concorde import run_concorde
from approaches.asp import run_asp
from approaches.bad import run_bad_encoding
from approaches.seq import run_seq_encoding
from approaches.ilp import run_ilp
from utils import setup_logger, calculate_oct
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from constants.constants import CHANGEOVER_MATRIX, PROJECT_FOLDER, RESULTS_FILE

LOGGER = logging.getLogger('experiment')

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

def run_experiment(sample_size : int, run : int, encoding : str) -> None:
    """Run an experiment instance for the given input, which is independent from the other
    instances and can be runned in parallel. The result of the experiment is then just appended
    to the results file

    Args:
        sample_size (int): number of products
        run (int): id of run
        encoding (str): encoding
    """
    setup_logger()

    LOGGER.info('run_experiment(%s, %s, %s) started', sample_size, run, encoding)
    products = select_random_set_of_product(sample_size, run)
    LOGGER.debug('product samples: %s', str(products))

    result = {'Time': math.nan, 'OptValue': math.nan, 'C': math.nan, 'GroundRules': math.nan,
              'Models': math.nan, 'Variables': math.nan, 'Constraints': math.nan}

    if encoding == 'tsp':
        temp = time.time()
        opt_value, order, rules, models = run_tsp_encoding(products, run)
        temp = time.time() - temp
        result['Time'] = temp
        result['OptValue'] = opt_value
        result['C'] = calculate_oct(order)
        result['GroundRules'] = rules
        result['Models'] = models

    if encoding == 'concorde':
        temp = time.time()
        order = run_concorde(products, run)
        temp = time.time() - temp
        result['Time'] = temp
        result['C'] = calculate_oct(order)

    if encoding == 'asp':
        temp = time.time()
        opt_value, order, rules, models = run_asp(products, run)
        temp = time.time() - temp
        result['Time'] = temp
        result['OptValue'] = opt_value
        result['C'] = calculate_oct(order)
        result['GroundRules'] = rules
        result['Models'] = models

    if encoding == 'bad':
        temp = time.time()
        opt_value, order, rules, models = run_bad_encoding(products, run)
        temp = time.time() - temp
        result['Time'] = temp
        result['OptValue'] = opt_value
        result['C'] = calculate_oct(order)
        result['GroundRules'] = rules
        result['Models'] = models

    if encoding == 'seq':
        temp = time.time()
        order, rules, models = run_seq_encoding(products, run)
        temp = time.time() - temp
        result['Time'] = temp
        result['C'] = calculate_oct(order)
        result['GroundRules'] = rules
        result['Models'] = models

    if encoding == 'ilp':
        temp = time.time()
        order, num_variables, num_constraints = run_ilp(products)
        temp = time.time() - temp
        result['Time'] = temp
        result['C'] = calculate_oct(order)
        result['Variables'] = num_variables
        result['Constraints'] = num_constraints

    with open(RESULTS_FILE, 'a', encoding='utf-8') as filehandle:
        filehandle.write(f'{sample_size},{run},{encoding},{result["Time"]},' + \
            f'{result["OptValue"]},{result["C"]},{result["GroundRules"]},'+ \
            f'{result["Variables"]},{result["Constraints"]}\n')
    
    LOGGER.info('run_experiment(%s, %s, %s) ended', sample_size, run, encoding)

if __name__ == '__main__':
    setup_logger()

    # List of encodings
    encodings = [
        # 'tsp',
        'concorde',
        # 'asp',
        # 'bad',
        # 'seq',
        # 'ilp'
    ]

    # Make and clean instances folders
    instances_folder = os.path.join(PROJECT_FOLDER, 'experiments', 'instances')
    if not os.path.isdir(instances_folder):
        os.mkdir(instances_folder)
    for encoding in encodings:
        folder = os.path.join(instances_folder, encoding)
        if not os.path.isdir(folder):
            os.mkdir(folder)
        else:
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))

    numProducts = [2] # list(range(6, 10, 2)) # [4, 8, 12, 16, 20, 24]
    runs = list(range(1))

    Parallel(n_jobs = -1)(delayed(run_experiment)(n, run, encoding) \
        for n in numProducts \
        for run in runs \
        for encoding in encodings \
    )
