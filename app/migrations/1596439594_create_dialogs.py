
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
                dialog_id bigint not null,
                sender_id bigint not null,
                created_at datetime not null default NOW(),
                text text,
                constraint dialogs_messages_pk
                    primary key (id),
                constraint dialogs_messages_dialogs_dialog_id_fk
                    foreign key (dialog_id) references dialogs (id)
                        on delete cascade,
                constraint dialogs_messages_profiles_sender_id_fk
                    foreign key (sender_id) references profiles (id)
                        on delete cascade
            )
        '''
    db.query(sql)
    sql = f'''
        CREATE TABLE IF NOT EXISTS dialogs_participants
            (
                dialog_id bigint not null,
                profile_id bigint not null,
                constraint dialogs_participants_pk
                    primary key (dialog_id, profile_id),
                constraint dialogs_participants_profiles_profile_id_fk
                    foreign key (profile_id) references profiles (id)
                        on delete cascade,
                constraint dialogs_participants_dialog_dialog_id_fk
                    foreign key (dialog_id) references dialogs (id)
                        on delete cascade
            )
        '''
    db.query(sql)


def down(db):
    db.query(f'DROP TABLE dialogs_participants')
    db.query(f'DROP TABLE dialogs_messages')
    db.query(f'DROP TABLE dialogs')
