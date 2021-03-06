import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')))
from src.experiment.approaches.pddl_solver import interpret_sas_plan

class TestUtils(unittest.TestCase):

    def test_interpret_sas_plan(self):
        filename = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sas_plan'))

        with open(filename, 'r') as filehandle:
            cmd_output = filehandle.read()

            opt_value, order = interpret_sas_plan(cmd_output)

            self.assertEqual(opt_value, 17)
            self.assertEqual(order, ['20001', '10014', '10012', '50013'])

if __name__ == '__main__':
    unittest.main()
