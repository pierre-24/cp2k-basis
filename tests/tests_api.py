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

        self.assertEqual(data['query']['name'], self.basis_name)
        self.assertNotIn('elements', data['query'])

        for abs_ in AtomicBasisSetsParser(data['result']).iter_atomic_basis_sets():
            self.assertIn(
                abs_.symbol, flask.current_app.config['BASIS_SETS_STORAGE'][self.basis_name])

    def test_basis_data_wrong_basis_ko(self):
        response = self.client.get(flask.url_for('api.basis-data', name='xx'))
        self.assertEqual(response.status_code, 404)

    def test_basis_data_atom_ok(self):
        atoms = ['H']

        response = self.client.get(
            flask.url_for('api.basis-data', name=self.basis_name) + '?elements={}'.format(''.join(atoms)))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertIn('elements', data['query'])
        self.assertEqual(data['query']['elements'], atoms)

    def test_basis_data_wrong_atom_ko(self):
        response = self.client.get(flask.url_for('api.basis-data', name=self.basis_name) + '?elements=X')
        self.assertEqual(response.status_code, 422)

    def test_basis_data_missing_atom_ko(self):
        response = self.client.get(flask.url_for('api.basis-data', name=self.basis_name) + '?elements=U')
        self.assertEqual(response.status_code, 404)


class PseudopotentialAPITestCase(FlaskAppMixture):

    def setUp(self) -> None:
        super().setUp()

        self.pseudo_name = 'GTH-BLYP'

    def test_pseudo_data_ok(self):

        response = self.client.get(flask.url_for('api.pseudo-data', name=self.pseudo_name))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['query']['name'], self.pseudo_name)
        self.assertNotIn('elements', data['query'])

        for app in AtomicPseudopotentialsParser(data['result']).iter_atomic_pseudopotentials():
            self.assertIn(
                app.symbol, flask.current_app.config['PSEUDOPOTENTIALS_STORAGE'][self.pseudo_name])

    def test_pseudo_data_wrong_pseudo_ko(self):
        response = self.client.get(flask.url_for('api.pseudo-data', name='xx'))
        self.assertEqual(response.status_code, 404)

    def test_pseudo_data_atom_ok(self):
        atoms = ['H']

        response = self.client.get(
            flask.url_for('api.pseudo-data', name=self.pseudo_name) + '?elements={}'.format(''.join(atoms)))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertIn('elements', data['query'])
        self.assertEqual(data['query']['elements'], atoms)

    def test_pseudo_data_missing_atom_ko(self):
        response = self.client.get(flask.url_for('api.basis-data', name=self.pseudo_name) + '?elements=U')
        self.assertEqual(response.status_code, 404)
