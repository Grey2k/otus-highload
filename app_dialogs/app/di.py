from flask import current_app
from injector import singleton

from app.database.db import db
from app.database.repositories import ProfileRepo, DialogsRepo, DialogMessagesRepo, DialogParticipantsRepo, \
    MessageStatusRepo
from app.gateway import CountersGateway


def configure_di(app):

    def configure(binder):
        binder.bind(ProfileRepo, to=ProfileRepo(db), scope=singleton)
        binder.bind(DialogsRepo, to=DialogsRepo(db), scope=singleton)
        binder.bind(DialogMessagesRepo, to=DialogMessagesRepo(db), scope=singleton)
        binder.bind(DialogParticipantsRepo, to=DialogParticipantsRepo(db), scope=singleton)
        binder.bind(MessageStatusRepo, to=MessageStatusRepo(db), scope=singleton)
        binder.bind(CountersGateway, to=CountersGateway(app.config.get('COUNTERS_API_URL')), scope=singleton)

    return configure


def get(service):
    return current_app.di.get(service)
