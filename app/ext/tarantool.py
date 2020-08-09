from tarantool import Connection
from flask import _app_ctx_stack
from tarantool.space import Space


class Tarantool:

    def __init__(self, app=None, config=None):
        self.app = app
        self.config = config
        if app is not None:
            self.init_app(app, config)

    def init_app(self, app, config):
        self.app = app
        self.app.teardown_appcontext(self.teardown)
        self.config = config

    @property
    def extension_name(self):
        return 'flask_tarantool'

    def connect(self):
        return Connection(
            host=self.config.get('host'),
            port=self.config.get('port'),
            user=self.config.get('user'),
            password=self.config.get('password'),
        )

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        if hasattr(ctx, self.extension_name):
            getattr(ctx, self.extension_name).close()

    @property
    def connection(self) -> Connection:
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, self.extension_name):
                setattr(ctx, self.extension_name, self.connect())
            return getattr(ctx, self.extension_name)

    def space(self, name) -> Space:
        return self.connection.space(name)
