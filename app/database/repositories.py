from app.database.db import db
from app.database.models import User, City, Profile


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

    def find_friends(self, profile_id: int):
        pass

    @classmethod
    def find_all(cls):
        query = f'SELECT * from `{cls.table_name}`'
        with db.cursor() as cursor:
            cursor.execute(query)
            profiles = [Profile(**row) for row in cursor.fetchall()]

        return profiles

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
