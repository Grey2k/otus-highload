from flask import current_app
from injector import singleton

from app.database.db import db
from app.database.repositories import ProfileRepo, DialogsRepo, DialogMessagesRepo, DialogParticipantsRepo


def configure_di(binder):
    binder.bind(ProfileRepo, to=ProfileRepo(db), scope=singleton)
    binder.bind(DialogsRepo, to=DialogsRepo(db), scope=singleton)
    binder.bind(DialogMessagesRepo, to=DialogMessagesRepo(db), scope=singleton)
    binder.bind(DialogParticipantsRepo, to=DialogParticipantsRepo(db), scope=singleton)


def get(service):
    return current_app.di.get(service)
