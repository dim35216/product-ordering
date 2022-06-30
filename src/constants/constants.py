import os

PROJECT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
INSTANCES_FOLDER = os.path.join(PROJECT_FOLDER, 'experiments', 'instances')

CHANGEOVER_MATRIX = os.path.join(PROJECT_FOLDER, 'experiments', 'changeover_matrix.csv')
CAMPAIGNS_ORDER = os.path.join(PROJECT_FOLDER, 'experiments', 'campaigns_order.csv')
PRODUCT_PROPERTIES = os.path.join(PROJECT_FOLDER, 'experiments', 'product_properties.csv')
PRODUCT_QUANTITY = os.path.join(PROJECT_FOLDER, 'experiments', 'product_quantity.csv')

# LP encodings
PERFECT_TSP_ENCODING = os.path.join(PROJECT_FOLDER, 'experiments', 'encodings', 'perfect_tsp.lp')
BAD_TSP_ENCODING = os.path.join(PROJECT_FOLDER, 'experiments', 'encodings', 'bad_tsp.lp')
PERFECT_PO_ENCODING = os.path.join(PROJECT_FOLDER, 'experiments', 'encodings', 'perfect_po.lp')
BAD_PO_ENCODING = os.path.join(PROJECT_FOLDER, 'experiments', 'encodings', 'bad_po.lp')

# PDDL encodings
DOMAIN_PDDL = os.path.join(PROJECT_FOLDER, 'examples', 'productordering', 'domain.pddl')

# Results file of computational experiment
RESULTS_FILE = os.path.join(PROJECT_FOLDER, 'experiments', 'results.csv')
RESULTS_BACKUP_FILE = os.path.join(PROJECT_FOLDER, 'experiments', 'results_backup.csv')

# Additional executables / scripts
CONCORDE_EXE = os.path.join(PROJECT_FOLDER, 'include', 'concorde-bin')
FAST_DOWNWARD_EXE = os.path.join(PROJECT_FOLDER, 'include', './fast-downward.py')

# Timeout per experiment in seconds
TIMEOUT = 600.0
