
def up(db):
    sql = '''
        CREATE TABLE IF NOT EXISTS profiles
            (
                id bigint auto_increment,
                first_name varchar(255) not null,
                last_name varchar(255) not null,
                interests text not null,
                birth_date date not null,
                gender varchar(6) null,
                city_id int null,
                user_id bigint not null,
                constraint profiles_pk
                    primary key (id),
                constraint city_fk
                    foreign key (city_id) references cities (id)
                        on delete set null,
                constraint user_fk
                    foreign key (user_id) references users (id)
                        on delete cascade
            )
        '''
    db.query(sql)


def down(db):
    db.query('DROP TABLE profiles')
