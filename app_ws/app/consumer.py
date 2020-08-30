import asyncio

import aio_pika

from app.settings import Settings


def create(app):
    config: Settings = app['config']
    manager = ConsumerManager(app, config.get('EXCHANGE_NAME'), config.get('NOTIFICATIONS_BROKER'))
    manager.run()
    return manager


class ConsumeTask:
    def __init__(self):
        self.consumer_tag = None
        self.task = None
        self.queue = None

    async def cancel(self, exchange):
        await self.queue.unbind(exchange)
        await self.queue.cancel(self.consumer_tag)
        self.task.cancel()
        await self.task


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
        self.connection_task = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.broker_url)

        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=self.prefetch_count)
        self.exchange = await self.channel.declare_exchange(self.exchange_name)

    def consume_queue(self, sid, queue_name, callback):
        consumer_task = ConsumeTask()

        async def consume(channel, exchange):
            queue = await channel.declare_queue(queue_name, auto_delete=True)
            await queue.bind(exchange, queue_name)
            consumer_tag = await queue.consume(callback)
            consumer_task.queue = queue
            consumer_task.consumer_tag = consumer_tag

        consumer_task.task = asyncio.create_task(consume(self.channel, self.exchange))
        self.tasks[sid] = consumer_task

    async def stop_cunsuming(self, sid):
        if not self.tasks.get(sid):
            return
        task = self.tasks[sid]
        del self.tasks[sid]
        await task.cancel(self.exchange)

    def run(self):
        self.app.on_startup.append(self._start)
        self.app.on_cleanup.append(self._stop)

    async def _start(self, *args, **kwargs):
        self.connection_task = asyncio.create_task(self.connect())

    async def _stop(self, *args, **kwargs):
        self.connection_task.cancel()
        self.connection_task = None

        for task in self.tasks.values():
            await task.cancel(self.exchange)

        self.tasks = {}
