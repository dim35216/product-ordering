from typing import List


class Action:
    """Auxiliary class representing an action used in parsing
    and translating PDDL planning problems
    """

    def __init__(self, name : str, parameters : List[List[str]], preconditions : tuple,
                 effects : tuple):
        """Constructor of a PDDL action, which is given in
        STRIPS-like notation with parameters, preconditions and
        effects

        Args:
            name (str): descriptive name of the action
            parameters (List[List[str]]): list of parameters
            preconditions (tuple): list of preconditions
            effects (tuple): list of effects
        """
        self.name = name
        self.parameters = parameters
        self.preconditions = preconditions
        self.effects = effects

    def __repr__(self):
        """Overwritten objects method for string representation

        Returns:
            str: string representation
        """
        return 'action: ' + self.name + \
        '\n  parameters: ' + str(self.parameters) + \
        '\n  preconditions: ' + str(self.preconditions) + \
        '\n  effects: ' + str(self.effects) + '\n'

    def repr_asp_term(self):
        """Get representation of action as ASP term

        Returns:
            str: ASP term
        """
        term = str(self.name).replace('-', '_')
        if self.parameters:
            term += '('
            for var, _ in self.parameters:
                assert var[0] == '?'
                term += var[1:].capitalize() + ', '
            term = term[:-2] + ')'
        return term

    def repr_parameters(self, sep : str = ',', leading_sep : bool = True) -> str:
        """Get list of parameters as string

        Args:
            sep (str, optional): separation char. Defaults to ','.
            leading_sep (bool, optional): add an additional separation char at the beginning. Defaults to True.

        Returns:
            str: string listing all parameters, divided by the separation char
        """
        result = ''
        first = True
        for var, typ in self.parameters:
            assert var[0] == '?'
            if not first or leading_sep:
                result += sep + ' '
            first = False
            result += f'{typ.lower()}({var[1:].capitalize()})'
        return result
