import os

PROJECT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
INSTANCES_FOLDER = os.path.join(PROJECT_FOLDER, 'experiments', 'instances')

CHANGEOVER_MATRIX = os.path.join(PROJECT_FOLDER, 'experiments', 'changeover_matrix.csv')

# LP encodings
TSP_ENCODING = os.path.join(PROJECT_FOLDER, 'experiments', 'perfect_tsp.lp')
BAD_ENCODING = os.path.join(PROJECT_FOLDER, 'experiments', 'bad_tsp.lp')

# PDDL encodings
DOMAIN_PDDL = os.path.join(PROJECT_FOLDER, 'examples', 'productordering', 'domain.pddl')

# Results file of computational experiment
RESULTS_FILE = os.path.join(PROJECT_FOLDER, 'experiments', 'results.csv')
RESULTS_BACKUP_FILE = os.path.join(PROJECT_FOLDER, 'experiments', 'results_backup.csv')

# Additional executables / scripts
CONCORDE_EXE = os.path.join(PROJECT_FOLDER, 'include', 'concorde-bin')
FAST_DOWNWARD_EXE = os.path.join(PROJECT_FOLDER, 'include', './fast-downward.py')

# Timeout per experiment in seconds
TIMEOUT = 300.0
