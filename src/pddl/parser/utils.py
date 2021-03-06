import re
from typing import FrozenSet, List, Dict, Union, Tuple

def frozenset_of_tuples(data : set) -> FrozenSet[tuple]:
    """Auxiliary function for constructing a frozenset (immutable set) of tuples (immutable list)

    Args:
        data (set): input data

    Returns:
        FrozenSet[tuple]: resulting frozenset of tuples
    """
    return frozenset([tuple(token) for token in data])

def scan_tokens(filename : str) -> Union[str, list]:
    """Scan tokens for a PDDL domain or problem instance file

    Args:
        filename (str): path to PDDL file

    Returns:
        Union[str, list]: hierarchied list of tokens extracted from the PDDL file
    """
    with open(filename) as filehandle:
        # Remove single line comments
        content = re.sub(r';.*$', '', filehandle.read(), flags=re.MULTILINE).lower()
    # Tokenize
    stack = []
    tokens : List[Union[str, list]] = []
    for token in re.findall(r'[()]|\"[^()"]+\"|[^\s()]+', content):
        if token == '(':
            stack.append(tokens)
            tokens = []
        elif token == ')':
            if stack:
                temp = tokens
                tokens = stack.pop()
                tokens.append(temp)
            else:
                raise Exception('Missing open parentheses')
        else:
            tokens.append(token)
    if stack:
        raise Exception('Missing close parentheses')
    if len(tokens) != 1:
        raise Exception('Malformed expression')
    return tokens[0]

def parse_hierarchy(group : list, structure : Dict[str, List], name : str, redefine : bool) -> None:
    """Parse object hierarchy of PDDL tokens and write back into the given structure file

    Args:
        group (list): hierarchied list of PDDL tokens
        structure (Dict[str, List]): PDDL structure element
        name (str): name of structure
        redefine (bool): permit and throw exception for redefinition of elements within structure
    """
    objects : List[str] = []
    while group:
        if redefine and group[0] in structure:
            raise Exception('Redefined supertype of ' + group[0])
        if group[0] == '-':
            if not objects:
                raise Exception('Unexpected hyphen in ' + name)
            group.pop(0)
            typ = group.pop(0)
            if not typ in structure:
                structure[typ] = []
            structure[typ] += objects
            objects = []
        else:
            objects.append(group.pop(0))
    if not 'object' in structure:
        structure['object'] = []
    structure['object'] += objects

def parse_fluents(group : list, structure : Dict[str, dict], name : str) -> None:
    """Parse fluents

    Args:
        group (list): hierarchied list of PDDL tokens
        structure (Dict[str, dict]): PDDL structure element
        name (str): name of structure
    """
    for pred in group:
        predicate_name = pred.pop(0)
        if predicate_name in structure:
            raise Exception('Predicate ' + predicate_name + ' redefined')
        arguments = {}
        untyped_variables : List[str] = []
        while pred:
            token = pred.pop(0)
            if token == '-':
                if not untyped_variables:
                    raise Exception('Unexpected hyphen in ' + name)
                typ = pred.pop(0)
                while untyped_variables:
                    arguments[untyped_variables.pop(0)] = typ
            else:
                untyped_variables.append(token)
        while untyped_variables:
            arguments[untyped_variables.pop(0)] = 'object'
        structure[predicate_name] = arguments

def parse_goal(group : list) -> Tuple[tuple, Dict[str, tuple]]:
    """Parse goal representation

    Args:
        group (list): hierarchied list of tokens extracted from the PDDL problem instance file

    Returns:
        Tuple[tuple, Dict[str, dict]]: goal representation and preferences list
    """
    goal : tuple = ('and', [])
    preferences : Dict[str, tuple] = {}
    if not isinstance(group, list):
        raise Exception('Error with goal')

    if len(group) == 0:
        return goal, preferences

    if group[0] == 'and':
        if len(group) <= 1:
            raise Exception('Unexpected and in goal')
        predicates = []
        for token in group[1:]:
            if isinstance(token, list) and len(token) > 0 and token[0] == 'preference':
                if len(token) != 3:
                    raise Exception('Unexpected preference in goal')
                preferences[token[1]] = split_predicates(token[2], '', 'preference')
            else:
                predicates.append(split_predicates(token, '', 'goal'))
        goal = tuple(['and', predicates])

    else:
        goal = split_predicates(group, '', 'goal')

    return goal, preferences

def split_predicates(group : list, name : str, part : str) -> tuple:
    """Split and parse list of PDDL predicates

    Args:
        group (list): hierarchied list of PDDL tokens
        name (str): name of action if given
        part (str): name of predicates list / structure element

    Returns:
        tuple: tuple representing the hierarchy of PDDL predicates
    """
    result = None
    if not isinstance(group, list) or len(group) == 0:
        raise Exception('Error with ' + name + part)

    if group[0] == 'and':
        if len(group) <= 1:
            raise Exception('Unexpected and in ' + name + part)
        predicates = []
        for predicate in group[1:]:
            predicates.append(split_predicates(predicate, name, part))
        result = tuple(['and', predicates])

    elif group[0] == 'or':
        if len(group) <= 2:
            raise Exception('Unexpected or in ' + name + part)
        predicates = []
        for predicate in group[1:]:
            predicates.append(split_predicates(predicate, name, part))
        result = tuple(['or', predicates])

    elif group[0] == 'not':
        if len(group) != 2:
            raise Exception('Unexpected not in ' + name + part)
        result = tuple(['not', split_predicates(group[1], name, part)])

    elif group[0] == '=':
        if len(group) != 3:
            raise Exception('Unexpected = in ' + name + part)
        element1 = split_predicates(group[1], name, part)
        element2 = split_predicates(group[2], name, part)
        result = tuple(['=', element1, element2])

    elif group[0] in ['<', '+', 'assign']:
        if len(group) != 3:
            raise Exception('Unexpected ' + group[0] + ' in ' + name + part)
        assert isinstance(group[1], list)
        element1 = split_predicates(group[1], name, part)
        if isinstance(group[2], list):
            element2 = split_predicates(group[2], name, part)
        else:
            element2 = group[2]
        result = tuple([group[0], element1, element2])

    elif group[0] == 'preferences':
        raise Exception('Unexpected preferences in ' + name + part)

    else:
        result = tuple(group)

    return result
