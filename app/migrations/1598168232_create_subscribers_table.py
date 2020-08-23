def up(db):
    sql = '''
        CREATE TABLE IF NOT EXISTS subscribers
            (
                id bigint auto_increment,
                subscriber bigint not null,
                subscribe_to bigint not null,
                constraint subscribers_pk
                    primary key (id),
                constraint subscriber_id_fk
                    foreign key (subscriber) references profiles (id)
                        on delete cascade,
                constraint subscribe_to_fk
                    foreign key (subscribe_to) references profiles (id)
                        on delete cascade
            )
        '''
    db.query(sql)


def down(db):
    db.query('DROP TABLE subscribers')