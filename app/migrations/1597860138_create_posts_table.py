
def up(db):
    sql = '''
        CREATE TABLE IF NOT EXISTS posts
            (
                id bigint auto_increment,
                author_id bigint,
                content longtext,
                created_at datetime not null default NOW(),
                updated_at datetime,
                constraint posts_pk
                    primary key (id),
                constraint author_fk
                    foreign key (author_id) references profiles(id)
                        on delete cascade
            )
    '''
    db.query(sql)


def down(db):
    db.query('DROP TABLE posts')
