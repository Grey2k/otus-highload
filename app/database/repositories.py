from dataclasses import dataclass
from math import ceil

from app.database.db import db
from app.database.models import User, City, Profile, Friendship


@dataclass
class Pagination:
    current_page: int
    items_per_page: int
    total_items: int

    @property
    def total_pages(self):
        return ceil(self.total_items / self.items_per_page)


@dataclass
class PaginatedCollection:
    pagination: Pagination
    items: list


class UserRepo:
    table_name = 'users'

    @classmethod
    def find_by_id(cls, uid):
        sql = f'SELECT * FROM `{cls.table_name}` where id=%s'
        user_data = db.query(sql, (uid,)).fetchone()
        if user_data is None:
            return None
        return User(**user_data)

    @classmethod
    def find_by_email(cls, email):
        sql = f'SELECT * FROM `{cls.table_name}` where email=%s'
        user_data = db.query(sql, (email,)).fetchone()
        if user_data is None:
            return None
        return User(**user_data)

    @classmethod
    def create(cls, email, password) -> User:
        with db.cursor() as cursor:
            query = f'INSERT INTO `{cls.table_name}` (`email`, `password`) VALUES (%s, %s)'
            cursor.execute(query, (email, password))
            return User(id=cursor.lastrowid, email=email, password=password)


class ProfileRepo:
    table_name = 'profiles'

    @classmethod
    def find_by_id(cls, profile_id: int):
        query = f'SELECT * from `{cls.table_name}` WHERE id=%s'
        with db.cursor() as cursor:
            cursor.execute(query, [profile_id])
            if cursor.rowcount == 0:
                return None
            profile = Profile(**cursor.fetchone())

        return profile

    @classmethod
    def find_by_user_id(cls, user_id: int):
        query = f'SELECT * from `{cls.table_name}` WHERE user_id=%s'
        with db.cursor() as cursor:
            cursor.execute(query, [user_id])
            if cursor.rowcount == 0:
                return None
            profile = Profile(**cursor.fetchone())

        return profile

    @classmethod
    def find_all(cls):
        query = f'SELECT * from `{cls.table_name}`'
        with db.cursor() as cursor:
            cursor.execute(query)
            profiles = [Profile(**row) for row in cursor.fetchall()]

        return profiles

    @classmethod
    def find_paginate(cls, page=1, count=10):
        query = f'SELECT * from `{cls.table_name}` limit %s, %s'
        count_query = f'SELECT * from `{cls.table_name}`'
        with db.cursor() as cursor:
            cursor.execute(query, ((page - 1) * count, count))
            profiles = [Profile(**row) for row in cursor.fetchall()]
            pagination = Pagination(current_page=page, items_per_page=count, total_items=cursor.execute(count_query))

        return PaginatedCollection(items=profiles, pagination=pagination)

    @classmethod
    def create(cls, first_name, last_name, interests, birth_date, gender, city_id, user_id) -> Profile:
        query = f'''
               INSERT INTO `{cls.table_name}`
                (`first_name`, `last_name`, `interests`, `birth_date`, `gender`, `city_id`, `user_id`)
               VALUES
                (%s, %s, %s, %s, %s, %s, %s)
            '''
        with db.cursor() as cursor:
            cursor.execute(query, (first_name, last_name, interests, birth_date, gender, city_id, user_id))
            return Profile(
                id=cursor.lastrowid,
                first_name=first_name, last_name=last_name,
                interests=interests, birth_date=birth_date, gender=gender,
                city_id=city_id, user_id=user_id
            )


class CityRepo:
    table_name = 'cities'

    @classmethod
    def find_all(cls):
        query = f'SELECT * from `{cls.table_name}`'
        with db.cursor() as cursor:
            cursor.execute(query)
            cities = [City(**row) for row in cursor.fetchall()]

        return cities

    @classmethod
    def add(cls, name):
        db.query('INSERT INTO `cities` (`name`) VALUES (%s)', name)
        db.commit()

    @classmethod
    def find_by_id(cls, entity_id: int):
        query = f'SELECT * from `{cls.table_name}` WHERE id=%s'
        with db.cursor() as cursor:
            cursor.execute(query, [entity_id])
            if cursor.rowcount == 0:
                return None
            city = City(**cursor.fetchone())

        return city

    @classmethod
    def find_by_ids(cls, ids):
        if not ids:
            return []
        query = f'SELECT * from `{cls.table_name}` WHERE id in %s'
        with db.cursor() as cursor:
            cursor.execute(query, [set(ids)])
            cities = {row['id']: City(**row) for row in cursor.fetchall()}

        return cities


class FriendRepo:
    table_name = 'friends'
    profile_table_name = 'profiles'

    @classmethod
    def find_all(cls, profile_id):
        query = f'''
        SELECT * from `{cls.profile_table_name}`
            WHERE id in (
                SELECT destination_id from `{cls.table_name}` WHERE source_id = %(profile_id)s and status = %(status)s
                UNION
                SELECT source_id from `{cls.table_name}` WHERE destination_id = %(profile_id)s and status = %(status)s
            )'''
        with db.cursor() as cursor:
            cursor.execute(query, {'profile_id': profile_id, 'status': 1})
            profiles = [Profile(**row) for row in cursor.fetchall()]

        return profiles

    @classmethod
    def find_incoming_requests(cls, profile_id):
        query = f'''
            SELECT p.* from `{cls.table_name}` as f
            LEFT JOIN `{cls.profile_table_name}` as p on p.id = f.source_id
            WHERE f.destination_id = %s and f.status = 0
        '''
        with db.cursor() as cursor:
            cursor.execute(query, [profile_id])
            profiles = [Profile(**row) for row in cursor.fetchall()]

        return profiles

    @classmethod
    def find_outgoing_requests(cls, profile_id):
        query = f'''
           SELECT p.* from `{cls.table_name}` as f
           LEFT JOIN `{cls.profile_table_name}` as p on p.id = f.destination_id
           WHERE f.source_id = %s and f.status = 0
        '''
        with db.cursor() as cursor:
            cursor.execute(query, [profile_id])
            profiles = [Profile(**row) for row in cursor.fetchall()]

        return profiles

    @classmethod
    def find_friendship(cls, profile_one, profile_two):
        query = f'''
           SELECT * from `{cls.table_name}`
           WHERE (source_id = %(one)s and destination_id = %(two)s) 
              or (source_id = %(two)s and destination_id = %(one)s)
        '''
        with db.cursor() as cursor:
            cursor.execute(query, {'one': profile_one, 'two': profile_two})
            if cursor.rowcount == 0:
                return None
            return Friendship(**cursor.fetchone())

    @classmethod
    def update(cls, friendship: Friendship):
        query = f'''
            UPDATE `{cls.table_name}`
            SET status = %(status)s 
            WHERE id = %(id)s
        '''
        with db.cursor() as cursor:
            cursor.execute(query, {'id': friendship.id, 'status': friendship.status})
            db.commit()

    @classmethod
    def create(cls, friendship: Friendship):
        query = f'''
            INSERT INTO `{cls.table_name}`
            (`source_id`, `destination_id`, `status`) VALUES (%s, %s, %s)
        '''
        with db.cursor() as cursor:
            cursor.execute(query, [friendship.source_id, friendship.destination_id, friendship.status])
            db.commit()
        return cursor.lastrowid

    @classmethod
    def remove(cls, friendship: Friendship):
        query = f'DELETE from `{cls.table_name}` WHERE id = %s'
        with db.cursor() as cursor:
            cursor.execute(query, [friendship.id])
            db.commit()
