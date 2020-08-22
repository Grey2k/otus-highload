import os

from app import create_app, celery as flask_celery

app = create_app(env=os.environ.get('ENV'))

celery = flask_celery.celery
