def up(db):
    sql = '''
        CREATE TABLE IF NOT EXISTS message_status
            (
                id bigint auto_increment,
                message_id bigint not null,
                recepient_id bigint not null,
                status smallint not null,
                constraint message_status_pk
                    primary key (id),
                constraint message_status_message_id_fk
                    foreign key (message_id) references dialogs_messages (id)
                        on delete cascade,
                constraint message_status_profile_fk
                    foreign key (recepient_id) references profiles (id)
                        on delete cascade
            )
        '''
    db.query(sql)


def down(db):
    db.query('DROP TABLE message_status')
