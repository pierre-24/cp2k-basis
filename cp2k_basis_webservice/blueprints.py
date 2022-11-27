import flask
from flask.views import MethodView
from flask.blueprints import Blueprint
from typing import Union
from werkzeug.exceptions import NotFound, Forbidden

from webargs import fields
from webargs.flaskparser import FlaskParser

from cp2k_basis.elements import ElementSetField
from cp2k_basis.base_objects import Storage, StorageException


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
@api_blueprint.errorhandler(409)
def handle_error_s(err: Union[NotFound, Forbidden]):
    return flask.jsonify(status=err.code, message=err.description), err.code


field_elements = ElementSetField()
field_name = fields.Str()

parser = FlaskParser()


class BaseDataAPI(MethodView):
    source: str = ''
    textual_source: str = ''

    @parser.use_kwargs({'name': field_name}, location='view_args')
    @parser.use_kwargs({'elements': field_elements}, location='query')
    def get(self, **kwargs):
        storage: Storage = flask.current_app.config['{}S_STORAGE'.format(self.source)]

        elements = kwargs.get('elements', None)
        name = kwargs.get('name')

        try:
            result = list(storage.get_atomic_data_objects(name, elements))
        except StorageException as e:
            flask.abort(404, description=str(e))

        query = dict(name=name)

        if elements:
            query['elements'] = list(elements)

        return flask.jsonify(
            query=query,
            result=''.join(str(data) for data in result)
        )


class BasisSetDataAPI(BaseDataAPI):
    source = 'BASIS_SET'
    textual_source = 'basis set'


api_blueprint.add_url_rule('/basis/<name>/data', view_func=BasisSetDataAPI.as_view(name='basis-data'))


class PseudopotentialDataAPI(BaseDataAPI):

    source = 'PSEUDOPOTENTIAL'
    textual_source = 'pseudopotential'


api_blueprint.add_url_rule(
    '/pseudopotentials/<name>/data', view_func=PseudopotentialDataAPI.as_view(name='pseudo-data'))
