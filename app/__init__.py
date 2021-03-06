import configparser
import os
from datetime import datetime

from flask import Flask
from flask_injector import FlaskInjector

from app.ext.pika import FlaskPika


def create_app(env="production"):
    app = Flask(__name__)
    init_config(app, env)

    from app.broker import publisher
    publisher.init_app(app)

    from app.celery import celery
    celery.init_app(app)

    from app.database.db import pool, init_db
    init_db(app)

    from app.jwt import init_jwt
    init_jwt(app)

    from app.tarantool.tarantool import init_tarantool
    init_tarantool(app)

    init_routes(app)
    from app.di import configure_di
    injector = FlaskInjector(app=app, modules=[configure_di])
    app.di = injector.injector

    from app.auth import login_manager
    login_manager.init_app(app)

    init_template_filters(app)
    init_tasks()

    from app.service_discovery import init_discovery
    init_discovery(app)

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
    from . import main
    from . import friends
    from . import dialogs
    from . import feed

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(friends.bp)
    app.register_blueprint(dialogs.bp)
    app.register_blueprint(feed.bp)


def init_template_filters(app):
    @app.template_filter('datetime')
    def filter_datetime(dt: datetime):
        return dt.strftime('%d.%m.%Y %H:%M')


def init_tasks():
    import app.feed.tasks
