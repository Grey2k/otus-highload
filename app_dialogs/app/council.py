from flask_consulate import Consul
import socket

consul = Consul()


def register_services(app):
    consul.init_app(app)
    host_name = socket.gethostname()
    consul.register_service(
        service_id=socket.gethostname(),
        name='dialogs-app',
        address=app.config.get('APP_HOST'),
        interval='10s',
        port=int(app.config.get('APP_PORT')),
        httpcheck=f'http://{host_name}:8000/health'
    )