import flask
from flask.views import MethodView
from flask.blueprints import Blueprint
from typing import Union
from werkzeug.exceptions import NotFound, Forbidden

from webargs import fields
from webargs.flaskparser import FlaskParser

from cp2k_basis.atoms import SYMB_TO_Z


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

        ctx['ATOMS_PER_BASIS_SET'] = flask.current_app.config['ATOMS_PER_BASIS_SET']
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
@api_blueprint.errorhandler(409)
def handle_error_s(err: Union[NotFound, Forbidden]):
    return flask.jsonify(status=err.code, message=err.description), err.code


field_atoms = fields.DelimitedList(fields.Str(validate=lambda x: x in SYMB_TO_Z))
field_basis = fields.Str(validate=lambda x: x in flask.current_app.config['ATOMS_PER_BASIS_SET'])

parser = FlaskParser()


class BasisSetAPI(MethodView):

    @parser.use_kwargs({'basis': field_basis}, location='view_args')
    @parser.use_kwargs({'atoms': field_atoms}, location='query')
    def get(self, **kwargs):
        return flask.jsonify(status=200)


api_blueprint.add_url_rule('/basis/<basis>/', view_func=BasisSetAPI.as_view(name='test'))
