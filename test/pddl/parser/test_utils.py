import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')))
from src.pddl.parser.utils import scan_tokens

class TestUtils(unittest.TestCase):

    def test_scan_tokens_tc1(self):
        """ TestCase 1
        """
        filename = os.path.join('test', 'pddl', 'parser', 'domain.pddl')

        tokens = scan_tokens(filename)

        comp = \
        ['define', ['domain', 'test'],
            [':requirements', ':typing', ':adl', ':preferences'],
            [':types', 'level', 'molecule', '-', 'object', 'simple', 'complex', '-', 'molecule'],
            [':predicates',
                ['association-reaction', '?x1', '?x2', '-', 'molecule', '?x3', '-', 'complex'],
                ['synthesis-reaction', '?x1', '?x2', '-', 'molecule'],
                ['catalyzed-association-reaction', '?x1', '?x2', '-', 'molecule', '?x3', '-', 'complex'],
                ['possible', '?s', '-', 'molecule'], ['available', '?s', '-', 'molecule'],
                ['next', '?l1', '?l2', '-', 'level'],
                ['num-subs', '?l', '-', 'level'],
                ['chosen', '?s', '-', 'simple']
            ],
            [':action', 'choose',
                ':parameters', ['?x', '-', 'simple', '?l1', '?l2', '-', 'level'],
                ':precondition', ['and', ['possible', '?x'], ['not', ['chosen', '?x']], ['num-subs', '?l2'], ['next', '?l1', '?l2']],
                ':effect', ['and', ['chosen', '?x'], ['not', ['num-subs', '?l2']], ['num-subs', '?l1']]
            ],
            [':action', 'initialize',
                ':parameters', ['?x', '-', 'simple'],
                ':precondition', ['and', ['chosen', '?x']], ':effect', ['and', ['available', '?x']]
            ],
            [':action', 'associate',
                ':parameters', ['?x1', '?x2', '-', 'molecule', '?x3', '-', 'complex'],
                ':precondition', ['and', ['association-reaction', '?x1', '?x2', '?x3'], ['available', '?x1'], ['available', '?x2']],
                ':effect', ['and', ['not', ['available', '?x1']], ['not', ['available', '?x2']], ['available', '?x3']]
            ],
            [':action', 'associate-with-catalyze',
                ':parameters', ['?x1', '?x2', '-', 'molecule', '?x3', '-', 'complex'],
                ':precondition', ['and', ['catalyzed-association-reaction', '?x1', '?x2', '?x3'], ['available', '?x1'], ['available', '?x2']],
                ':effect', ['and', ['not', ['available', '?x1']], ['available', '?x3']]
            ],
            [':action', 'synthesize',
                ':parameters', ['?x1', '?x2', '-', 'molecule'],
                ':precondition', ['and', ['synthesis-reaction', '?x1', '?x2'], ['available', '?x1']],
                ':effect', ['and', ['available', '?x2']]
            ]
        ]

        self.assertEqual(tokens, comp)

    def test_scan_tokens_tc2(self):
        """ TestCase 2
        """
        filename = os.path.join('examples', 'dinner', 'dinner.pddl')

        tokens = scan_tokens(filename)

        comp = \
        ['define', ['domain', 'dinner'],
            [':requirements', ':strips'],
            [':predicates', ['clean'], ['dinner'], ['quiet'], ['present'], ['garbage']],
            [':action', 'cook',
                ':precondition', ['clean'],
                ':effect', ['dinner']
            ],
            [':action', 'wrap',
                ':precondition', ['quiet'],
                ':effect', ['present']
            ],
            [':action', 'carry',
                ':precondition', ['garbage'],
                ':effect', ['and', ['not', ['garbage']], ['not', ['clean']]]
            ],
            [':action', 'dolly',
                ':precondition', ['garbage'],
                ':effect', ['and', ['not', ['garbage']], ['not', ['quiet']]]
            ]
        ]

        self.assertEqual(tokens, comp)

    def test_scan_tokens_tc3(self):
        """ TestCase 3
        """
        filename = os.path.join('examples', 'dinner', 'pb1.pddl')

        tokens = scan_tokens(filename)

        comp = \
        ['define', ['problem', 'pb1'],
            [':domain', 'dinner'],
            [':init', ['garbage'], ['clean'], ['quiet']],
            [':goal', ['and', ['dinner'], ['present'], ['not', ['garbage']]]]
        ]

        self.assertEqual(tokens, comp)

if __name__ == '__main__':
    unittest.main()
