import pathlib
from unittest import TestCase

from cp2k_basis.elements import ElementSet
from cp2k_basis_webservice import Config, create_app

from cp2k_basis.basis_set import AtomicBasisSetsParser
from cp2k_basis.pseudopotential import AtomicPseudopotentialsParser

import flask

from tests import BaseDataObjectMixin


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

        self.bs_storage = flask.current_app.config['BASIS_SETS_STORAGE']
        self.pp_storage = flask.current_app.config['PSEUDOPOTENTIALS_STORAGE']

    def test_data_ok(self):

        response = self.client.get(flask.url_for('api.data'))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['query']['type'], 'ALL')

        self.assertEqual(
            data['result']['basis_sets']['elements'],
            self.bs_storage.elements_per_family
        )

        self.assertEqual(
            data['result']['basis_sets']['tags'],
            dict((n, self.bs_storage[n].metadata['tags']) for n in self.bs_storage
                 if 'tags' in self.bs_storage[n].metadata)
        )

        self.assertEqual(
            data['result']['pseudopotentials']['elements'],
            self.pp_storage.elements_per_family
        )

        self.assertEqual(
            data['result']['pseudopotentials']['tags'],
            dict((n, self.pp_storage[n].metadata['tags']) for n in self.pp_storage
                 if 'tags' in self.pp_storage[n].metadata)
        )

    def test_names_no_elements_ok(self):
        response = self.client.get(flask.url_for('api.names'))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['query']['type'], 'ALL')
        self.assertNotIn('elements', data['query'])

        self.assertEqual(data['result']['basis_sets'], list(self.bs_storage))
        self.assertEqual(data['result']['pseudopotentials'], list(self.pp_storage))

    def test_names_with_elements_ok(self):
        elements = 'O,Ne'
        response = self.client.get(flask.url_for('api.names') + '?elements={}'.format(elements))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['query']['type'], 'ALL')
        self.assertEqual(sorted(data['query']['elements']), sorted(elements.split(',')))

        self.assertEqual(data['result']['basis_sets'], [])
        self.assertEqual(data['result']['pseudopotentials'], ['GTH-BLYP'])

    def test_names_with_name_ok(self):
        name = 'molopt'
        response = self.client.get(flask.url_for('api.names') + '?bs_name={}'.format(name))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['query']['type'], 'ALL')

        self.assertEqual(
            data['result']['basis_sets'],
            list(k for k in self.bs_storage if name in k.lower())
        )

    def test_names_with_tag_ok(self):
        tag = 'molopt'
        response = self.client.get(flask.url_for('api.names') + '?bs_tag={}'.format(tag))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['query']['type'], 'ALL')

        self.assertEqual(
            data['result']['basis_sets'],
            list(k for k in self.bs_storage.tags_per_family if tag in self.bs_storage.tags_per_family[k])
        )


class BasisSetAPITestCase(FlaskAppMixture, BaseDataObjectMixin):
    def setUp(self) -> None:
        super().setUp()
        self.basis_name = 'SZV-MOLOPT-GTH'

    def test_basis_data_ok(self):

        response = self.client.get(flask.url_for('api.basis-data', name=self.basis_name))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['query']['name'], self.basis_name)
        self.assertNotIn('elements', data['query'])

        basis_set = flask.current_app.config['BASIS_SETS_STORAGE'][self.basis_name]

        for abs_ in AtomicBasisSetsParser(data['result']['data']).iter_atomic_basis_set_variants():
            self.assertIn(abs_.symbol, basis_set)
            self.assertAtomicBasisSetEqual(abs_, basis_set[abs_.symbol]['q1' if abs_.symbol == 'H' else 'q4'])

        self.assertEqual(sorted(data['result']['elements']), sorted(basis_set))
        self.assertEqual(data['result']['metadata'], basis_set.metadata)

        variants = {}
        for symbol in data['result']['elements']:
            variants[symbol] = dict(
                (v, basis_set[symbol][v].preferred_name(self.basis_name, v)) for v in basis_set[symbol])

        self.assertEqual(data['result']['variants'], variants)

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
            data['result']['references'],
            flask.current_app.config['BASIS_SETS_STORAGE'][self.basis_name].metadata['references']
        )

        self.assertEqual(
            data['result']['elements'],
            sorted(flask.current_app.config['BASIS_SETS_STORAGE'][self.basis_name].data_objects.keys())
        )

        self.assertEqual(
            data['result']['tags'],
            flask.current_app.config['BASIS_SETS_STORAGE'][self.basis_name].metadata['tags']
        )

    def test_basis_metadata_wrong_basis_ko(self):

        response = self.client.get(flask.url_for('api.basis-metadata', name='x'))
        self.assertEqual(response.status_code, 404)


class PseudopotentialAPITestCase(FlaskAppMixture, BaseDataObjectMixin):

    def setUp(self) -> None:
        super().setUp()

        self.pseudo_name = 'GTH-BLYP'

    def test_pseudo_data_ok(self):

        response = self.client.get(flask.url_for('api.pseudo-data', name=self.pseudo_name))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['query']['name'], self.pseudo_name)
        self.assertNotIn('elements', data['query'])

        pseudo_family = flask.current_app.config['PSEUDOPOTENTIALS_STORAGE'][self.pseudo_name]

        for app in AtomicPseudopotentialsParser(data['result']['data']).iter_atomic_pseudopotential_variants():
            self.assertIn(app.symbol, pseudo_family)
            self.assertAtomicPseudoEqual(app, pseudo_family[app.symbol]['q{}'.format(sum(app.nelec))])

        self.assertEqual(sorted(data['result']['elements']), sorted(pseudo_family))
        self.assertEqual(data['result']['metadata'], pseudo_family.metadata)

        variants = {}
        for symbol in data['result']['elements']:
            variants[symbol] = dict(
                (v, pseudo_family[symbol][v].preferred_name(self.pseudo_name, v)) for v in pseudo_family[symbol])

        self.assertEqual(data['result']['variants'], variants)

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
            data['result']['references'],
            flask.current_app.config['PSEUDOPOTENTIALS_STORAGE'][self.pseudo_name].metadata['references']
        )

        self.assertEqual(
            data['result']['elements'],
            sorted(flask.current_app.config['PSEUDOPOTENTIALS_STORAGE'][self.pseudo_name].data_objects.keys())
        )

        self.assertEqual(
            data['result']['tags'],
            flask.current_app.config['PSEUDOPOTENTIALS_STORAGE'][self.pseudo_name].metadata['tags']
        )
