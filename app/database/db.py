import functools

from pymysql import MySQLError

from app.ext.mysql import Mysql

db = Mysql()


def transactional(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        try:
            db.begin_transaction()
            result = fn(*args, **kwargs)
            db.commit()
            return result
        except MySQLError as e:
            db.rollback()
            raise e

    return wrapped
