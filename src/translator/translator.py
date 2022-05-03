import time
from typing import List
import logging
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

from pddl.parser import Parser

class Translator:
    """This class implements a tranlator of a planning problem, given in the domain
       description language PDDL (Planning Domain Definition Language), into a logic
       program considering the description language of ASP (Answer Set Programming)
    """

    @staticmethod
    def _constructTerm(name : str, params : list, strongNegation : bool = False, sep : str = ',') -> str:
        """Static and protected method for constructing ASP predicates

        Args:
            name (str): name of the predicate
            params (List[str]): list of variables of the predicate
            negated (bool, optional): Addition of the prefix '-' to the predicate name. Defaults to False.

        Returns:
            str: constructed ASP predicate
        """
        assert sep in [',', ';']
        reserved = ['T', 'T - 1', 'V', 'V1', 'V2', 'Value']
        term = ''
        if strongNegation:
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

        Pi = []
        
        Pi.append('% Definitions\n')
        Pi.append(f'#const timesteps={timesteps}.\n')
        Pi.append('time(1..timesteps).\n\n')

        Pi.append('%% Constants\n')
        for typ, values in parser.constants.items():
            if len(values) > 0:
                Pi.append(f'{self._constructTerm(typ, values, sep=";")}.\n')
        if len(parser.constants.items()) == 0:
            Pi.append('% empty\n')

        Pi.append('%% Objects\n')
        for typ, values in parser.objects.items():
            if len(values) > 0:
                Pi.append(f'{self._constructTerm(typ, values, sep=";")}.\n')
        if len(parser.objects.items()) == 0:
            Pi.append('% empty\n')
        
        for type, subtypes in parser.types.items():
            for subtype in subtypes:
                Pi.append(f'{type}(X)\t:- {subtype}(X).\n')

        fluentsInEffects = set()
        fluentsWithNegatedEffects = set()
        for action in parser.actions:
            if len(action.effects) == 1:
                action.effects = ('and', [action.effects])
            
            for effect in action.effects[1]:
                
                negated = False
                if effect[0] == 'not':
                    effect = effect[1]
                    negated = True
                if effect[0] in parser.predicates:
                    fluentsInEffects.add(effect[0])
                    if negated:
                        fluentsWithNegatedEffects.add(effect[0])
                elif effect[0] in ['+', 'assign']:
                    fluentsInEffects.add(effect[1][0])
                    fluentsWithNegatedEffects.add(effect[1][0])

        def reprFluent(fluent : tuple, timeTerm : str = '', addList : List[str] = [],
                        defaultNegation : bool = False, strongNegation : bool = False) -> str:
            if len(fluent) == 0:
                raise Exception('Empty fluent!')
            result = ''
            if defaultNegation:
                result += 'not '
            params = list(fluent)[1:] + addList
            if fluent[0] in fluentsInEffects and timeTerm != '' and timeTerm not in params:
                params.append(timeTerm)
            result += self._constructTerm(fluent[0], params, strongNegation)
            return result

        for action in parser.actions:
            Pi.append(f'\n% ---- action: {action.name} ----\n')
            
            logging.debug('action.parameters: %s', str(action.parameters))
            logging.debug('action.effects: %s', str(action.effects))
            logging.debug('action.preconditions: %s', str(action.preconditions))

            Pi.append(f'action({action.repr_asp_term()})')
            if action.parameters:
                Pi.append(f'\t:- {action.repr_parameters(leading_sep=False)}')
            Pi.append('.\n\n')

            for effect in action.effects[1]:
                strongNegation = False
                if effect[0] == 'not':
                    effect = effect[1]
                    strongNegation = True
                if effect[0] in parser.predicates:
                    Pi.append(f'{reprFluent(effect, timeTerm="T", strongNegation=strongNegation)}\t:- time(T), occ({action.repr_asp_term()}, T){action.repr_parameters()}.\n')
                
                elif effect[0] == '+':
                    Pi.append(f'{reprFluent(effect[1], timeTerm="T", addList= ["V"])}\t:- time(T), occ({action.repr_asp_term()}, T){action.repr_parameters()}, {reprFluent(effect[1], timeTerm="T - 1", addList=["V1"])}')
                    if effect[2][0] in fluentsInEffects:
                        Pi.append(f', {reprFluent(effect[2], timeTerm="T", addList=["V2"])}, V = V1 + V2.\n')
                    else:
                        Pi.append(f', {reprFluent(effect[2], addList=["V2"])}, V = V1 + V2.\n')
                    Pi.append(f'{reprFluent(effect[1], timeTerm="T", addList=["V"], strongNegation=True)}\t:- time(T), occ({action.repr_asp_term()}, T){action.repr_parameters()}, {reprFluent(effect[1], timeTerm="T - 1", addList=["V"])}.\n')

                elif effect[0] == 'assign':
                    Pi.append(f'{reprFluent(effect[1], timeTerm = "T", addList=["V"])}\t:- time(T), occ({action.repr_asp_term()}, T){action.repr_parameters()}, V = {effect[2]}.\n')
                    Pi.append(f'{reprFluent(effect[1], timeTerm = "T", addList=["V"], strongNegation=True)}\t:- time(T), occ({action.repr_asp_term()}, T){action.repr_parameters()}, {reprFluent(effect[1], timeTerm = "T - 1", addList=["V"])}.\n')

            if len(action.effects[1]) > 0:
                Pi.append('\n')
            
            if len(action.preconditions) == 1:
                action.preconditions = ('and', [action.preconditions])

            Pi.append(f'possible({action.repr_asp_term()}, T)\t:- time(T)')
            for precondition in action.preconditions[1]:
                Pi.append(', ')
                defaultNegation = False
                if precondition[0] == 'not':
                    precondition = precondition[1]
                    defaultNegation = True
                if precondition[0] in parser.predicates:
                    Pi.append(reprFluent(precondition, timeTerm="T - 1", defaultNegation=defaultNegation))
                elif precondition[0] == '<':
                    Pi.append(f'{reprFluent(precondition[1], timeTerm="T - 1", addList=["Value"])}, Value < {precondition[2]}')
                else:
                    raise Exception('Using unimplemented feature')
            Pi.append(f'{action.repr_parameters()}.\n')
        
        Pi.append('\n% Action generation rule with Executability constraint\n')
        Pi.append('1 { occ(A, T) : possible(A, T), action(A) } 1 :- time(T).\n\n')

        Pi.append('% Inertia rules\n')
        Pi.append('%% Fluents (Predicates)\n')
        for predicateName, predicateParams in parser.predicates.items():
            if predicateName in fluentsInEffects:
                Pi.append(self._constructTerm(predicateName, list(predicateParams.keys()) + ['T']))
                Pi.append('\t:- time(T), ')
                Pi.append(self._constructTerm(predicateName, list(predicateParams.keys()) + ['T - 1']))
                if predicateName in fluentsWithNegatedEffects:
                    Pi.append(f', not {self._constructTerm(predicateName, list(predicateParams.keys()) + ["T"], strongNegation=True)}')
                Pi.append('.\n')
        if sum([predicateName in fluentsInEffects for predicateName in parser.predicates.keys()]) == 0:
            Pi.append('% empty\n')
        
        Pi.append('%% Numeric Fluents (Functions)\n')
        for functionName, functionParams in parser.functions.items():
            if functionName in fluentsInEffects:
                Pi.append(self._constructTerm(functionName, list(functionParams.keys()) + ['V', 'T']))
                Pi.append('\t:- time(T), ')
                Pi.append(self._constructTerm(functionName, list(functionParams.keys()) + ['V', 'T - 1']))
                if functionName in fluentsWithNegatedEffects:
                    Pi.append(f', not {self._constructTerm(functionName, list(functionParams.keys()) + ["V", "T"], strongNegation=True)}')
                Pi.append('.\n')
        if sum([functionName in fluentsInEffects for functionName in parser.functions.keys()]) == 0:
            Pi.append('% empty\n')

        Pi.append('\n')

        def build_goal(goal : tuple) -> str:
            result = ''
            if goal[0] in parser.predicates:
                return reprFluent(goal, timeTerm='timesteps')
            elif goal[0] == 'and':
                for t in goal[1]:
                    result += build_goal(t) + ', '
                result = result[:-2]

            elif goal[0] == 'or':
                result += '1 { '
                for t in goal[1]:
                    if isinstance(t, tuple):
                        result += build_goal(t) + '; '
                    elif isinstance(t, list):
                        result += reprFluent(tuple(t), timeTerm='timesteps')
                result = result[:-2] + ' }'

            elif goal[0] == 'not':
                result += reprFluent(goal[1], timeTerm='timesteps', defaultNegation=True)

            else:
                raise Exception('Error with build goal ' + str(goal))

            return result

        Pi.append('% Goal representation\n')
        Pi.append('%% Hard goals\n')
        if len(parser.goal[1]) > 0:
            Pi.append(f'goal :- {build_goal(parser.goal)}.\n:- not goal.\n')
        else:
            Pi.append('% empty\n')

        Pi.append('%% Soft goals\n')
        if len(parser.metric) > 0:
            opt_goal, numeric_expression = parser.metric
            preferences = []
            negative_preferences = []
            for term in numeric_expression[1]:
                if term[0] in parser.numeric_fluents:
                    Pi.append(f'#{opt_goal}{{ V')
                    for t in list(term)[1:]:
                        Pi.append(f', {t[1:].capitalize()}')
                    Pi.append(f' : {reprFluent(term, timeTerm="timesteps", addList=["V"])} }}.\n')
                elif term[0] == '*':
                    factors = term[1]
                    Pi.append(f'#{opt_goal}{{ {int(float(factors[0][0]))} : ')
                    if len(factors[1]) == 1:
                        preferences.append(factors[1][0])
                        Pi.append(factors[1][0])
                    elif len(factors[1]) == 2:
                        assert factors[1][0] == 'is-violated'
                        preferences.append(factors[1][1][0])
                        negative_preferences.append(factors[1][1][0])
                        Pi.append(f'violated_{factors[1][1][0]}')
                    Pi.append(' }.\n')

            if len(preferences) > 0:
                Pi.append('%% Preferences\n')
                for prefName, prefExpression in [(p, parser.preferences[p]) for p in preferences]:
                    Pi.append(f'{prefName}\t:- {build_goal(prefExpression)}.\n')
                    if prefName in negative_preferences:
                        Pi.append(f'violated_{prefName}\t:- not {prefName}.\n')
        else:
            Pi.append('% empty\n')

        Pi.append('\n% Display\n')
        Pi.append('#show occ/2.\n')

        Pi.append('\n% Initial state\n')

        Pi.append('%% Fluents\n')
        for state in parser.state:
            Pi.append(f'{reprFluent(state, timeTerm="0")}.\n')
        if len(parser.state) == 0:
            Pi.append('% empty\n')

        Pi.append('%% Numeric Fluents\n')
        for name, data in parser.numeric_fluents.items():
            for params, value in data.items():
                fluent = tuple([name] + list(params) + [value])
                Pi.append(f'{reprFluent(fluent, timeTerm="0")}.\n')
        if len(parser.numeric_fluents) == 0:
            Pi.append('% empty\n')
        
        program = ''.join(Pi)

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
    Pi = translator.translate(domain, problem, timesteps)
    if Pi:
        filename = f'{problem}.lp'
        with open(filename, 'w') as f:
            f.write(Pi)
            logging.info('Logic program written into file %s.lp', problem)
    else:
        logging.error('Translation was not possible')
        exit(1)
    logging.info('Translator ended after ' + str(time.time() - start_time) + 's')
