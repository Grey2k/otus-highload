import functools

from pymysql import MySQLError

from app.ext.mysql import MysqlPool, Mysql

pool = MysqlPool()


def transactional(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        db = pool.master
        try:
            db.begin_transaction()
            result = fn(*args, **kwargs)
            db.commit()
            return result
        except MySQLError as e:
            db.rollback()
            raise e

    return wrapped


def init_db(app):
    pool.set_master(Mysql(app, {
        'host': app.config.get('DB_HOST', 'localhost'),
        'port': int(app.config.get('DB_PORT', 3306)),
        'database': app.config.get('DB_DATABASE'),
        'user': app.config.get('DB_USER', 'usr'),
        'password': app.config.get('DB_PASSWORD', 'password'),
        'charset': app.config.get('DB_CHARSET', 'utf8mb4'),
    }))
    for slave_host in app.config.get('SLAVE_HOST', '').split(','):
        if not slave_host:
            continue
        pool.add_slave(Mysql(app, {
            'host': slave_host,
            'port': int(app.config.get('DB_PORT', 3306)),
            'database': app.config.get('DB_DATABASE'),
            'user': app.config.get('DB_USER', 'usr'),
            'password': app.config.get('DB_PASSWORD', 'password'),
            'charset': app.config.get('DB_CHARSET', 'utf8mb4'),
        }))
