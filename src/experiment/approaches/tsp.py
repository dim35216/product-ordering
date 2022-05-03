import pandas as pd
import subprocess
import re
import os
from typing import Set, List, Tuple
import sys
sys.path.append(os.path.abspath('..'))
from constants import CHANGEOVER_MATRIX, TSP_ENCODING, TPO_ENCODING, PROJECT_FOLDER, TIMEOUT

def create_instance(products : Set[str], filename : str) -> None:
    """Modelling an Product Ordering problem instance as a logic program in Answer Set Programming

    Args:
        products (Set[str]): set of products
        filename (str): file to resulting LP instance file
    """
    df = pd.read_csv(CHANGEOVER_MATRIX, index_col=0)

    result = ''
    for product in products:
        result += f'node(p{product}).\n'
    for product1 in products:
        for product2 in products:
            if product1 != product2:
                result += f'edge(p{product1}, p{product2}).\n'
    for product1 in products:
        for product2 in products:
            if product1 != product2:
                value = df[product2][int(product1)]
                result += f'cost(p{product1}, p{product2}, {value}).\n'

    with open(filename, 'w') as f:
        f.write(result)
    return

def interpret_clingo(cmd_output : str) -> Tuple[int, List[str]]:
    """Parsing the command line output of the answer set solver clingo for extracting the
    resulting order of products for the TSP encoding

    Args:
        cmd_output (str): command line output of clingo

    Returns:
        Tuple[int, List[str]]: objective value, optimal product order
    """
    pattern_cycle = re.compile('cycle\(p(\d*),p(\d*)\)')
    pattern_start = re.compile('cycle\(v,p(\d*)\)')
    pattern_end = re.compile('cycle\(p(\d*),v\)')
    pattern_opt = re.compile('Optimization: (\d*)')
    
    optValue = None
    start = None
    end = None
    order_dict = {}
    for line in cmd_output.split('\n'):
        result_cycle = pattern_cycle.match(line)
        result_start = pattern_start.match(line)
        result_end = pattern_end.match(line)
        result_opt = pattern_opt.match(line)
        
        if result_cycle:
            p1 = result_cycle.group(1)
            p2 = result_cycle.group(2)
            assert p1 not in order_dict
            order_dict[p1] = p2
        
        if result_start:
            start = result_start.group(1)

        if result_end:
            end = result_end.group(1)

        if result_opt:
            optValue = result_opt.group(1)

    assert optValue is not None
    assert start is not None
    assert end is not None
    
    order = []
    current = start
    while current != end:
        order.append(current)
        current = order_dict[current]
    order.append(end)

    return optValue, order

def run_tsp_encoding(products : Set[str], run : int) -> Tuple[int, List[str], int]:
    """Computing the Product Ordering problem as a logic program using the perfect TSP encoding;
    therefore the Product Ordering problem instance has to transformed into a TSP instance using
    a little additional logic program

    Args:
        products (Set[str]): set of products
        run (int): id of run

    Returns:
        Tuple[int, List[str], int]: objective value, optimal product order, number of ground rules
    """
    filename = os.path.join(PROJECT_FOLDER, 'experiments', 'instances', 'tsp', f'instance_{len(products)}_{run}.lp')
    create_instance(products, filename)
    assert os.path.exists(filename)
    assert os.path.exists(TSP_ENCODING)
    assert os.path.exists(TPO_ENCODING)

    try:
        args=['clingo', TSP_ENCODING, TPO_ENCODING, filename, '--quiet=1,0', '--out-ifs=\n']
        process = subprocess.run(args, capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return -1, [], -1

    optValue, order = interpret_clingo(process.stdout)
    assert len(order) == len(products)

    try:
        args=['gringo', TSP_ENCODING, TPO_ENCODING, filename, '--text']
        lines = subprocess.run(args, capture_output=True).stdout.count(b'\n')
    except subprocess.TimeoutExpired:
        lines = -1

    return optValue, order, lines
