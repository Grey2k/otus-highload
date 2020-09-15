import configparser
import os

from flask import Flask
from flask_injector import FlaskInjector

from app.council import register_services
from app.database.db import init_db
from app.di import configure_di
from app.jwt import jwt, init_jwt


def create_app(env="production"):
    app = Flask(__name__)
    init_config(app, env)
    init_jwt(app)
    init_db(app)
    init_routes(app)
    register_services(app)

    injector = FlaskInjector(app=app, modules=[configure_di(app)])
    app.di = injector.injector

    @app.after_request
    def after_request(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response

    return app


def init_config(app, env=None):
    env_config = {k: v for k, v in os.environ.items()}

    file_config = __read_config_from_file(app, env)
    config = {**file_config, **env_config}
    app.config.from_mapping(config)


def __read_config_from_file(app, env):
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(os.path.join(app.config.root_path, 'config.ini'))
    env = str(env or os.environ.get('ENV', '')).upper()
    config = dict(parser.items('DEFAULT'))
    if parser.has_section(env):
        config.update(dict(parser.items(env)))
    return config


def init_routes(app):
    from . import dialogs

    for bp in dialogs.API_VIEWS:
        app.register_blueprint(bp)
