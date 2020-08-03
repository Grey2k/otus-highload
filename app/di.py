from flask import current_app
from injector import singleton

from app.database.db import pool
from app.database.repositories import CityRepo, UserRepo, ProfileRepo, FriendRepo, DialogsRepo


def configure_di(binder):
    binder.bind(CityRepo, to=CityRepo(pool), scope=singleton)
    binder.bind(UserRepo, to=UserRepo(pool), scope=singleton)
    binder.bind(ProfileRepo, to=ProfileRepo(pool), scope=singleton)
    binder.bind(FriendRepo, to=FriendRepo(pool), scope=singleton)
    binder.bind(DialogsRepo, to=DialogsRepo(pool), scope=singleton)


def get(service):
    return current_app.di.get(service)
