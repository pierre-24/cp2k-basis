import pathlib
from unittest import TestCase

from cp2k_basis.elements import ElementSet
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


class GeneralAPITestCase(FlaskAppMixture):
    def setUp(self) -> None:
        super().setUp()

    def test_data_ok(self):

        response = self.client.get(flask.url_for('api.data'))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['query']['type'], 'ALL')

        self.assertEqual(
            data['result']['basis_sets']['per_name'],
            flask.current_app.config['BASIS_SETS_STORAGE'].elements_per_family
        )

        self.assertEqual(
            data['result']['basis_sets']['per_element'],
            flask.current_app.config['BASIS_SETS_STORAGE'].families_per_element
        )

        self.assertEqual(
            data['result']['pseudopotentials']['per_name'],
            flask.current_app.config['PSEUDOPOTENTIALS_STORAGE'].elements_per_family
        )

        self.assertEqual(
            data['result']['pseudopotentials']['per_element'],
            flask.current_app.config['PSEUDOPOTENTIALS_STORAGE'].families_per_element
        )

    def test_names_no_elements_ok(self):
        response = self.client.get(flask.url_for('api.names'))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['query']['type'], 'ALL')
        self.assertNotIn('elements', data['query'])

        self.assertEqual(data['result']['basis_sets'], list(flask.current_app.config['BASIS_SETS_STORAGE']))
        self.assertEqual(data['result']['pseudopotentials'], list(flask.current_app.config['PSEUDOPOTENTIALS_STORAGE']))

    def test_names_with_elements_ok(self):
        elements = 'O,Ne'
        response = self.client.get(flask.url_for('api.names') + '?elements={}'.format(elements))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['query']['type'], 'ALL')
        self.assertEqual(sorted(data['query']['elements']), sorted(elements.split(',')))

        self.assertEqual(data['result']['basis_sets'], [])
        self.assertEqual(data['result']['pseudopotentials'], ['GTH-BLYP'])


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

        for abs_ in AtomicBasisSetsParser(data['result']['data']).iter_atomic_basis_set_variants():
            self.assertIn(
                abs_.symbol, flask.current_app.config['BASIS_SETS_STORAGE'][self.basis_name])

        self.assertEqual(
            sorted(data['result']['elements']),
            sorted(flask.current_app.config['BASIS_SETS_STORAGE'][self.basis_name])
        )

        self.assertEqual(
            data['result']['alternate_names'],
            dict(
                (d.symbol, list(filter(lambda x: x != self.basis_name, d.names)))
                for d in flask.current_app.config['BASIS_SETS_STORAGE'][self.basis_name].data_objects.values()
            )
        )

        self.assertEqual(
            data['result']['metadata'],
            flask.current_app.config['BASIS_SETS_STORAGE'][self.basis_name].metadata
        )

    def test_basis_data_wrong_basis_ko(self):
        response = self.client.get(flask.url_for('api.basis-data', name='xx'))
        self.assertEqual(response.status_code, 404)

    def test_basis_data_atom_ok(self):
        elements = 'H'

        response = self.client.get(
            flask.url_for('api.basis-data', name=self.basis_name) + '?elements={}'.format(elements))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertIn('elements', data['query'])
        self.assertEqual(data['query']['elements'], elements.split(','))
        self.assertEqual(data['result']['elements'], elements.split(','))

    def test_basis_data_wrong_atom_ko(self):
        response = self.client.get(flask.url_for('api.basis-data', name=self.basis_name) + '?elements=X')
        self.assertEqual(response.status_code, 422)

    def test_basis_data_missing_atom_ko(self):
        response = self.client.get(flask.url_for('api.basis-data', name=self.basis_name) + '?elements=U')
        self.assertEqual(response.status_code, 404)

    def test_basis_metadata_ok(self):

        response = self.client.get(flask.url_for('api.basis-metadata', name=self.basis_name))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['query']['name'], self.basis_name)

        self.assertEqual(
            data['result']['description'],
            flask.current_app.config['BASIS_SETS_STORAGE'][self.basis_name].metadata['description']
        )

        self.assertEqual(
            data['result']['source'],
            flask.current_app.config['BASIS_SETS_STORAGE'][self.basis_name].metadata['source']
        )

        self.assertEqual(
            data['result']['references'],
            flask.current_app.config['BASIS_SETS_STORAGE'][self.basis_name].metadata['references']
        )

        self.assertEqual(
            data['result']['elements'],
            sorted(flask.current_app.config['BASIS_SETS_STORAGE'][self.basis_name].data_objects.keys())
        )

    def test_basis_metadata_wrong_basis_ko(self):

        response = self.client.get(flask.url_for('api.basis-metadata', name='x'))
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

        for app in AtomicPseudopotentialsParser(data['result']['data']).iter_atomic_pseudopotentials():
            self.assertIn(
                app.symbol, flask.current_app.config['PSEUDOPOTENTIALS_STORAGE'][self.pseudo_name])

        self.assertEqual(
            sorted(data['result']['elements']),
            sorted(flask.current_app.config['PSEUDOPOTENTIALS_STORAGE'][self.pseudo_name])
        )

        self.assertEqual(
            data['result']['alternate_names'],
            dict(
                (d.symbol, list(filter(lambda x: x != self.pseudo_name, d.names)))
                for d in flask.current_app.config['PSEUDOPOTENTIALS_STORAGE'][self.pseudo_name].data_objects.values()
            )
        )

        self.assertEqual(
            data['result']['metadata'],
            flask.current_app.config['PSEUDOPOTENTIALS_STORAGE'][self.pseudo_name].metadata
        )

    def test_pseudo_data_wrong_pseudo_ko(self):
        response = self.client.get(flask.url_for('api.pseudo-data', name='xx'))
        self.assertEqual(response.status_code, 404)

    def test_pseudo_data_atom_ok(self):
        elements = 'H,C-O'

        response = self.client.get(
            flask.url_for('api.pseudo-data', name=self.pseudo_name) + '?elements={}'.format(elements))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertIn('elements', data['query'])
        self.assertEqual(data['query']['elements'], list(ElementSet.create(elements).iter_sorted()))
        self.assertEqual(data['result']['elements'], list(ElementSet.create(elements).iter_sorted()))

    def test_pseudo_data_missing_atom_ko(self):
        response = self.client.get(flask.url_for('api.basis-data', name=self.pseudo_name) + '?elements=U')
        self.assertEqual(response.status_code, 404)

    def test_pseudo_metadata_ok(self):

        response = self.client.get(flask.url_for('api.pseudo-metadata', name=self.pseudo_name))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['query']['name'], self.pseudo_name)

        self.assertEqual(
            data['result']['description'],
            flask.current_app.config['PSEUDOPOTENTIALS_STORAGE'][self.pseudo_name].metadata['description']
        )

        self.assertEqual(
            data['result']['source'],
            flask.current_app.config['PSEUDOPOTENTIALS_STORAGE'][self.pseudo_name].metadata['source']
        )

        self.assertEqual(
            data['result']['references'],
            flask.current_app.config['PSEUDOPOTENTIALS_STORAGE'][self.pseudo_name].metadata['references']
        )

        self.assertEqual(
            data['result']['elements'],
            sorted(flask.current_app.config['PSEUDOPOTENTIALS_STORAGE'][self.pseudo_name].data_objects.keys())
        )
