import asyncio
import json

import aio_pika
from aiohttp import web

import app.websocket as websocket
import app.consumer as consumer
from app.settings import Settings

app = web.Application()
app['config'] = Settings.from_env()
connection_manager = websocket.create(app)
consumer_manager = consumer.create(app)


def consume(connection: websocket.Connection):
    async def process_message(message: aio_pika.IncomingMessage):
        async with message.process():
            print(json.loads(message.body), flush=True)
            await connection_manager.emit('new-post', json.loads(message.body), room=connection.sid)
            await asyncio.sleep(1)

    consumer_manager.consume_queue(connection.queue_name, process_message)


connection_manager.on_connect(consume)
