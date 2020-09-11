from flask import current_app


def configure_di(binder):
    pass


def get(service):
    return current_app.di.get(service)
