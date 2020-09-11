from flask import Blueprint

from app.counters.resource import resource, CounterResource
from app.redis import redis_store

v1 = Blueprint('counters', __name__, url_prefix='/counters')


@v1.route('/chat/<chat_id>/messages/<profile_id>', methods=['GET'])
def get_messages_count(chat_id: int, profile_id: int):
    count = redis_store.get(f'{profile_id}:{chat_id}')
    count = int(count) if count else 0
    return resource(CounterResource(count))


@v1.route('/user/<profile_id>/chats', methods=['GET'])
def get_chats_count(profile_id: int):
    keys = list(redis_store.scan_iter(match=f'{profile_id}:*'))
    values = redis_store.mget(keys)
    return {
        'items': dict(
            zip(
                map(lambda x: x.replace(f'{profile_id}:', ''), keys),
                map(lambda x: int(x) if x else 0, values))
        )
    }


@v1.route('/chat/<chat_id>/messages/<profile_id>/inc', methods=['POST'])
def increment_messages(chat_id: int, profile_id: int):
    count = redis_store.incr(f'{profile_id}:{chat_id}')
    return resource(CounterResource(count))


@v1.route('/chat/<chat_id>/messages/<profile_id>/dec', methods=['POST'])
def decrement_messages(chat_id: int, profile_id: int):
    count = redis_store.decr(f'{profile_id}:{chat_id}')
    return resource(CounterResource(count))
