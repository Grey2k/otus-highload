from random import choice

import pymysql
from flask import _app_ctx_stack
from pymysql.cursors import Cursor


class Mysql:
    __instance = 0

    def __init__(self, app=None, config=None):
        self.app = app
        self.config = config
        self.__instance = self.__new_instance()
        if app is not None:
            self.init_app(app, config)

    def init_app(self, app, config):
        self.app = app
        self.app.teardown_appcontext(self.teardown)
        self.config = config

    @property
    def extension_name(self):
        return f'flask_mysql_{self.__instance}'

    @classmethod
    def __new_instance(cls):
        cls.__instance += 1
        return cls.__instance

    def connect(self):
        return pymysql.connect(
            host=self.config.get('host'),
            port=self.config.get('port'),
            database=self.config.get('database'),
            user=self.config.get('user'),
            password=self.config.get('password'),
            charset=self.config.get('charset'),
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


class MysqlPool:

    def __init__(self, master: Mysql = None):
        self._master = master
        self._slaves = []

    def set_master(self, master: Mysql):
        self._master = master

    def add_slave(self, slave: Mysql):
        self._slaves.append(slave)

    @property
    def master(self) -> Mysql:
        if not self._master:
            raise RuntimeError('Master not configured')
        return self._master

    @property
    def slave(self) -> Mysql:
        if not self._slaves:
            return self._master
        return choice(self._slaves)
