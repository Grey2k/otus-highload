
table_name = 'dialogs'


def up(db):
    sql = f'''
        CREATE TABLE IF NOT EXISTS {table_name}
            (
                id bigint auto_increment,
                sender_id bigint not null,
                recipient_id bigint not null,
                created_at datetime not null default NOW(),
                message text,
                updated_at datetime,
                constraint dialogs_pk
                    primary key (id),
                constraint dialogs_profiles_sender_id_fk
                    foreign key (sender_id) references profiles (id)
                        on delete cascade,
                constraint dialogs_profiles_recipient_id_fk
                    foreign key (recipient_id) references profiles (id)
                        on delete cascade
            )
        '''
    db.query(sql)


def down(db):
    db.query(f'DROP TABLE {table_name}')
