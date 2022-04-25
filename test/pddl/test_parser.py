import unittest
import sys
import os
sys.path.append('.')

from src.pddl.parser import Parser
from src.pddl.action import Action
from src.pddl.utils import parse_hierarchy, parse_fluents

class TestPDDLParser(unittest.TestCase):

    def setUp(self):
        domain = os.path.join('examples', 'dinner', 'dinner.pddl')
        problem = os.path.join('examples', 'dinner', 'pb1.pddl')
        self.parser = Parser(domain, problem)

    def test_parse_domain(self):
        self.assertEqual(self.parser.domain_name, 'dinner')
        self.assertSetEqual(self.parser.requirements, set([':strips']))
        self.assertEqual(self.parser.predicates, {'clean': {}, 'dinner': {}, 'quiet': {}, 'present': {}, 'garbage': {}})
        self.assertEqual(self.parser.types, {})
        self.assertDictEqual(self.parser.actions[0].__dict__, Action('cook', [], ('clean',), ('dinner',)).__dict__)

    def test_parse_problem(self):
        def frozenset_of_tuples(data):
            return frozenset([tuple(t) for t in data])
        self.assertEqual(self.parser.problem_name, 'pb1')
        self.assertEqual(self.parser.objects, {})
        self.assertEqual(self.parser.state, frozenset_of_tuples([['garbage'],['clean'],['quiet']]))
        self.assertTupleEqual(self.parser.goal, ('and', [('dinner',), ('present',), ('not', ('garbage',))]))

    def test_parse_predicates(self):
        predicates = {}

        group = \
        [
            ['untyped_pred', '?v1', '?v2', '?v3'],
            ['typed_pred', '?v1', '-', 'type1', '?v2', '-', 'type1', '?v3', '-', 'object'],
            ['shared_type_pred', '?v1', '?v2', '-', 'type1', '?v3']
        ]

        parse_fluents(group, predicates, 'predicates')

        comp = \
        {
            'untyped_pred': {'?v1': 'object', '?v2': 'object', '?v3': 'object'},
            'typed_pred': {'?v1': 'type1', '?v2': 'type1', '?v3': 'object'},
            'shared_type_pred': {'?v1': 'type1', '?v2': 'type1', '?v3': 'object'}
        }

        self.assertEqual(predicates, comp)

    def test_parse_undefined_types(self):
        types = {}
        
        group = ['location', 'pile', 'robot', 'crane', 'container']

        parse_hierarchy(group, types, 'types', True)

        comp = {'object': ['location', 'pile', 'robot', 'crane', 'container']}

        self.assertEqual(types, comp)

    def test_parse_defined_types(self):
        types = {}

        group = \
        [
            'place', 'locatable', 'level', '-', 'object',
            'depot', 'market', '-', 'place',
            'truck', 'goods', '-', 'locatable'
        ]

        parse_hierarchy(group, types, 'types', True)

        comp = \
        {
            'object': ['place', 'locatable', 'level'],
            'place': ['depot', 'market'],
            'locatable': ['truck', 'goods']
        }

        self.assertEqual(types, comp)

    def test_parse_objects(self):
        types = {}
        objects = {}

        group = ['airplane', 'segment', 'direction', 'airplanetype', 'a']

        parse_hierarchy(group, types, 'types', True)
        
        group = \
        [
            'b', '-', 'a',
            'a', '-', 'a',
            'north', 'south', '-', 'direction',
            'light', 'medium', 'heavy', '-', 'airplanetype',
            'element1', '-', 'object',
            'seg_pp_0_60', 'seg_ppdoor_0_40', '-', 'segment',
            'airplane_CFBEG', '-', 'airplane',
            'element2'
        ]

        parse_hierarchy(group, objects, 'objects', False)

        self.assertDictEqual(objects, {
            'a': ['b', 'a'],
            'object': ['element1', 'element2'],
            'direction': ['north', 'south'],
            'airplanetype': ['light', 'medium', 'heavy'],
            'segment': ['seg_pp_0_60', 'seg_ppdoor_0_40'],
            'airplane': ['airplane_CFBEG']
        })

if __name__ == '__main__':
    unittest.main()
