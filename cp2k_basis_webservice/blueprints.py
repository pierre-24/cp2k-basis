import json

import flask
from flask.views import MethodView
from flask.blueprints import Blueprint
from werkzeug.exceptions import NotFound

from webargs import fields
from webargs.flaskparser import FlaskParser

import cp2k_basis
from cp2k_basis.elements import ElementSetField, Z_TO_SYMB
from cp2k_basis.base_objects import Storage


class RenderTemplateView(MethodView):
    methods = ['GET']
    template_name = None

    def get_context_data(self, **kwargs):
        return {}

    def get(self, **kwargs):
        """Handle GET: render template"""

        if not self.template_name:
            raise ValueError('template_name')

        context_data = self.get_context_data(**kwargs)
        return flask.render_template(self.template_name, **context_data)


# ----
visitor_blueprint = Blueprint('visitor', __name__)


class IndexView(RenderTemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx.update(
            site_name=cp2k_basis.__name__,
            site_version=cp2k_basis.__version__,
            z_to_symb=Z_TO_SYMB,
            bs_per_name=json.dumps(flask.current_app.config['BASIS_SETS_STORAGE'].elements_per_family),
            pp_per_name=json.dumps(flask.current_app.config['PSEUDOPOTENTIALS_STORAGE'].elements_per_family),
        )

        return ctx


visitor_blueprint.add_url_rule('/', view_func=IndexView.as_view(name='index'))

# ----
api_blueprint = Blueprint('api', __name__, url_prefix='/api')


@api_blueprint.errorhandler(422)
def handle_error(err):
    headers = err.data.get('headers', None)
    messages = err.data.get('messages', ['Invalid request.'])
    data = {'status': err.code, 'message': 'Error while handling parameters', 'errors': messages}
    if headers:
        return flask.jsonify(data), err.code, headers
    else:
        return flask.jsonify(data), err.code


@api_blueprint.errorhandler(401)
@api_blueprint.errorhandler(403)
@api_blueprint.errorhandler(404)
def handle_error_s(err):
    return flask.jsonify(status=err.code, message=err.description), err.code


field_elements = ElementSetField()
field_name = fields.Str()

parser = FlaskParser()


class AllDataAPI(MethodView):
    def get(self, **kwargs):
        bs_storage: Storage = flask.current_app.config['BASIS_SETS_STORAGE']
        pp_storage: Storage = flask.current_app.config['PSEUDOPOTENTIALS_STORAGE']

        return flask.jsonify(
            query=dict(type='ALL'),
            result=dict(
                basis_sets=dict(
                    per_name=bs_storage.elements_per_family, per_element=bs_storage.families_per_element),
                pseudopotentials=dict(
                    per_name=pp_storage.elements_per_family, per_element=pp_storage.families_per_element)
            )
        )


api_blueprint.add_url_rule('/data', view_func=AllDataAPI.as_view(name='data'))


class NamesAPI(MethodView):
    @parser.use_kwargs({'elements': field_elements}, location='query')
    def get(self, **kwargs):
        bs_storage: Storage = flask.current_app.config['BASIS_SETS_STORAGE']
        pp_storage: Storage = flask.current_app.config['PSEUDOPOTENTIALS_STORAGE']

        elements = kwargs.get('elements', None)

        query = dict(type='ALL')

        if elements:
            query['elements'] = list(elements)

        return flask.jsonify(
            query=query,
            result=dict(
                basis_sets=bs_storage.get_names_for_elements(elements),
                pseudopotentials=pp_storage.get_names_for_elements(elements)
            )
        )


api_blueprint.add_url_rule('/names', view_func=NamesAPI.as_view(name='names'))


class BaseFamilyStorageDataAPI(MethodView):
    source: str = ''
    textual_source: str = ''

    @parser.use_kwargs({'name': field_name}, location='view_args')
    @parser.use_kwargs({'elements': field_elements}, location='query')
    def get(self, **kwargs):
        storage: Storage = flask.current_app.config['{}S_STORAGE'.format(self.source)]

        elements = kwargs.get('elements', None)
        name = kwargs.get('name')

        try:
            family_storage = storage[name]
        except KeyError:
            raise NotFound('{} `{}` does not exist'.format(self.textual_source, name))

        if not elements:
            atomic_data_objects = list(family_storage.values())
        else:
            atomic_data_objects = []
            for symbol in elements:
                try:
                    atomic_data_objects.append(family_storage[symbol])
                except KeyError:
                    raise NotFound('{} `{}` does not exist for atom {}'.format(self.textual_source, name, symbol))

        query = dict(type=self.source, name=name)
        result = dict(
            data=''.join(str(obj) for obj in atomic_data_objects),
            elements=list(obj.symbol for obj in atomic_data_objects),
            alternate_names=dict(
                (obj.symbol, list(filter(lambda x: x != name, obj.names))) for obj in atomic_data_objects),
            metadata=family_storage.metadata
        )

        if elements:
            query['elements'] = list(elements)

        return flask.jsonify(
            query=query,
            result=result
        )


class BasisSetDataAPI(BaseFamilyStorageDataAPI):
    source = 'BASIS_SET'
    textual_source = 'basis set'


api_blueprint.add_url_rule('/basis/<name>/data', view_func=BasisSetDataAPI.as_view(name='basis-data'))


class PseudopotentialDataAPI(BaseFamilyStorageDataAPI):
    source = 'PSEUDOPOTENTIAL'
    textual_source = 'pseudopotential'


api_blueprint.add_url_rule(
    '/pseudopotentials/<name>/data', view_func=PseudopotentialDataAPI.as_view(name='pseudo-data'))


class BaseMetadataAPI(MethodView):
    source: str = ''
    textual_source: str = ''

    @parser.use_kwargs({'name': field_name}, location='view_args')
    def get(self, **kwargs):
        storage: Storage = flask.current_app.config['{}S_STORAGE'.format(self.source)]
        name = kwargs.get('name')

        try:
            family_storage = storage[name]
        except KeyError:
            raise NotFound('{} `{}` does not exist'.format(self.textual_source, name))

        query = dict(type=self.source, name=name)
        result = family_storage.metadata
        result['elements'] = list(family_storage.data_objects.keys())

        return flask.jsonify(
            query=query,
            result=result
        )


class BasisSetMetadataAPI(BaseMetadataAPI):
    source = 'BASIS_SET'
    textual_source = 'basis set'


api_blueprint.add_url_rule('/basis/<name>/metadata', view_func=BasisSetMetadataAPI.as_view(name='basis-metadata'))


class PseudopotentialMetadataAPI(BaseMetadataAPI):
    source = 'PSEUDOPOTENTIAL'
    textual_source = 'pseudopotential'


api_blueprint.add_url_rule(
    '/pseudopotentials/<name>/metadata', view_func=PseudopotentialMetadataAPI.as_view(name='pseudo-metadata'))
