
def up(db):
    sql = '''
    CREATE TABLE IF NOT EXISTS users (
        id bigint auto_increment,
        email varchar(255) not null,
        password varchar(255) not null,
        constraint users_pk
            primary key (id)
    )
    '''
    db.query(sql)


def down(db):
    db.query('DROP TABLE `users`')
