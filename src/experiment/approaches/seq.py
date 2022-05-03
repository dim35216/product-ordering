import subprocess
import os
from typing import Set
import sys
sys.path.append(os.path.abspath('..'))
from constants import TSP_ENCODING, TPO_ENCODING, PROJECT_FOLDER, TIMEOUT
from utils import calculateOCT
from approaches.tsp import create_instance, interpret_clingo

def run_seq_encoding(products : Set[str], run : int) -> int:
    """Computing the Product Ordering problem as a logic program using the perfect TSP encoding,
    but the start and end product is specified explicitly; as a consequence, the solver runs O(n^2)
    times; in each run, the Product Ordering problem instance has to transformed into a TSP instance using
    a little additional logic program

    Args:
        products (Set[str]): set of products
        run (int): id of run

    Returns:
        int: best objective value, optimal product order, accumulated number of ground rules
    """
    filename = os.path.join(PROJECT_FOLDER, 'experiments', 'instances', 'tsp', f'instance_{len(products)}_{run}.lp')
    if not os.path.exists(filename):
        create_instance(products, filename)
    assert os.path.exists(filename)
    assert os.path.exists(TSP_ENCODING)
    assert os.path.exists(TPO_ENCODING)

    template_args = ['clingo', TSP_ENCODING, TPO_ENCODING, filename, '--quiet=1,0', '--out-ifs=\n']
    numCalls = len(products) * (len(products) - 1)

    minC = 10080
    minOrder = []
    for p1 in products:
        for p2 in products:
            if p1 != p2:
                try:
                    args = template_args + [f'-c s=p{p1}', f'-c e=p{p2}']
                    process = subprocess.run(args, capture_output=True, text=True, timeout=TIMEOUT/numCalls)
                except subprocess.TimeoutExpired:
                    return -1, [], -1

                _, order = interpret_clingo(process.stdout)
                assert len(order) == len(products)

                C = calculateOCT(order)
                if C < minC:
                    minC = C
                    minOrder = order

    try:
        args=['gringo', TSP_ENCODING, TPO_ENCODING, filename, '--text'] + [f'-c s=p{p1}', f'-c e=p{p2}']
        lines = subprocess.run(args, capture_output=True).stdout.count(b'\n')
        lines = lines * numCalls
    except subprocess.TimeoutExpired:
        lines = -1

    return minC, minOrder, lines