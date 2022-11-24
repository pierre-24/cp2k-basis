import pathlib
from unittest import TestCase

from cp2k_basis_webservice import Config, create_app

from cp2k_basis.basis_set import AtomicBasisSetsParser
from cp2k_basis.pseudopotential import AtomicPseudopotentialsParser

import flask


class FlaskAppMixture(TestCase):
    def setUp(self) -> None:
        # config
        Config.LIBRARY = '{}/LIBRARY_EXAMPLE.h5'.format(pathlib.Path(__file__).parent)

        # create app
        self.app = create_app(False)
        self.app.config.update(
            TESTING=True
        )

        # push context
        self.app_context = self.app.app_context()
        self.app_context.push()

        # create client
        self.client = self.app.test_client(use_cookies=True)


class BasisSetAPITestCase(FlaskAppMixture):
    def setUp(self) -> None:
        super().setUp()

        self.basis_name = 'SZV-MOLOPT-GTH'

    def test_basis_data_ok(self):

        response = self.client.get(flask.url_for('api.basis-data', name=self.basis_name))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['request']['name'], self.basis_name)
        self.assertEqual(data['request']['atoms'], self.app.config['ATOMS_PER_BASIS_SET'][self.basis_name])

        basis_set = AtomicBasisSetsParser(data['result']).atomic_basis_sets()
        for symbol in data['request']['atoms']:
            self.assertIn(symbol, basis_set)

    def test_basis_data_wrong_basis_ko(self):
        response = self.client.get(flask.url_for('api.basis-data', name='xx'))
        self.assertEqual(response.status_code, 404)

    def test_basis_data_atom_ok(self):
        atoms = ['H']

        response = self.client.get(
            flask.url_for('api.basis-data', name=self.basis_name) + '?atoms={}'.format(''.join(atoms)))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['request']['atoms'], atoms)

    def test_basis_data_wrong_atom_ko(self):
        response = self.client.get(flask.url_for('api.basis-data', name=self.basis_name) + '?atoms=X')
        self.assertEqual(response.status_code, 422)

    def test_basis_data_missing_atom_ko(self):
        response = self.client.get(flask.url_for('api.basis-data', name=self.basis_name) + '?atoms=U')
        self.assertEqual(response.status_code, 404)


class PseudopotentialAPITestCase(FlaskAppMixture):
    def test_pseudo_data_ok(self):
        pseudo_name = 'GTH-BLYP'

        response = self.client.get(flask.url_for('api.pseudo-data', name=pseudo_name))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['request']['name'], pseudo_name)
        self.assertEqual(data['request']['atoms'], self.app.config['ATOMS_PER_PSEUDOPOTENTIAL'][pseudo_name])

        atomic_pseudopotentials = AtomicPseudopotentialsParser(data['result']).atomic_pseudopotentials()
        for symbol in data['request']['atoms']:
            self.assertIn(symbol, atomic_pseudopotentials)
