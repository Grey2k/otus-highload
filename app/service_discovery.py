from datetime import datetime, timedelta
import random
from dataclasses import dataclass

from consulate import Session
from flask_consulate import Consul

consul = Consul()


def init_discovery(app):
    consul.init_app(app)
    service_discovery: ServiceDiscovery = app.di.get(ServiceDiscovery)

    @app.teardown_request
    def healthcheck(*args, **kwargs):
        service_discovery.reload()


@dataclass
class Service:
    host: str
    port: str
    status: str

    @property
    def address(self):
        return f'http://{self.host}:{self.port}'

    def is_alive(self):
        return self.status == 'passing'


class ServiceDiscovery:

    def __init__(self, consul: Consul, health_interval=100):
        self.consul = consul
        self.health_interval = health_interval
        self.last_check = None
        self.services = {}

    def service(self, name) -> Service:
        if not self.services.get(name):
            self.services[name] = self.__load_service(name)
        active = [s for s in self.services[name] if s.is_alive()]
        return random.choice(active)

    def __load_service(self, name):
        instances = self.__session.catalog.service(name)
        if not instances:
            raise Exception(f'No service {name} instances')
        checks = self.__get_checks(name)
        return [
            Service(
                host=item.get('ServiceAddress'),
                port=item.get('ServicePort'),
                status=checks.get(f'service:{item.get("ServiceID")}')
            )
            for item in instances
        ]

    def __get_checks(self, name):
        return {check.get('CheckID'): check.get('Status') for check in self.__session.health.checks(name)}

    @property
    def __session(self) -> Session:
        return self.consul.session

    def reload(self):
        if not self.last_check:
            self.last_check = datetime.now()
        now = datetime.now()
        if now < self.last_check + timedelta(seconds=self.health_interval):
            return
        self.last_check = now
        for name in self.services.keys():
            self.services[name] = self.__load_service(name)