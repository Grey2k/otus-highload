from flask import current_app
from injector import singleton

from app.database.db import db
from app.database.repositories import CityRepo, UserRepo, ProfileRepo, FriendRepo


def configure_di(binder):
    binder.bind(CityRepo, to=CityRepo(db), scope=singleton)
    binder.bind(UserRepo, to=UserRepo(db), scope=singleton)
    binder.bind(ProfileRepo, to=ProfileRepo(db), scope=singleton)
    binder.bind(FriendRepo, to=FriendRepo(db), scope=singleton)


def get(service):
    return current_app.di.get(service)
