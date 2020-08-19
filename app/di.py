from flask import current_app
from injector import singleton

from app.database.db import pool
from app.database.repositories import CityRepo, UserRepo, ProfileRepo, FriendRepo, DialogsRepo, DialogMessagesRepo, \
    DialogParticipantsRepo, PostsRepo
from app.tarantool.repositories import TarantoolProfilesRepo
from app.tarantool.tarantool import tarantool


def configure_di(binder):
    binder.bind(CityRepo, to=CityRepo(pool), scope=singleton)
    binder.bind(UserRepo, to=UserRepo(pool), scope=singleton)
    binder.bind(ProfileRepo, to=ProfileRepo(pool), scope=singleton)
    binder.bind(FriendRepo, to=FriendRepo(pool), scope=singleton)
    binder.bind(DialogsRepo, to=DialogsRepo(pool), scope=singleton)
    binder.bind(DialogMessagesRepo, to=DialogMessagesRepo(pool), scope=singleton)
    binder.bind(DialogParticipantsRepo, to=DialogParticipantsRepo(pool), scope=singleton)
    binder.bind(TarantoolProfilesRepo, to=TarantoolProfilesRepo(tarantool), scope=singleton)
    binder.bind(PostsRepo, to=PostsRepo(pool), scope=singleton)


def get(service):
    return current_app.di.get(service)
