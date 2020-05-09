import os
from random import choice, randint

import click
from faker import Faker
from flask.cli import AppGroup
from werkzeug.security import generate_password_hash

from app import create_app
from app.database.db import db
from app.database.repositories import CityRepo, UserRepo, ProfileRepo
from app.ext.migrate import Migrate

app = create_app(env=os.environ.get('ENV'))
migrate = Migrate(app, db)
seed = AppGroup('seed', help='Seeding database')
app.cli.add_command(seed)


@seed.command('cities')
@click.argument('count')
def seed_cities(count):
    fake = Faker()

    for _ in range(int(count)):
        CityRepo.add(fake.city())


@seed.command('users')
@click.argument('count')
def seed_users(count):
    fake = Faker()
    for _ in range(int(count)):
        user = UserRepo.create(fake.free_email(), generate_password_hash(fake.password()))
        ProfileRepo.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            interests=fake.paragraph(),
            birth_date=fake.date_of_birth().strftime('%Y-%m-%d'),
            gender=choice(['male', 'female']),
            city_id=randint(1, 10),
            user_id=user.id
        )
        db.commit()

