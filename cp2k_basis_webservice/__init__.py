"""
Implementation of a working webservice
"""

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


limiter = Limiter(key_func=get_remote_address)


def create_app():
    app = Flask(__name__)

    limiter.init_app(app)

    # add blueprint(s)
    from cp2k_basis_webservice.blueprint import visitor_blueprint
    app.register_blueprint(visitor_blueprint)

    return app
