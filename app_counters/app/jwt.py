from datetime import timedelta

from flask_jwt import JWT


def identity(payload):
    return payload['identity']


jwt = JWT(authentication_handler=lambda *args, **kwargs: None, identity_handler=identity)


def init_jwt(app):
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=360)
    jwt.init_app(app)
