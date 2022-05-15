import math
import time
import os
import random
import logging
from joblib import Parallel, delayed
from typing import Set
import pandas as pd
import sys
sys.path.append(os.path.abspath('.'))
from constants import CHANGEOVER_MATRIX, PROJECT_FOLDER, RESULTS_FILE
from approaches.tsp import run_tsp_encoding
from approaches.asp import run_asp
from approaches.seq import run_seq_encoding
from approaches.bad import run_bad_encoding
from approaches.ilp import run_ilp
from utils import calculate_oct

def select_random_set_of_product(n : int, run : int) -> Set[str]:
    """Auxiliary function for selecting a random set of n products out of all products in the
    changeover matrix; with the help of the run id, the random selection becomes reproducible,
    because with the help of the run id a seed for the selection is generated

    Args:
        n (int): number of products in sample
        run (int): id of run

    Returns:
        Set[str]: set of products
    """
    df_matrix = pd.read_csv(CHANGEOVER_MATRIX, index_col=0)
    products = df_matrix.columns.to_list()
    random.seed(42)
    seed = random.randint(run * 100 + 1, (run + 1) * 100)
    random.seed(seed)
    samples = set(random.sample(products, n))
    return samples

def run_experiment(n : int, run : int, encoding : str) -> None:
    """Run an experiment instance for the given input, which is independent from the other
    instances and can be runned in parallel. The result of the experiment is then just appended
    to the results file

    Args:
        n (int): number of products
        run (int): id of run
        encoding (str): encoding
    """
    print('run_experiment(%s, %s, %s)', n, run, encoding)
    products = select_random_set_of_product(n, run)
    print('product samples: %s', str(products))

    result = {'Time': math.nan, 'OptValue': math.nan, 'C': math.nan, 'GroundRules': math.nan,
              'Variables': math.nan, 'Constraints': math.nan}
    
    if encoding == 'tsp':
        t = time.time()
        opt_value, order, ground_rules = run_tsp_encoding(products, run)
        t = time.time() - t
        result['Time'] = t
        result['OptValue'] = opt_value
        result['C'] = calculate_oct(order)
        result['GroundRules'] = ground_rules

    if encoding == 'asp':
        t = time.time()
        opt_value, order, ground_rules = run_asp(products, run)
        t = time.time() - t
        result['Time'] = t
        result['OptValue'] = opt_value
        result['C'] = calculate_oct(order)
        result['GroundRules'] = ground_rules

    if encoding == 'seq':
        t = time.time()
        opt_value, order, ground_rules = run_seq_encoding(products, run)
        t = time.time() - t
        result['Time'] = t
        result['OptValue'] = opt_value
        result['GroundRules'] = ground_rules

    if encoding == 'bad':
        t = time.time()
        opt_value, order, ground_rules = run_bad_encoding(products, run)
        t = time.time() - t
        result['Time'] = t
        result['OptValue'] = opt_value
        result['GroundRules'] = ground_rules

    if encoding == 'ilp':
        t = time.time()
        opt_value, order, numVariables, numConstraints = run_ilp(products, run)
        t = time.time() - t
        result['Time'] = t
        result['OptValue'] = opt_value
        result['C'] = calculate_oct(order)
        result['Variables'] = numVariables
        result['Constraints'] = numConstraints

    with open(RESULTS_FILE, 'a', encoding='utf-8') as f:
        f.write(f'{n},{run},{encoding},{result["Time"]},{result["OptValue"]}, ' + \
            f'{result["C"]},{result["GroundRules"]},{result["Variables"]},' + \
            f'{result["Constraints"]}\n')

if __name__ == '__main__':
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
    logging.basicConfig(level=logging.INFO)

    encodings = [
        'tsp',
        'asp',
        'seq',
        'bad',
        'ilp'
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

    numProducts = list(range(10, 50, 4)) # [4, 8, 12, 16, 20, 24]
    runs = list(range(3))

    Parallel(n_jobs = -1)(delayed(run_experiment)(n, run, encoding) \
        for n in numProducts \
        for run in runs \
        for encoding in encodings \
    )
