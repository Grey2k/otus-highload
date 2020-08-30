import json
from datetime import datetime

from flask import current_app
from injector import inject

from app import FlaskPika
from app.database.models import Profile, Post
from app.database.repositories import PostsRepo
from app.events import event_manager
from app.feed.providers import FeedProvider


class Publisher:

    def __init__(self, exchange_name: str, publisher: FlaskPika):
        self.exchange_name = exchange_name
        self.publisher = publisher
        self.exchange_inited = True

    def publish(self, routing_key, body):
        with current_app.app_context():
            self.publisher.channel.basic_publish(self.exchange_name, routing_key, body)


class FeedService:
    LIMIT = 1000

    @inject
    def __init__(self, feed_provider: FeedProvider, posts_repo: PostsRepo, publisher: Publisher):
        self.feed_provider = feed_provider
        self.posts_repo = posts_repo
        self.publisher = publisher

    def load(self, feed_id, page, count):
        return self.feed_provider.load(feed_id, page, count)

    def add_post(self, feed_id, post):
        self.feed_provider.add(feed_id, post)
        self.feed_provider.cutoff(feed_id, self.LIMIT)
        self.publisher.publish(
            routing_key=f'feed_{feed_id}',
            body=json.dumps({
                'id': post.id,
                'feed_id': feed_id,
                'author': post.author.name,
                'author_id': post.author_id,
                'content': post.content,
                'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }).encode()
        )

    def build(self, feed_id):
        self.feed_provider.clear(feed_id)
        posts = self.posts_repo.load_feed(feed_id, self.LIMIT)
        for post in posts:
            self.feed_provider.add(feed_id, post)
        self.feed_provider.cutoff(feed_id, self.LIMIT)


class PostService:

    @inject
    def __init__(self, repo: PostsRepo):
        self.repo = repo

    def create(self, author: Profile, content: str):
        post = self.repo.save(Post(
            author_id=author.id,
            content=content,
            author=author,
            created_at=datetime.utcnow()
        ))
        self.repo.db.commit()
        event_manager.trigger('add_post', post=post)

    def get(self, post_id):
        return self.repo.find_by_id(post_id)
