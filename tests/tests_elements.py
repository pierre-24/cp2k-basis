import unittest

from cp2k_basis.elements import ElementSet


class ElementSetTestCase(unittest.TestCase):
    def test_create_element_set_ok(self):
        # single element
        eset = ElementSet.create('C')
        self.assertEqual(eset.elements, {6})
        self.assertEqual(list(eset), ['C'])

        # multiple elements
        eset = ElementSet.create('C,H,O,N')
        self.assertEqual(eset.elements, {1, 6, 7, 8})
        self.assertEqual(sorted(list(eset)), ['C', 'H', 'N', 'O'])

        # range
        self.assertEqual(ElementSet.create('H-Ne').elements, set(range(1, 11)))

        # range and element
        self.assertEqual(ElementSet.create('C-O,H,Fe').elements, {1, 6, 7, 8, 26})

        # numbers
        self.assertEqual(ElementSet.create('1,C,7').elements, {1, 6, 7})

        # range with number
        self.assertEqual(ElementSet.create('1-3,C').elements, {1, 2, 3, 6})

    def test_create_element_set_wrong_input_ko(self):
        with self.assertRaises(ValueError):  # wrong atom
            ElementSet.create('E')

        with self.assertRaises(ValueError):  # outside bounds
            ElementSet.create('115')

        with self.assertRaises(ValueError):  # wrong range
            ElementSet.create('C-H-N')

    def test_union_element_set_ok(self):
        self.assertEqual(ElementSet.create('C-O') | ElementSet.create('H'), ElementSet.create('H,C,N,O'))
        self.assertEqual(ElementSet.create('C-O') | '1', 'H,C,N,O')

    def test_intersect_element_set_ok(self):
        self.assertEqual(ElementSet.create('H-Ne') & ElementSet.create('C,O,Fe'), ElementSet.create('C,O'))
        self.assertEqual(ElementSet.create('H-Ne') & 'C,O,Fe', 'C,O')

    def test_sub_element_set_ok(self):
        self.assertEqual(ElementSet.create('H-Ne') - ElementSet.create('Li-O'), ElementSet.create('H,He,F,Ne'))
        self.assertEqual(ElementSet.create('H-Ne') - 'Li-O', 'H,He,F,Ne')

    def test_contains_element_set_ok(self):
        eset = ElementSet.create('H-Ne')
        self.assertIn('O', eset)
        self.assertNotIn('Fe', eset)
