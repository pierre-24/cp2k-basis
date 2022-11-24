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
field_name = fields.Str()

parser = FlaskParser()


class BaseDataAPI(MethodView):
    source: str = ''
    textual_source: str = ''

    @parser.use_kwargs({'name': field_name}, location='view_args')
    @parser.use_kwargs({'atoms': field_atoms}, location='query')
    def get(self, **kwargs):
        name = kwargs.pop('name')

        if name not in flask.current_app.config['ATOMS_PER_{}'.format(self.source)]:
            flask.abort(404, 'Unnkown {} {}'.format(self.textual_source, name))

        atoms = kwargs.pop('atoms', None)

        if not atoms:
            atoms = flask.current_app.config['ATOMS_PER_{}'.format(self.source)][name]

        result = []
        for symbol in atoms:
            data_per_atom = flask.current_app.config['{}S_PER_ATOM'.format(self.source)].get(symbol)
            if data_per_atom:
                data = getattr(data_per_atom, self.source.lower() + 's').get(name)
                if data:
                    result.append(data)
                else:
                    flask.abort(404, description='No {} {} for {}'.format(self.textual_source, name, symbol))
            else:
                flask.abort(404, description='No {} available for {}'.format(self.textual_source, symbol))

        return flask.jsonify(
            request=dict(
                atoms=atoms,
                name=name,
            ),
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
    '/pseudopotential/<name>/data', view_func=PseudopotentialDataAPI.as_view(name='pseudo-data'))
