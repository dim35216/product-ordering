from typing import List, Dict
import os
import pandas as pd
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from constants import CHANGEOVER_MATRIX

def calculate_oct(order: List[str], occurences : Dict[str, int] = {}) -> int:
    """Calculate the overall changeover time for a given product order and the changeover matrix

    Args:
        order (List[str]): product order

    Returns:
        int: overall changeover time
    """
    assert len(order) == len(set(order))
    df_matrix = pd.read_csv(CHANGEOVER_MATRIX, index_col=0)
    C = 0
    for i in range(1, len(order)):
        p1 = order[i - 1]
        p2 = order[i]
        C += df_matrix.at[int(p1), p2]
    for num in occurences.values():
        assert num >= 1
        C += (num - 1) * 15
    return C
