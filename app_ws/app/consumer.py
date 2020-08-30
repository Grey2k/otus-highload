import asyncio

import aio_pika

from app.settings import Settings


def create(app):
    config: Settings = app['config']
    manager = ConsumerManager(app, config.get('EXCHANGE_NAME'), config.get('NOTIFICATIONS_BROKER'))
    manager.run()
    return manager


class ConsumerManager:

    def __init__(self, app, exchange_name, broker_url, prefetch_count=100):
        self.app = app
        self.exchange_name = exchange_name
        self.broker_url = broker_url
        self.prefetch_count = prefetch_count
        self.connection = None
        self.channel = None
        self.exchange = None
        self.tasks = {}

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.broker_url)

        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=self.prefetch_count)
        self.exchange = await self.channel.declare_exchange(self.exchange_name, auto_delete=True)

    def consume_queue(self, sid, queue_name, callback):
        async def consume(channel, exchange):
            queue = await channel.declare_queue(queue_name, auto_delete=True)
            await queue.bind(exchange, queue_name)
            await queue.consume(callback)

        self.tasks[sid] = asyncio.create_task(consume(self.channel, self.exchange))

    async def stop_cunsuming(self, sid):
        if not self.tasks.get(sid):
            return
        self.tasks[sid].cancel()
        await self.tasks[sid]
        del self.tasks[sid]

    def run(self):
        self.app.on_startup.append(self._start)
        self.app.on_cleanup.append(self._stop)

    async def _start(self, *args, **kwargs):
        self.tasks['connection'] = asyncio.create_task(self.connect())

    async def _stop(self, *args, **kwargs):
        for task in self.tasks.values():
            task.cancel()
            await task
        self.tasks = {}
