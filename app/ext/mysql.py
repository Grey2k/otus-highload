import pymysql
from flask import _app_ctx_stack
from pymysql.cursors import Cursor


class Mysql:
    extension_name = 'flask_mysql'

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.app.teardown_appcontext(self.teardown)

    def connect(self):
        return pymysql.connect(
            host=self.app.config.get('DB_HOST', 'localhost'),
            port=int(self.app.config.get('DB_PORT', 3306)),
            database=self.app.config.get('DB_DATABASE'),
            user=self.app.config.get('DB_USER', 'usr'),
            password=self.app.config.get('DB_PASSWORD', 'password'),
            charset=self.app.config.get('DB_CHARSET', 'utf8mb4'),
            cursorclass=pymysql.cursors.DictCursor
        )

    def query(self, sql, variables=None):
        with self.cursor() as cursor:
            cursor.execute(sql, variables)
            return cursor

    def cursor(self) -> Cursor:
        return self.connection.cursor()

    def begin_transaction(self):
        self.connection.begin()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        if hasattr(ctx, self.extension_name):
            getattr(ctx, self.extension_name).close()

    @property
    def connection(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, self.extension_name):
                setattr(ctx, self.extension_name, self.connect())
            return getattr(ctx, self.extension_name)
