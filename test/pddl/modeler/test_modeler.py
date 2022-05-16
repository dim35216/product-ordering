import unittest
import subprocess
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

class TestModeler(unittest.TestCase):

    def setUp(self):
        self.filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.pddl')
        self.modeler_py = os.path.join('src', 'pddl', 'modeler', 'modeler.py')
        if os.path.exists(self.filename):
            os.remove(self.filename)
        self.assertTrue(os.path.exists(self.modeler_py))


    def test_main(self):
        comparison_filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'comparison.pddl')
        self.assertTrue(os.path.exists(comparison_filename))
        products = ['23545', '12020', '12021', '23547']
        subprocess.run(args=['python', self.modeler_py, self.filename,
        '-p'] + products)
        self.assertTrue(os.path.exists(self.filename))

        with open(self.filename, 'r') as f:
            content = f.readlines()
            
            with open(comparison_filename, 'r') as c:
                comparison_content = c.readlines()

                self.assertEqual(len(content), len(comparison_content))
                for i in range(len(content)):
                    self.assertEqual(content[i], comparison_content[i])

if __name__ == '__main__':
    unittest.main()
