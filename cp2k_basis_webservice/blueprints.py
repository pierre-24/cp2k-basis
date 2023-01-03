import datetime
import json

import flask
from flask.views import MethodView
from flask.blueprints import Blueprint
from werkzeug.exceptions import NotFound

from webargs import fields
from webargs.flaskparser import FlaskParser

from cp2k_basis.elements import ElementSetField, Z_TO_SYMB
from cp2k_basis.base_objects import Storage
from cp2k_basis_webservice import limiter, Config


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

    def __init__(self):
        super().__init__()

        self.bs_storage = flask.current_app.config['BASIS_SETS_STORAGE']
        self.pp_storage = flask.current_app.config['PSEUDOPOTENTIALS_STORAGE']

        # separate orb and aux basis sets
        self.orb_basis = {'elements': {}, 'tags': {}}
        self.aux_basis = {'elements': {}, 'tags': {}, 'type': {}}

        for name in self.bs_storage:
            if self.bs_storage[name].metadata.get('basis_type', 'ORB') != 'ORB':
                b = self.aux_basis
                b['type'][name] = self.bs_storage[name].metadata.get('basis_type', 'ORB')
            else:
                b = self.orb_basis

            b['elements'][name] = self.bs_storage.elements_per_family[name]
            b['tags'][name] = self.bs_storage.tags_per_family[name]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        from cp2k_basis_webservice import COMMON_CONTEXT
        ctx.update(**COMMON_CONTEXT)

        aux_basis = []
        for name in flask.current_app.config['BASIS_SETS_STORAGE']:
            if self.bs_storage[name].metadata.get('basis_type', 'ORB') != 'ORB':
                aux_basis.append(name)

        ctx.update(
            z_to_symb=Z_TO_SYMB,
            orb_basis_sets=self.orb_basis,
            aux_basis_sets=self.aux_basis,
            pseudopotentials=dict(
                elements=json.dumps(self.pp_storage.elements_per_family),
                tags=json.dumps(self.pp_storage.tags_per_family),
            )
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
    decorators = [limiter.limit(Config.API_LIMIT)]

    def get(self, **kwargs):
        bs_storage: Storage = flask.current_app.config['BASIS_SETS_STORAGE']
        pp_storage: Storage = flask.current_app.config['PSEUDOPOTENTIALS_STORAGE']

        return flask.jsonify(
            query=dict(type='ALL'),
            result=dict(
                basis_sets=dict(
                    elements=bs_storage.elements_per_family,
                    tags=bs_storage.tags_per_family,
                    build_date=bs_storage.date_build
                ),
                pseudopotentials=dict(
                    elements=pp_storage.elements_per_family,
                    tags=pp_storage.tags_per_family,
                    build_date=pp_storage.date_build
                )
            )
        )


api_blueprint.add_url_rule('/data', view_func=AllDataAPI.as_view(name='data'))


class NamesAPI(MethodView):
    @parser.use_kwargs({
        'elements': field_elements,
        'bs_name': fields.Str(),
        'bs_tag': fields.Str(),
        'pp_name': fields.Str(),
        'pp_tag': fields.Str()
    }, location='query')
    def get(self, **kwargs):
        bs_storage: Storage = flask.current_app.config['BASIS_SETS_STORAGE']
        pp_storage: Storage = flask.current_app.config['PSEUDOPOTENTIALS_STORAGE']

        elements = kwargs.get('elements', None)
        bs_name = kwargs.get('bs_name', None)
        pp_name = kwargs.get('pp_name', None)
        bs_tag = kwargs.get('bs_tag', None)
        pp_tag = kwargs.get('pp_tag', None)

        query = dict(type='ALL')

        if elements:
            query['elements'] = list(elements)

        return flask.jsonify(
            query=query,
            result=dict(
                basis_sets=bs_storage.get_names(elements, bs_name, bs_tag),
                pseudopotentials=pp_storage.get_names(elements, pp_name, pp_tag)
            )
        )


api_blueprint.add_url_rule('/names', view_func=NamesAPI.as_view(name='names'))


class BaseFamilyStorageDataAPI(MethodView):
    decorators = [limiter.limit(Config.API_LIMIT)]
    source: str = ''
    textual_source: str = ''

    @parser.use_kwargs({'name': field_name}, location='view_args')
    @parser.use_kwargs({'elements': field_elements, 'header': fields.Bool()}, location='query')
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
            for symbol in elements.iter_sorted():
                try:
                    atomic_data_objects.append(family_storage[symbol])
                except KeyError:
                    raise NotFound('{} `{}` does not exist for atom {}'.format(self.textual_source, name, symbol))

        header = ''
        TPL_DATETIME = '%d/%m/%Y @ %H:%M'

        if kwargs.get('header', True):
            header = '# URL: {}\n# BUILD: {}\n# FETCHED: {}\n# ---\n'.format(
                flask.url_for(
                    'api.{}-data'.format('basis' if self.source == 'BASIS_SET' else 'pseudo'),
                    name=name,
                    _external=True
                ) + ('?elements={}'.format(','.join(elements.iter_sorted())) if elements else ''),
                datetime.datetime.fromisoformat(storage.date_build).strftime('%d/%m/%Y @ %H:%M') if storage.date_build else '?',  # noqa
                datetime.datetime.now().strftime(TPL_DATETIME),
            )

        variants = {}
        for obj in atomic_data_objects:
            variants[obj.symbol] = dict((v, obj[v].preferred_name(name, v)) for v in obj)

        query = dict(type=self.source, name=name)
        result = dict(
            data=header + ''.join(str(obj) for obj in atomic_data_objects),
            elements=list(obj.symbol for obj in atomic_data_objects),
            variants=variants,
            metadata=family_storage.metadata
        )

        if elements:
            query['elements'] = list(elements.iter_sorted())

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
    decorators = [limiter.limit(Config.API_LIMIT)]
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
        result = {}
        result.update(**family_storage.metadata)
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
