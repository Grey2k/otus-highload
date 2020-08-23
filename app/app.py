import os

from app import create_app
from app.celery import celery as flask_celery

app = create_app(env=os.environ.get('ENV'))

celery = flask_celery.celery


class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask
