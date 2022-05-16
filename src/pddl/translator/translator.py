import time
from typing import List
import logging
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from pddl.parser.parser import Parser

class Translator:
    """This class implements a translator of a planning problem, given in the domain
       description language PDDL (Planning Domain Definition Language), into a logic
       program considering the description language of ASP (Answer Set Programming)
    """

    @staticmethod
    def _construct_term(name : str, params : list, strong_negation : bool = False, sep : str = ',') -> str:
        """Static and protected method for constructing ASP predicates

        Args:
            name (str): name of the predicate
            params (list): list of variables of the predicate
            strong_negation (bool, optional): Addition of the prefix '-' to the predicate name. Defaults to False.
            sep (str, optional): separation delimiter. Defaults to ','.

        Returns:
            str: constructed ASP predicate
        """
        assert sep in [',', ';']
        reserved = ['T', 'T - 1', 'V', 'V1', 'V2', 'Value']
        term = ''
        if strong_negation:
            term += '-'
        term += str(name).replace('-', '_').lower()
        if len(params) > 0:
            term += '('
            for param in params:
                if isinstance(param, str) and param[0] == '?':
                    assert param[1:].capitalize() not in reserved
                    term += param[1:].capitalize() + sep + ' '
                elif param in reserved:
                    term += str(param) + sep + ' '
                else:
                    term += str(param).replace('-', '_').lower() + sep + ' '
            term = term[:-2] + ')'
        return term


    def translate(self, domain : str, problem : str, timesteps : int) -> str:
        """Public method for translating a given planning problem, given as its domain
           (together with its initial state) and a limit of timesteps, into an ASP logic
           program

        Args:
            domain (str): path to domain encoding file
            problem (str): path to problem instance file
            timesteps (int): limit of timesteps of the planning problem

        Returns:
            str: ASP logic program
        """
        # Parser
        parser = Parser(domain, problem)

        # Parsed data
        logging.debug('predicates: %s', str(parser.predicates))
        logging.debug('goal: %s', str(parser.goal))
        logging.debug('actions: %s', str(parser.actions))
        logging.debug('predicates: %s', str(parser.predicates))

        pi = []

        pi.append('% Definitions\n')
        pi.append(f'#const timesteps={timesteps}.\n')
        pi.append('time(1..timesteps).\n\n')

        pi.append('%% Constants\n')
        for typ, values in parser.constants.items():
            if len(values) > 0:
                pi.append(f'{self._construct_term(typ, values, sep=";")}.\n')
        if len(parser.constants.items()) == 0:
            pi.append('% empty\n')

        pi.append('%% Objects\n')
        for typ, values in parser.objects.items():
            if len(values) > 0:
                pi.append(f'{self._construct_term(typ, values, sep=";")}.\n')
        if len(parser.objects.items()) == 0:
            pi.append('% empty\n')

        for typ, subtypes in parser.types.items():
            for subtype in subtypes:
                pi.append(f'{typ}(X)\t:- {subtype}(X).\n')

        fluents_in_effects = set()
        fluents_with_negated_effects = set()
        for action in parser.actions:
            if len(action.effects) == 1:
                action.effects = ('and', [action.effects])

            for effect in action.effects[1]:

                negated = False
                if effect[0] == 'not':
                    effect = effect[1]
                    negated = True
                if effect[0] in parser.predicates:
                    fluents_in_effects.add(effect[0])
                    if negated:
                        fluents_with_negated_effects.add(effect[0])
                elif effect[0] in ['+', 'assign']:
                    fluents_in_effects.add(effect[1][0])
                    fluents_with_negated_effects.add(effect[1][0])

        def repr_fluent(fluent : tuple, time_term : str = '', add_list : List[str] = [],
                        default_negation : bool = False, strong_negation : bool = False) -> str:
            if len(fluent) == 0:
                raise Exception('Empty fluent!')
            result = ''
            if default_negation:
                result += 'not '
            params = list(fluent)[1:] + add_list
            if fluent[0] in fluents_in_effects and time_term != '' and time_term not in params:
                params.append(time_term)
            result += self._construct_term(fluent[0], params, strong_negation)
            return result

        for action in parser.actions:
            pi.append(f'\n% ---- action: {action.name} ----\n')

            logging.debug('action.parameters: %s', str(action.parameters))
            logging.debug('action.effects: %s', str(action.effects))
            logging.debug('action.preconditions: %s', str(action.preconditions))

            pi.append(f'action({action.repr_asp_term()})')
            if action.parameters:
                pi.append(f'\t:- {action.repr_parameters(leading_sep=False)}')
            pi.append('.\n\n')

            for effect in action.effects[1]:
                strong_negation = False
                if effect[0] == 'not':
                    effect = effect[1]
                    strong_negation = True
                if effect[0] in parser.predicates:
                    pi.append(f'{repr_fluent(effect, time_term="T", strong_negation=strong_negation)}\t:- time(T), occ({action.repr_asp_term()}, T){action.repr_parameters()}.\n')

                elif effect[0] == '+':
                    pi.append(f'{repr_fluent(effect[1], time_term="T", add_list= ["V"])}\t:- time(T), occ({action.repr_asp_term()}, T){action.repr_parameters()}, {repr_fluent(effect[1], time_term="T - 1", add_list=["V1"])}')
                    if effect[2][0] in fluents_in_effects:
                        pi.append(f', {repr_fluent(effect[2], time_term="T", add_list=["V2"])}, V = V1 + V2.\n')
                    else:
                        pi.append(f', {repr_fluent(effect[2], add_list=["V2"])}, V = V1 + V2.\n')
                    pi.append(f'{repr_fluent(effect[1], time_term="T", add_list=["V"], strong_negation=True)}\t:- time(T), occ({action.repr_asp_term()}, T){action.repr_parameters()}, {repr_fluent(effect[1], time_term="T - 1", add_list=["V"])}.\n')

                elif effect[0] == 'assign':
                    pi.append(f'{repr_fluent(effect[1], time_term = "T", add_list=["V"])}\t:- time(T), occ({action.repr_asp_term()}, T){action.repr_parameters()}, V = {effect[2]}.\n')
                    pi.append(f'{repr_fluent(effect[1], time_term = "T", add_list=["V"], strong_negation=True)}\t:- time(T), occ({action.repr_asp_term()}, T){action.repr_parameters()}, {repr_fluent(effect[1], time_term = "T - 1", add_list=["V"])}.\n')

            if len(action.effects[1]) > 0:
                pi.append('\n')

            if len(action.preconditions) == 1:
                action.preconditions = ('and', [action.preconditions])

            pi.append(f'possible({action.repr_asp_term()}, T)\t:- time(T)')
            for precondition in action.preconditions[1]:
                pi.append(', ')
                default_negation = False
                if precondition[0] == 'not':
                    precondition = precondition[1]
                    default_negation = True
                if precondition[0] in parser.predicates:
                    pi.append(repr_fluent(precondition, time_term="T - 1", default_negation=default_negation))
                elif precondition[0] == '<':
                    pi.append(f'{repr_fluent(precondition[1], time_term="T - 1", add_list=["Value"])}, Value < {precondition[2]}')
                else:
                    raise Exception('Using unimplemented feature')
            pi.append(f'{action.repr_parameters()}.\n')

        pi.append('\n% Action generation rule with Executability constraint\n')
        pi.append('1 { occ(A, T) : possible(A, T), action(A) } 1 :- time(T).\n\n')

        pi.append('% Inertia rules\n')
        pi.append('%% Fluents (Predicates)\n')
        for predicate_name, predicate_params in parser.predicates.items():
            if predicate_name in fluents_in_effects:
                pi.append(self._construct_term(predicate_name, list(predicate_params.keys()) + ['T']))
                pi.append('\t:- time(T), ')
                pi.append(self._construct_term(predicate_name, list(predicate_params.keys()) + ['T - 1']))
                if predicate_name in fluents_with_negated_effects:
                    pi.append(f', not {self._construct_term(predicate_name, list(predicate_params.keys()) + ["T"], strong_negation=True)}')
                pi.append('.\n')
        if sum([predicateName in fluents_in_effects for predicateName in parser.predicates.keys()]) == 0:
            pi.append('% empty\n')

        pi.append('%% Numeric Fluents (Functions)\n')
        for function_name, function_params in parser.functions.items():
            if function_name in fluents_in_effects:
                pi.append(self._construct_term(function_name, list(function_params.keys()) + ['V', 'T']))
                pi.append('\t:- time(T), ')
                pi.append(self._construct_term(function_name, list(function_params.keys()) + ['V', 'T - 1']))
                if function_name in fluents_with_negated_effects:
                    pi.append(f', not {self._construct_term(function_name, list(function_params.keys()) + ["V", "T"], strong_negation=True)}')
                pi.append('.\n')
        if sum([functionName in fluents_in_effects for functionName in parser.functions.keys()]) == 0:
            pi.append('% empty\n')

        pi.append('\n')

        def build_goal(goal : tuple) -> str:
            result = ''
            if goal[0] in parser.predicates:
                return repr_fluent(goal, time_term='timesteps')

            if goal[0] == 'and':
                for token in goal[1]:
                    result += build_goal(token) + ', '
                result = result[:-2]

            elif goal[0] == 'or':
                result += '1 { '
                for token in goal[1]:
                    if isinstance(token, tuple):
                        result += build_goal(token) + '; '
                    elif isinstance(token, list):
                        result += repr_fluent(tuple(token), time_term='timesteps')
                result = result[:-2] + ' }'

            elif goal[0] == 'not':
                result += repr_fluent(goal[1], time_term='timesteps', default_negation=True)

            else:
                raise Exception('Error with build goal ' + str(goal))

            return result

        pi.append('% Goal representation\n')
        pi.append('%% Hard goals\n')
        if len(parser.goal[1]) > 0:
            pi.append(f'goal :- {build_goal(parser.goal)}.\n:- not goal.\n')
        else:
            pi.append('% empty\n')

        pi.append('%% Soft goals\n')
        if len(parser.metric) > 0:
            opt_goal, numeric_expression = parser.metric
            preferences = []
            negative_preferences = []
            for term in numeric_expression[1]:
                if term[0] in parser.numeric_fluents:
                    pi.append(f'#{opt_goal}{{ V')
                    for token in list(term)[1:]:
                        pi.append(f', {token[1:].capitalize()}')
                    pi.append(f' : {repr_fluent(term, time_term="timesteps", add_list=["V"])} }}.\n')
                elif term[0] == '*':
                    factors = term[1]
                    pi.append(f'#{opt_goal}{{ {int(float(factors[0][0]))} : ')
                    if len(factors[1]) == 1:
                        preferences.append(factors[1][0])
                        pi.append(factors[1][0])
                    elif len(factors[1]) == 2:
                        assert factors[1][0] == 'is-violated'
                        preferences.append(factors[1][1][0])
                        negative_preferences.append(factors[1][1][0])
                        pi.append(f'violated_{factors[1][1][0]}')
                    pi.append(' }.\n')

            if len(preferences) > 0:
                pi.append('%% Preferences\n')
                for pref_name, pref_expression in [(p, parser.preferences[p]) for p in preferences]:
                    pi.append(f'{pref_name}\t:- {build_goal(pref_expression)}.\n')
                    if pref_name in negative_preferences:
                        pi.append(f'violated_{pref_name}\t:- not {pref_name}.\n')
        else:
            pi.append('% empty\n')

        pi.append('\n% Display\n')
        pi.append('#show occ/2.\n')

        pi.append('\n% Initial state\n')

        pi.append('%% Fluents\n')
        for state in parser.state:
            pi.append(f'{repr_fluent(state, time_term="0")}.\n')
        if len(parser.state) == 0:
            pi.append('% empty\n')

        pi.append('%% Numeric Fluents\n')
        for name, data in parser.numeric_fluents.items():
            for params, value in data.items():
                fluent = tuple([name] + list(params) + [value])
                pi.append(f'{repr_fluent(fluent, time_term="0")}.\n')
        if len(parser.numeric_fluents) == 0:
            pi.append('% empty\n')

        program = ''.join(pi)

        return program

#-----------------------------------------------
# Main
#-----------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Please give the following command line arguments: ' + \
            'python [./]translator.py <domain_file> <problem_file> <timesteps>')
        sys.exit(1)
    domain = sys.argv[1]
    problem = sys.argv[2]
    timesteps = int(sys.argv[3])
    assert timesteps > 0
    logging.basicConfig(level=logging.INFO)
    logging.info('Translator started')
    start_time = time.time()
    translator = Translator()
    logic_program = translator.translate(domain, problem, timesteps)
    if logic_program is not None:
        filename = f'{problem}.lp'
        with open(filename, 'w') as f:
            f.write(logic_program)
            logging.info('Logic program written into file %s.lp', problem)
    else:
        logging.error('Translation was not possible')
        sys.exit(1)
    logging.info('Translator ended after %ss', str(time.time() - start_time))
