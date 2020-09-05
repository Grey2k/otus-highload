from app.ext.mysql import MysqlPool, Mysql

db = MysqlPool()


def init_db(app):
    db.set_master(Mysql(app, {
        'host': app.config.get('DIALOGS_DB', 'dialogs-db'),
        'port': int(app.config.get('DIALOGS_DB_PORT', 3306)),
        'database': app.config.get('DIALOGS_DB_DATABASE', 'dialogs_db'),
        'user': app.config.get('DIALOGS_DB_USER', 'root'),
        'password': app.config.get('DIALOGS_DB_PASSWORD', 'root'),
        'charset': app.config.get('DIALOGS_DB_CHARSET', 'utf8mb4'),
    }))
