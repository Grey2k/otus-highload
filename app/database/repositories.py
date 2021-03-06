from abc import ABC

from app.database.models import User, City, Profile, Friendship, Model, FriendshipStatus, Post, Subscribe
from app.database.utils import Pagination, PaginatedCollection
from app.ext.mysql import MysqlPool


class PoolPolicy:
    USE_MASTER = 0
    USE_SLAVE = 10

    def __init__(self, pool: MysqlPool, policy):
        self.pool = pool
        self.__policy = policy

    @property
    def db(self):
        return self.pool.master if self.__policy == self.USE_MASTER else self.pool.slave


class Spec:

    def __init__(self):
        self.attributes = {}
        self.conditions = []

    def where(self, condition: str, attributes: dict = None, operator: str = 'AND'):
        if attributes:
            self.attributes.update(attributes)
        if not self.conditions:
            operator = ''
        self.conditions.append((condition, operator))
        return self

    def __str__(self):
        if not self.conditions:
            return ''
        where = ' '.join([f'{operator} {cond}' for cond, operator in self.conditions]).strip()
        return f'WHERE {where}'


class BaseRepo(ABC):
    table_name = None
    model_class = None

    def __init__(self, pool: MysqlPool, policy=PoolPolicy.USE_MASTER):
        self.policy = PoolPolicy(pool, policy)

    @property
    def db(self):
        return self.policy.db

    def use_slave(self):
        return self.__class__(self.policy.pool, PoolPolicy.USE_SLAVE)

    def find_all(self):
        query = f'SELECT * from `{self.table_name}`'
        with self.db.cursor() as cursor:
            cursor.execute(query)
            items = [self.model_class(**row) for row in cursor.fetchall()]

        return items

    def find_paginate(self, page=1, count=10, sort='id', order='asc') -> PaginatedCollection:
        query = f'SELECT * from `{self.table_name}` ORDER BY {sort} {order} limit %s, %s'
        count_query = f'SELECT count(1) as cnt from `{self.table_name}`'
        with self.db.cursor() as cursor:
            cursor.execute(query, ((page - 1) * count, count))
            items = [self.model_class(**row) for row in cursor.fetchall()]
            cursor.execute(count_query)
            cnt = cursor.fetchone()
            pagination = Pagination(current_page=page, items_per_page=count, total_items=cnt['cnt'])

        return PaginatedCollection(items=items, pagination=pagination)

    def find_by_spec(self, spec: Spec, page=1, count=10):
        query = f'SELECT * from `{self.table_name}` {spec} limit %(offset)s, %(limit)s'
        count_query = f'SELECT * from `{self.table_name}` {spec}'
        with self.db.cursor() as cursor:
            cursor.execute(query, {'offset': (page - 1) * count, 'limit': count, **spec.attributes})
            items = [self.model_class(**row) for row in cursor.fetchall()]
            pagination = Pagination(
                current_page=page,
                items_per_page=count,
                total_items=cursor.execute(count_query, {**spec.attributes})
            )

        return PaginatedCollection(items=items, pagination=pagination)

    def find_by_id(self, entity_id):
        return self._find_one_by_attribute('id', entity_id)

    def find_by_ids(self, ids):
        if not ids:
            return []
        query = f'SELECT * from `{self.table_name}` WHERE id in %s'
        with self.db.cursor() as cursor:
            cursor.execute(query, [set(ids)])
            items = {row['id']: self.model_class(**row) for row in cursor.fetchall()}

        return items

    def _find_one_by_attribute(self, attr, value):
        sql = f'SELECT * FROM `{self.table_name}` where {attr}=%s'
        row = self.db.query(sql, (value,)).fetchone()
        return self.model_class(**row) if row else None

    def save(self, entity: Model):
        if not entity.id:
            return self._add(entity)
        return self._update(entity)

    def _add(self, entity: Model):
        data = {k: v for k, v in entity.to_dict().items() if v is not None and not isinstance(v, dict)}
        keys = ','.join(map(lambda k: f'`{k}`', data.keys()))
        values = ','.join(map(lambda k: f'%({k})s', data.keys()))
        query = f'INSERT INTO `{self.table_name}` ({keys}) VALUES ({values})'
        with self.db.cursor() as cursor:
            cursor.execute(query, data)
            if hasattr(entity, 'id'):
                entity.id = cursor.lastrowid
        return entity

    def _update(self, entity: Model):
        data = {k: v for k, v in entity.to_dict().items() if not isinstance(v, dict)}
        del data['id']
        placeholders = ', '.join(map(lambda key: f'`{key}` = %({key})s', data.keys()))
        query = f'UPDATE `{self.table_name}` SET {placeholders} WHERE id = %(id)s'
        with self.db.cursor() as cursor:
            cursor.execute(query, {'id': entity.id, **data})
        return entity

    def remove(self, entity):
        query = f'DELETE from `{self.table_name}` WHERE id = %s'
        with self.db.cursor() as cursor:
            cursor.execute(query, [entity.id])
            self.db.commit()

    def project(self, model: Model, row):
        return {key: row.get(key) for key in model.fields() if row.get(key) is not None}


class UserRepo(BaseRepo):
    table_name = 'users'
    model_class = User

    def find_by_email(self, email):
        return self._find_one_by_attribute('email', email)


class ProfileRepo(BaseRepo):
    table_name = 'profiles'
    model_class = Profile

    def find_by_user_id(self, user_id: int):
        return self._find_one_by_attribute('user_id', user_id)


class CityRepo(BaseRepo):
    table_name = 'cities'
    model_class = City


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
            cursor.execute(query, {'profile_id': profile_id, 'status': FriendshipStatus.CONFIRMED})
            profiles = [Profile(**row) for row in cursor.fetchall()]

        return profiles

    def find_incoming_requests(self, profile_id):
        query = f'''
            SELECT p.* from `{self.table_name}` as f
            LEFT JOIN `{self.profile_table_name}` as p on p.id = f.source_id
            WHERE f.destination_id = %s and f.status = %s
        '''
        with self.db.cursor() as cursor:
            cursor.execute(query, [profile_id, FriendshipStatus.WAITING])
            profiles = [Profile(**row) for row in cursor.fetchall()]

        return profiles

    def find_outgoing_requests(self, profile_id):
        query = f'''
           SELECT p.* from `{self.table_name}` as f
           LEFT JOIN `{self.profile_table_name}` as p on p.id = f.destination_id
           WHERE f.source_id = %s and f.status = %s
        '''
        with self.db.cursor() as cursor:
            cursor.execute(query, [profile_id, FriendshipStatus.WAITING])
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


class PostsRepo(BaseRepo):
    table_name = 'posts'
    model_class = Post

    def find_by_id(self, entity_id):
        post = super().find_by_id(entity_id)
        if not post:
            return None
        post.author = self._find_author(post.author_id)
        return post

    def _find_author(self, post_id):
        sql = f'SELECT * FROM `{ProfileRepo.table_name}` where id = %s'
        row = self.db.query(sql, (post_id,)).fetchone()
        return ProfileRepo.model_class(**row) if row else None

    def load_feed(self, feed_id, limit):
        query = f'''
            SELECT t.id, t.author_id, t.content, t.created_at, p.first_name, p.last_name  from `{self.table_name}` t
            JOIN `{SubscribersRepo.table_name}` s on t.author_id = s.subscribe_to
            JOIN `{ProfileRepo.table_name}` p on p.id = t.author_id
            WHERE s.subscriber = %(subscriber)s
            ORDER BY created_at desc
            LIMIT {limit}
        '''
        with self.db.cursor() as cursor:
            cursor.execute(query, {'subscriber': feed_id})
            rows = cursor.fetchall()
            items = []
            for row in rows:
                post = self.model_class(**self.project(self.model_class, row))
                post.author = ProfileRepo.model_class(**self.project(ProfileRepo.model_class, row))
                items.append(post)
        return items


class SubscribersRepo(BaseRepo):
    table_name = 'subscribers'
    model_class = Subscribe

    def find_subscribed(self, subscribed_to):
        query = f'SELECT * from `{self.table_name}` WHERE subscribe_to = %(id)s'
        with self.db.cursor() as cursor:
            cursor.execute(query, {'id': subscribed_to})
            items = [self.model_class(**row) for row in cursor.fetchall()]
        return items
