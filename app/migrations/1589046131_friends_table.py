
def up(db):
    sql = '''
        CREATE TABLE IF NOT EXISTS friends
            (
                id bigint auto_increment,
                source_id bigint not null,
                destination_id bigint not null,
                status smallint not null,
                created_at datetime not null default NOW(),
                constraint friends_pk
                    primary key (id),
                constraint profiles_source_id_fk
                    foreign key (source_id) references profiles (id)
                        on delete cascade,
                constraint profiles_dest_id_fk_2
                    foreign key (destination_id) references profiles (id)
                        on delete cascade
            )
        '''
    db.query(sql)


def down(db):
    db.query('DROP TABLE friends')
