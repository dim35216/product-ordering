from typing import List
import os
import pandas as pd
import sys
sys.path.append(os.path.abspath('.'))
from constants import CHANGEOVER_MATRIX

def calculate_oct(order: List[str]) -> int:
    """Calculate the overall changeover time for a given product order and the changeover matrix

    Args:
        order (List[str]): product order

    Returns:
        int: overall changeover time
    """
    df_matrix = pd.read_csv(CHANGEOVER_MATRIX, index_col=0)
    C = 0
    for i in range(1, len(order)):
        p1 = order[i - 1]
        p2 = order[i]
        C += df_matrix.at[int(p1), p2]
    return C
