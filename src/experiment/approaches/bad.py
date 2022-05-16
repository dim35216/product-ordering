"""Approach for solving the Product Ordering approach:
Interpretation of problem instance as TSP and usage of bad encoding
"""
import subprocess
from typing import Set, Tuple, List
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import BAD_ENCODING, TPO_ENCODING, PROJECT_FOLDER, TIMEOUT
sys.path.append(os.path.abspath(PROJECT_FOLDER))
from src.experiment.approaches.tsp import create_instance, interpret_clingo

def run_bad_encoding(products : Set[str], run : int) -> Tuple[int, List[str], int]:
    """Computing the Product Ordering problem as a logic program using the bad TSP encoding;
    therefore the Product Ordering problem instance has to transformed into a TSP instance using
    a little additional logic program

    Args:
        products (Set[str]): set of products
        run (int): id of run

    Returns:
        Tuple[int, List[str], int]: minimal overall changeover time, optimal product order, number of ground rules
    """
    filename = os.path.join(PROJECT_FOLDER, 'experiments', 'instances', 'bad',
        f'instance_{len(products)}_{run}.lp')
    create_instance(products, filename)
    assert os.path.exists(filename)
    assert os.path.exists(BAD_ENCODING)

    try:
        args = ['clingo', BAD_ENCODING, TPO_ENCODING, filename, '--quiet=1,0', '--out-ifs=\n']
        process = subprocess.run(args, capture_output=True, text=True, check=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return -1, [], -1

    opt_value, order = interpret_clingo(process.stdout)
    assert len(order) == len(products)

    try:
        args=['gringo', BAD_ENCODING, TPO_ENCODING, filename, '--text']
        lines = subprocess.run(args, capture_output=True, check=True,
            timeout=TIMEOUT).stdout.count(b'\n')
    except subprocess.TimeoutExpired:
        lines = -1

    return opt_value, order, lines
