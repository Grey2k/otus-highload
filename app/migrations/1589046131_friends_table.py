
def up(db):
    sql = '''
        CREATE TABLE IF NOT EXISTS friends
            (
                id bigint auto_increment,
                user_id bigint not null,
                friend_id bigint not null,
                status smallint not null,
                created_at datetime not null default NOW(),
                constraint friends_pk
                    primary key (id),
                constraint profiles_users_id_fk
                    foreign key (user_id) references users (id)
                        on delete cascade,
                constraint profiles_users_id_fk_2
                    foreign key (friend_id) references users (id)
                        on delete cascade
            )
        '''
    db.query(sql)


def down(db):
    db.query('DROP TABLE friends')
