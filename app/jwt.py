from datetime import timedelta
from functools import wraps

from flask import request, url_for
from flask_jwt import JWT, _default_jwt_encode_handler, _default_jwt_decode_handler
from jwt import InvalidTokenError
from werkzeug.utils import redirect


def identity(payload):
    return payload['identity']


jwt = JWT(authentication_handler=lambda *args, **kwargs: None, identity_handler=identity)


def init_jwt(app):
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=360)
    jwt.init_app(app)


def create_token(profile):
    return _default_jwt_encode_handler(profile).decode()


def jwt_cookie_required(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        try:
            token = request.cookies.get('auth_token')
            _default_jwt_decode_handler(token)
        except InvalidTokenError as e:
            return redirect(url_for('auth.logout'))
        return fn(*args, **kwargs)

    return decorator
