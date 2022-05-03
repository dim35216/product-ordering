import time
import os
import random
import logging
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
    print('samples:', samples)
    return samples

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
        # 'asp',
        # 'seq',
        'bad',
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

    numProducts = list(range(10, 40, 4)) # [4, 8, 12, 16, 20, 24]
    runs = list(range(3))
    index = pd.MultiIndex.from_product([numProducts, runs, encodings],
        names=['NumProducts', 'Run', 'Encoding'])
    df_results = pd.DataFrame([], index=index,
        columns=['Time', 'OptValue', 'C', 'GroundRules', 'Variables', 'Constraints'])

    for n in numProducts:
        print('n:', n)
        for run in runs:
            print('--------')
            print('run:', run)
            products = select_random_set_of_product(n, run)

            if 'tsp' in encodings:
                print('tsp encoding')
                t = time.time()
                opt_value, order, ground_rules = run_tsp_encoding(products, run)
                t = time.time() - t
                df_results['Time'][(n, run, 'tsp')] = t
                df_results['OptValue'][(n, run, 'tsp')] = opt_value
                df_results['C'][(n, run, 'tsp')] = calculate_oct(order)
                df_results['GroundRules'][(n, run, 'tsp')] = ground_rules
                print(t)

            if 'asp' in encodings:
                print('asp encoding')
                t = time.time()
                opt_value, order, ground_rules = run_asp(products, run)
                t = time.time() - t
                df_results['Time'][(n, run, 'asp')] = t
                df_results['OptValue'][(n, run, 'asp')] = opt_value
                df_results['C'][(n, run, 'asp')] = calculate_oct(order)
                df_results['GroundRules'][(n, run, 'asp')] = ground_rules
                print(t)

            if 'seq' in encodings:
                print('seq encoding')
                t = time.time()
                opt_value, order, ground_rules = run_seq_encoding(products, run)
                t = time.time() - t
                df_results['Time'][(n, run, 'seq')] = t
                df_results['OptValue'][(n, run, 'seq')] = opt_value
                df_results['GroundRules'][(n, run, 'seq')] = ground_rules
                print(t)

            if 'bad' in encodings:
                print('bad encoding')
                t = time.time()
                opt_value, order, ground_rules = run_bad_encoding(products, run)
                t = time.time() - t
                df_results['Time'][(n, run, 'bad')] = t
                df_results['OptValue'][(n, run, 'bad')] = opt_value
                df_results['GroundRules'][(n, run, 'bad')] = ground_rules
                print(t)

            if 'ilp' in encodings:
                print('ilp encoding')
                t = time.time()
                opt_value, order, numVariables, numConstraints = run_ilp(products, run)
                t = time.time() - t
                df_results['Time'][(n, run, 'ilp')] = t
                df_results['OptValue'][(n, run, 'ilp')] = opt_value
                df_results['C'][(n, run, 'ilp')] = calculate_oct(order)
                df_results['Variables'][(n, run, 'ilp')] = numVariables
                df_results['Constraints'][(n, run, 'ilp')] = numConstraints
                print(t)

            print('--------')

        df_results.to_csv(RESULTS_FILE)
