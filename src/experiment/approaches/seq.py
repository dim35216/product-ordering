"""Approach for solving the Product Ordering approach:
Interpretation of problem instance as TSP and usage of sequential encoding
"""
import subprocess
from typing import Set, Tuple, List
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import TSP_ENCODING, TPO_ENCODING, PROJECT_FOLDER, TIMEOUT
sys.path.append(os.path.abspath(PROJECT_FOLDER))
from src.experiment.approaches.tsp import create_instance, interpret_clingo
from src.experiment.utils import calculate_oct

def run_seq_encoding(products : Set[str], run : int) -> Tuple[int, List[int], int]:
    """Computing the Product Ordering problem as a logic program using the perfect TSP encoding,
    but the start and end product is specified explicitly; as a consequence, the solver runs O(n^2)
    times; in each run, the Product Ordering problem instance has to transformed into a TSP
    instance using a little additional logic program

    Args:
        products (Set[str]): set of products
        run (int): id of run

    Returns:
        int: best objective value, optimal product order, accumulated number of ground rules
    """
    filename = os.path.join(PROJECT_FOLDER, 'experiments', 'instances', 'tsp',
        f'instance_{len(products)}_{run}.lp')
    if not os.path.exists(filename):
        create_instance(products, filename)
    assert os.path.exists(filename)
    assert os.path.exists(TSP_ENCODING)
    assert os.path.exists(TPO_ENCODING)

    template_args = ['clingo', TSP_ENCODING, TPO_ENCODING, filename, '--quiet=1,0', '--out-ifs=\n']
    num_calls = len(products) * (len(products) - 1)

    product1 = ''
    product2 = ''
    min_oct = 10080
    min_order = []
    for product1 in products:
        for product2 in products:
            if product1 != product2:
                try:
                    args = template_args + [f'-c s=p{product1}', f'-c e=p{product2}']
                    process = subprocess.run(args, capture_output=True, text=True, check=True,
                                             timeout=TIMEOUT/num_calls)
                except subprocess.TimeoutExpired:
                    return -1, [], -1

                _, order = interpret_clingo(process.stdout)
                assert len(order) == len(products)

                cur_oct = calculate_oct(order)
                if cur_oct < min_oct:
                    min_oct = cur_oct
                    min_order = order

    try:
        args = ['gringo', TSP_ENCODING, TPO_ENCODING, filename,
                '--text'] + [f'-c s=p{product1}', f'-c e=p{product2}']
        lines = subprocess.run(args, capture_output=True, check=True).stdout.count(b'\n')
        lines = lines * num_calls
    except subprocess.TimeoutExpired:
        lines = -1

    return min_oct, min_order, lines
