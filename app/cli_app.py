import os
from datetime import datetime
from random import choice, randint

import click
from faker import Faker
from flask.cli import AppGroup
from werkzeug.security import generate_password_hash

from app import create_app
from app.celery import celery as flask_celery
from app.database.db import pool
from app.ext.migrate import Migrate

app = create_app(env=os.environ.get('ENV'))

celery = flask_celery.celery


class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask

db = pool.master
migrate = Migrate(app, db)
seed = AppGroup('seed', help='Seeding database')
app.cli.add_command(seed)
fake = Faker()


@seed.command('cities')
@click.argument('count')
def seed_cities(count):
    from app.database.repositories import CityRepo
    from app import di
    from app.database.models import City

    repo: CityRepo = di.get(CityRepo)
    for _ in range(int(count)):
        repo.save(City(name=fake.city()))
    db.commit()


@seed.command('users')
@click.argument('count')
def seed_users(count):
    from app.database.repositories import UserRepo
    from app import di
    from app.database.models import User, Profile
    from app.database.repositories import ProfileRepo

    user_repo: UserRepo = di.get(UserRepo)
    profile_repo: ProfileRepo = di.get(ProfileRepo)
    count = int(count)
    time = datetime.now().strftime('%d%m%y%H%M%S')
    with click.progressbar(length=count, show_percent=True, show_eta=True, show_pos=True) as bar:
        for idx in bar:
            user = User(email=f"{idx}@{time}.com", password=generate_password_hash(fake.password()))
            user_repo.save(user)
            profile_repo.save(Profile(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                interests=fake.paragraph(),
                birth_date=fake.date_of_birth().strftime('%Y-%m-%d'),
                gender=choice(['male', 'female']),
                city_id=randint(1, 10),
                user_id=user.id
            ))
            db.commit()


@app.cli.command('build_feed')
@click.argument('feed_id', type=int)
def build_feed(feed_id):
    from app.feed.services import FeedService
    from app import di

    feed: FeedService = di.get(FeedService)
    feed.build(feed_id)
