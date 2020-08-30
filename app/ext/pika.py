import pika
from flask import _app_ctx_stack
from pika.channel import Channel


class FlaskPika:
    extension_name = 'flask_pika'
    app = None
    parameters = None

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.app.teardown_appcontext(self.teardown)
        self.parameters = pika.URLParameters(app.config['NOTIFICATIONS_BROKER'])

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        if hasattr(ctx, self.extension_name):
            getattr(ctx, self.extension_name).close()

    def connect(self):
        return pika.BlockingConnection(self.parameters)

    @property
    def connection(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, self.extension_name):
                setattr(ctx, self.extension_name, self.connect())
            return getattr(ctx, self.extension_name)

    @property
    def channel(self) -> Channel:
        return self.connection.channel()
