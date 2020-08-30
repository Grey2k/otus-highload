import socketio


class Connection:

    def __init__(self, sid, environ):
        self.sid = sid
        self.environ = environ
        self.queue_name = f'feed_{self._get_feed_id()}'

    def _get_feed_id(self):
        return self.environ.get('aiohttp.request').query.get('feed_id')


class ConnectionManager:

    def __init__(self, sio):
        self.connections = {}
        self.sio = sio
        self.connect = sio.event(self.connect)
        self.disconnect = sio.event(self.disconnect)
        self.disconnect_request = sio.event(self.disconnect_request)
        self._on_connect = None
        self._on_disconnect = None

    def on_connect(self, cb):
        self._on_connect = cb

    def on_disconnect(self, cb):
        self._on_disconnect = cb

    def close(self, sid):
        if self.connections.get(sid, False):
            del self.connections[sid]

    async def connect(self, sid, environ):
        self.connections[sid] = Connection(sid, environ)
        if self._on_connect:
            self._on_connect(self.connections[sid])

    async def disconnect(self, sid):
        self.close(sid)
        if self._on_disconnect:
            await self._on_disconnect(sid)

    async def disconnect_request(self, sid):
        await self.sio.disconnect(sid)
        self.close(sid)

    async def emit(self, event_name, data, room):
        await self.sio.emit(event_name, data, room=room)


def create(app):
    sio = socketio.AsyncServer(
        async_mode='aiohttp',
        cors_allowed_origins='*',
    )
    sio.attach(app)
    return ConnectionManager(sio)
