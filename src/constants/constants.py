import os

# Folder constants
PROJECT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
EXPERIMENTS_FOLDER = os.path.join(PROJECT_FOLDER, 'experiments')
EVALUATIONS_FOLDER = os.path.join(PROJECT_FOLDER, 'evaluations')
INSTANCES_FOLDER = os.path.join(EXPERIMENTS_FOLDER, 'instances')

# Product information
CHANGEOVER_MATRIX = os.path.join(EXPERIMENTS_FOLDER, 'changeover_matrix.csv')
CAMPAIGNS_ORDER = os.path.join(EXPERIMENTS_FOLDER, 'campaigns_order.csv')
PRODUCT_PROPERTIES = os.path.join(EXPERIMENTS_FOLDER, 'product_properties.csv')
PRODUCT_QUANTITY = os.path.join(EXPERIMENTS_FOLDER, 'product_quantity.csv')

# LP encodings
PO_ENCODING = os.path.join(EXPERIMENTS_FOLDER, 'encodings', 'po.lp')
NORMAL_OPT_ENCODING = os.path.join(EXPERIMENTS_FOLDER, 'encodings', 'optimization', 'normal_opt.lp')
ADVANCED_OPT_ENCODING = os.path.join(EXPERIMENTS_FOLDER, 'encodings', 'optimization', 'advanced_opt.lp')
CONSTRAINT_1_ENCODING = os.path.join(EXPERIMENTS_FOLDER, 'encodings', 'constraints', 'c1.lp')
CONSTRAINT_2_ENCODING = os.path.join(EXPERIMENTS_FOLDER, 'encodings', 'constraints', 'c2.lp')
CONSTRAINT_3_ENCODING = os.path.join(EXPERIMENTS_FOLDER, 'encodings', 'constraints', 'c3.lp')
CONSTRAINT_4_ENCODING = os.path.join(EXPERIMENTS_FOLDER, 'encodings', 'constraints', 'c4.lp')

# Results file of computational experiment
RESULTS_FILE = os.path.join(EXPERIMENTS_FOLDER, 'results.csv')
RESULTS_BACKUP_FILE = os.path.join(EXPERIMENTS_FOLDER, 'results_backup.csv')

# PDDL encodings
DOMAIN_PDDL = os.path.join(PROJECT_FOLDER, 'examples', 'productordering', 'domain.pddl')

# Additional executables / scripts
CONCORDE_EXE = os.path.join(PROJECT_FOLDER, 'include', 'concorde-bin')
FAST_DOWNWARD_EXE = os.path.join(PROJECT_FOLDER, 'include', './fast-downward.py')

# Timeout per experiment in seconds
TIMEOUT = 600.0

# Arc length infinity
INF = 100000000
