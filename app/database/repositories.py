from abc import ABC

from app.database.models import User, City, Profile, Friendship
from app.database.utils import Pagination, PaginatedCollection
from app.ext.mysql import Mysql


class BaseRepo(ABC):
    table_name = None
    model_class = None

    def __init__(self, db: Mysql):
        self.db = db

    def find_all(self):
        query = f'SELECT * from `{self.table_name}`'
        with self.db.cursor() as cursor:
            cursor.execute(query)
            items = [self.model_class(**row) for row in cursor.fetchall()]

        return items

    def find_paginate(self, page=1, count=10) -> PaginatedCollection:
        query = f'SELECT * from `{self.table_name}` limit %s, %s'
        count_query = f'SELECT * from `{self.table_name}`'
        with self.db.cursor() as cursor:
            cursor.execute(query, ((page - 1) * count, count))
            items = [self.model_class(**row) for row in cursor.fetchall()]
            pagination = Pagination(current_page=page, items_per_page=count, total_items=cursor.execute(count_query))

        return PaginatedCollection(items=items, pagination=pagination)

    def find_by_id(self, entity_id):
        return self._find_one_by_attribute('id', entity_id)

    def _find_one_by_attribute(self, attr, value):
        sql = f'SELECT * FROM `{self.table_name}` where {attr}=%s'
        row = self.db.query(sql, (value,)).fetchone()
        return self.model_class(**row) if row else None

    def remove(self, entity):
        query = f'DELETE from `{self.table_name}` WHERE id = %s'
        with self.db.cursor() as cursor:
            cursor.execute(query, [entity.id])
            self.db.commit()


class UserRepo(BaseRepo):
    table_name = 'users'
    model_class = User

    def find_by_email(self, email):
        return self._find_one_by_attribute('email', email)

    def create(self, email, password) -> User:
        with self.db.cursor() as cursor:
            query = f'INSERT INTO `{self.table_name}` (`email`, `password`) VALUES (%s, %s)'
            cursor.execute(query, (email, password))
            return User(id=cursor.lastrowid, email=email, password=password)


class ProfileRepo(BaseRepo):
    table_name = 'profiles'
    model_class = Profile

    def find_by_user_id(self, user_id: int):
        return self._find_one_by_attribute('user_id', user_id)

    def create(self, first_name, last_name, interests, birth_date, gender, city_id, user_id) -> Profile:
        query = f'''
               INSERT INTO `{self.table_name}`
                (`first_name`, `last_name`, `interests`, `birth_date`, `gender`, `city_id`, `user_id`)
               VALUES
                (%s, %s, %s, %s, %s, %s, %s)
            '''
        with self.db.cursor() as cursor:
            cursor.execute(query, (first_name, last_name, interests, birth_date, gender, city_id, user_id))
            return Profile(
                id=cursor.lastrowid,
                first_name=first_name, last_name=last_name,
                interests=interests, birth_date=birth_date, gender=gender,
                city_id=city_id, user_id=user_id
            )


class CityRepo(BaseRepo):
    table_name = 'cities'
    model_class = City

    def create(self, name):
        self.db.query(f'INSERT INTO `{self.table_name}` (`name`) VALUES (%s)', name)
        self.db.commit()

    def find_by_ids(self, ids):
        if not ids:
            return []
        query = f'SELECT * from `{self.table_name}` WHERE id in %s'
        with self.db.cursor() as cursor:
            cursor.execute(query, [set(ids)])
            cities = {row['id']: City(**row) for row in cursor.fetchall()}

        return cities


class FriendRepo(BaseRepo):
    table_name = 'friends'
    model_class = Friendship
    profile_table_name = 'profiles'

    def find_friends(self, profile_id):
        query = f'''
        SELECT * from `{self.profile_table_name}`
            WHERE id in (
                SELECT destination_id from `{self.table_name}` WHERE source_id = %(profile_id)s and status = %(status)s
                UNION
                SELECT source_id from `{self.table_name}` WHERE destination_id = %(profile_id)s and status = %(status)s
            )'''
        with self.db.cursor() as cursor:
            cursor.execute(query, {'profile_id': profile_id, 'status': 1})
            profiles = [Profile(**row) for row in cursor.fetchall()]

        return profiles

    def find_incoming_requests(self, profile_id):
        query = f'''
            SELECT p.* from `{self.table_name}` as f
            LEFT JOIN `{self.profile_table_name}` as p on p.id = f.source_id
            WHERE f.destination_id = %s and f.status = 0
        '''
        with self.db.cursor() as cursor:
            cursor.execute(query, [profile_id])
            profiles = [Profile(**row) for row in cursor.fetchall()]

        return profiles

    def find_outgoing_requests(self, profile_id):
        query = f'''
           SELECT p.* from `{self.table_name}` as f
           LEFT JOIN `{self.profile_table_name}` as p on p.id = f.destination_id
           WHERE f.source_id = %s and f.status = 0
        '''
        with self.db.cursor() as cursor:
            cursor.execute(query, [profile_id])
            profiles = [Profile(**row) for row in cursor.fetchall()]

        return profiles

    def find_friendship(self, profile_one, profile_two):
        query = f'''
           SELECT * from `{self.table_name}`
           WHERE (source_id = %(one)s and destination_id = %(two)s) 
              or (source_id = %(two)s and destination_id = %(one)s)
        '''
        with self.db.cursor() as cursor:
            cursor.execute(query, {'one': profile_one, 'two': profile_two})
            if cursor.rowcount == 0:
                return None
            return Friendship(**cursor.fetchone())

    def update(self, friendship: Friendship):
        query = f'''
            UPDATE `{self.table_name}`
            SET status = %(status)s 
            WHERE id = %(id)s
        '''
        with self.db.cursor() as cursor:
            cursor.execute(query, {'id': friendship.id, 'status': friendship.status})
            self.db.commit()

    def create(self, friendship: Friendship):
        query = f'''
            INSERT INTO `{self.table_name}`
            (`source_id`, `destination_id`, `status`) VALUES (%s, %s, %s)
        '''
        with self.db.cursor() as cursor:
            cursor.execute(query, [friendship.source_id, friendship.destination_id, friendship.status])
            self.db.commit()
        return cursor.lastrowid
