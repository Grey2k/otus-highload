from celery import Celery


class FlaskCelery:

    def __init__(self, app=None):
        self.app = app
        self.celery = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
        celery.conf.update(app.config)
        self.celery = celery
