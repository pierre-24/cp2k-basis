import flask
from flask.views import MethodView
from flask.blueprints import Blueprint


class RenderTemplateView(MethodView):
    methods = ['GET']
    template_name = None

    def get_context_data(self):
        return {}

    def get(self):
        """Handle GET: render template"""

        if not self.template_name:
            raise ValueError('template_name')

        context_data = self.get_context_data()
        return flask.render_template(self.template_name, **context_data)


visitor_blueprint = Blueprint('visitor', __name__)


class IndexView(RenderTemplateView):
    template_name = 'index.html'

    def get_context_data(self):
        ctx = super().get_context_data()

        ctx['ATOMS_PER_BASIS_SET'] = flask.current_app.config['ATOMS_PER_BASIS_SET']
        return ctx


visitor_blueprint.add_url_rule('/', view_func=IndexView.as_view(name='index'))
