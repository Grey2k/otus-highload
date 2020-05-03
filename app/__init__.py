import configparser
import os

from flask import Flask

from app.db import db


def create_app(env="production"):
    app = Flask(__name__)
    init_config(app, env)
    db.init_app(app)
    init_routes(app)

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
    from . import auth

    app.register_blueprint(auth.bp)


