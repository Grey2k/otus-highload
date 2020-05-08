
def up(db):
    sql = '''
        CREATE TABLE IF NOT EXISTS cities (
            id int auto_increment,
            name varchar(255) not null,
            constraint cities_pk
                primary key (id)
        )
    '''
    db.query(sql)


def down(db):
    db.query('DROP TABLE cities')
