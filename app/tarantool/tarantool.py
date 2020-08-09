from app.ext.tarantool import Tarantool

tarantool = Tarantool()


def init_tarantool(app):
    tarantool.init_app(app, {
        'host': app.config.get('TARANTOOL_HOST', 'tarantool'),
        'port': int(app.config.get('TARANTOOL_PORT', 3301)),
        'user': app.config.get('TARANTOOL_USER_NAME', 'tarantool'),
        'password': app.config.get('TARANTOOL_USER_PASSWORD', 'tarantool'),
    })
