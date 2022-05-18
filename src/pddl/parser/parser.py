from typing import Set, Dict, Any, List
import logging
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from constants.constants import PROJECT_FOLDER
sys.path.append(PROJECT_FOLDER)
from src.pddl.parser.action import Action
from src.pddl.parser.utils import scan_tokens, parse_hierarchy, parse_fluents, \
    frozenset_of_tuples, split_predicates, parse_goal

class Parser:
    """PDDL parser, which parses PDDL planning problems divided
    into a domain file and a problem file
    """

    SUPPORTED_REQUIREMENTS = [':strips', ':negative-preconditions', ':typing', ':adl',
                              ':preferences', ':disjunctive-preconditions', ':equality',
                              ':numeric-fluents']
    SUPPORTED_SUPER_REQUIREMENTS = {':adl': [':strips', ':typing' , ':disjunctive-preconditions',
                                    ':equality', ':quantified-preconditions', ':condition-effects']}

    def __init__(self, domain : str, problem : str) -> None:
        """Constructor of PDDL parser

        Args:
            domain (str): path to PDDL domain file
            problem (str): path to PDDL problem file
        """
        self.domain_name = 'unknown'
        self.requirements : Set[str] = set()
        self.types : Dict[str, list] = {}
        self.constants : Dict[str, Any] = {}
        self.actions : List[Action] = []
        self.predicates : Dict[str, dict] = {}
        self.functions : Dict[str, dict] = {}

        self.parse_domain(domain)

        self.problem_name = 'unknown'
        self.state : tuple = ()
        self.objects : Dict[str, list] = {}
        self.numeric_fluents : Dict[str, dict] = {}
        for function in self.functions:
            self.numeric_fluents[function] = {}
        self.goal : tuple = ('and', [])
        self.preferences : Dict[str, tuple] = {}
        self.metric : tuple = ()

        self.parse_problem(problem)

    def parse_domain(self, domain_filename : str):
        """Parse the domain of a PDDL planning problem

        Args:
            domain_filename (str): path to PDDL domain file
        """
        tokens = scan_tokens(domain_filename)

        if not isinstance(tokens, list) or tokens.pop(0) != 'define':
            raise Exception('File ' + domain_filename + ' does not match domain pattern')

        for group in tokens:
            token = group.pop(0)

            if token == 'domain':
                self.domain_name = group[0]

            elif token == ':requirements':
                group = set(group)
                for req in group:
                    if req in self.SUPPORTED_SUPER_REQUIREMENTS:
                        self.requirements.update(self.SUPPORTED_SUPER_REQUIREMENTS[req])
                    if not req in self.SUPPORTED_REQUIREMENTS:
                        raise Exception('Requirement ' + req + ' not supported')
                group.difference_update(self.SUPPORTED_SUPER_REQUIREMENTS)
                self.requirements.update(group)

            elif token == ':constants':
                parse_hierarchy(group, self.constants, 'constants', False)

            elif token == ':functions':
                parse_fluents(group, self.functions, 'functions')

            elif token == ':predicates':
                parse_fluents(group, self.predicates, 'predicates')

            elif token == ':types':
                parse_hierarchy(group, self.types, 'types', True)

            elif token == ':action':
                self.parse_action(group)

            else:
                logging.error(str(token) + ' is not recognized in domain')


    def parse_problem(self, problem_filename : str):
        """Parse the problem instance of a PDDL planning problem

        Args:
            problem_filename (str): path to PDDL problem file
        """
        tokens = scan_tokens(problem_filename)

        if not isinstance(tokens, list) or tokens.pop(0) != 'define':
            raise Exception('File ' + problem_filename + ' does not match problem pattern')

        while tokens:
            group = tokens.pop(0)
            token = group.pop(0)

            if token == 'problem':
                self.problem_name = group[0]

            elif token == ':domain':
                if self.domain_name != group[0]:
                    raise Exception('Different domain specified in problem file')

            elif token == ':requirements':
                pass # Ignore requirements in problem, parse them in the domain

            elif token == ':objects':
                parse_hierarchy(group, self.objects, 'objects', False)

            elif token == ':init':
                state = set()
                for predicate in group:
                    assert isinstance(predicate, list)
                    assert len(predicate) > 0
                    if predicate[0] in self.predicates:
                        state.add(tuple(predicate))
                    elif predicate[0] == '=':
                        target = predicate[1]
                        source = predicate[2]
                        if isinstance(target, list) and len(target) != 0:
                            if target[0] in self.numeric_fluents:
                                if isinstance(source, str):
                                    self.numeric_fluents[target[0]][tuple(target[1:])] = int(source)
                self.state = frozenset_of_tuples(state)

            elif token == ':goal':
                assert len(group) == 1
                self.goal, self.preferences = parse_goal(group[0])

            elif token == ':metric':
                assert len(group) == 2
                self.metric = tuple([group[0], self.parse_numeric_operation(group[1])])

            else:
                logging.error(str(token) + ' is not recognized in problem')

    def parse_action(self, group : list):
        """Parse PDDL action

        Args:
            group (list): hierarchied list of tokens extracted from the PDDL domain file
        """
        name = group.pop(0)
        if not isinstance(name, str):
            raise Exception('Action without name definition')
        for action in self.actions:
            if action.name == name:
                raise Exception('Action ' + name + ' redefined')

        parameters = []
        preconditions : tuple = ()
        effects : tuple = ('and', [])

        while group:
            token = group.pop(0)

            if token == ':parameters':
                if not isinstance(group, list):
                    raise Exception('Error with ' + name + ' parameters')
                untyped_parameters : List[List[str]] = []
                param = group.pop(0)
                while param:
                    token = param.pop(0)
                    if token == '-':
                        if not untyped_parameters:
                            raise Exception('Unexpected hyphen in ' + name + ' parameters')
                        ptype = param.pop(0)
                        while untyped_parameters:
                            parameters.append([untyped_parameters.pop(0), ptype])
                    else:
                        untyped_parameters.append(token)
                while untyped_parameters:
                    parameters.append([untyped_parameters.pop(0), 'object'])

            elif token == ':precondition':
                preconditions = split_predicates(group.pop(0), name, ' preconditions')

            elif token == ':effect':
                effects = split_predicates(group.pop(0), name, ' effects')

            else:
                logging.error(str(token) + ' is not recognized in action')

        self.actions.append(Action(name, parameters, preconditions, effects))

    def parse_numeric_operation(self, group : list) -> tuple:
        """Parse numeric operation occuring in the goal
        representations in PDDL problem instance files

        Args:
            group (list): hierarchied list of tokens from goal representation

        Returns:
            tuple: numeric expression
        """
        if not isinstance(group, list):
            return tuple([group])
        assert len(group) > 0

        expression = None
        if group[0] == '+':
            assert len(group) > 1
            elements = []
            for term in group[1:]:
                elements.append(self.parse_numeric_operation(term))
            expression = tuple(['+', elements])

        elif group[0] == '*':
            assert len(group) > 2
            elements = []
            for term in group[1:]:
                elements.append(self.parse_numeric_operation(term))
            expression = tuple(['*', elements])

        elif group[0] == 'is-violated':
            assert len(group) == 2
            expression = tuple(['is-violated', self.parse_numeric_operation(group[1])])

        elif group[0] in self.functions:
            expression = tuple(group)

        else:
            raise Exception('Error in parse numeric operation')

        return expression
