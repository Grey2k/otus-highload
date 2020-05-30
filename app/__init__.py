import configparser
import os

from flask import Flask
from flask_injector import FlaskInjector
from flask_login import LoginManager

from app.database.db import db
from app.database.repositories import UserRepo, ProfileRepo
from app.di import configure_di


def create_app(env="production"):
    app = Flask(__name__)
    init_config(app, env)
    db.init_app(app)
    init_routes(app)
    injector = FlaskInjector(app=app, modules=[configure_di])
    app.di = injector.injector
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(id):
        user_repo = app.di.get(UserRepo)
        profile_repo = app.di.get(ProfileRepo)
        user = user_repo.find_by_id(id) if id else None
        if user:
            user.profile = profile_repo.find_by_user_id(user.id)
        return user

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

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(friends.bp)
