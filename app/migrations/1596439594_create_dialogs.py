
def up(db):
    sql = f'''
        CREATE TABLE IF NOT EXISTS dialogs
            (
                id bigint auto_increment,
                type smallint not null,
                created_by bigint not null,
                created_at datetime not null default NOW(),
                constraint dialogs_pk
                    primary key (id),
                constraint dialogs_profiles_created_by_fk
                    foreign key (created_by) references profiles (id)
                        on delete cascade
            )
        '''
    db.query(sql)
    sql = f'''
        CREATE TABLE IF NOT EXISTS dialogs_messages
            (
                id bigint auto_increment,
                sender_id bigint not null,
                created_at datetime not null default NOW(),
                text text,
                constraint dialogs_messages_pk
                    primary key (id),
                constraint dialogs_messages_profiles_sender_id_fk
                    foreign key (sender_id) references profiles (id)
                        on delete cascade
            )
        '''
    db.query(sql)
    sql = f'''
        CREATE TABLE IF NOT EXISTS dialogs_participants
            (
                id bigint auto_increment,
                profile_id bigint not null,
                constraint dialogs_participants_pk
                    primary key (id),
                constraint dialogs_participants_profiles_sender_id_fk
                    foreign key (profile_id) references profiles (id)
                        on delete cascade
            )
        '''
    db.query(sql)


def down(db):
    db.query(f'DROP TABLE dialogs_participants')
    db.query(f'DROP TABLE dialogs_messages')
    db.query(f'DROP TABLE dialogs')
