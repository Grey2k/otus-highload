from flask import current_app
from injector import singleton

from app.broker import publisher
from app.database.db import pool
from app.database.repositories import CityRepo, UserRepo, ProfileRepo, FriendRepo, PostsRepo, SubscribersRepo
from app.feed.providers import FeedProvider, TarantoolFeedProvider
from app.feed.services import Publisher
from app.service_discovery import ServiceDiscovery, consul
from app.tarantool.repositories import TarantoolProfilesRepo
from app.tarantool.tarantool import tarantool


def configure_di(binder):
    profiles_repo = ProfileRepo(pool)
    binder.bind(CityRepo, to=CityRepo(pool), scope=singleton)
    binder.bind(UserRepo, to=UserRepo(pool), scope=singleton)
    binder.bind(ProfileRepo, to=profiles_repo, scope=singleton)
    binder.bind(FriendRepo, to=FriendRepo(pool), scope=singleton)

    binder.bind(TarantoolProfilesRepo, to=TarantoolProfilesRepo(tarantool), scope=singleton)
    binder.bind(FeedProvider, to=TarantoolFeedProvider(tarantool), scope=singleton)
    binder.bind(PostsRepo, to=PostsRepo(pool), scope=singleton)
    binder.bind(SubscribersRepo, to=SubscribersRepo(pool), scope=singleton)
    binder.bind(Publisher, to=Publisher('feed_exchange', publisher), scope=singleton)

    binder.bind(ServiceDiscovery, to=ServiceDiscovery(consul=consul), scope=singleton)


def get(service):
    return current_app.di.get(service)
