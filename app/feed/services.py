from datetime import datetime

from injector import inject

from app.database.models import Profile, Post
from app.database.repositories import PostsRepo
from app.feed.providers import FeedProvider


class FeedService:

    @inject
    def __init__(self, feed_provider: FeedProvider):
        self.feed_provider = feed_provider

    def load(self, feed_id, page, count):
        return self.feed_provider.load(feed_id, page, count)

    def add_post(self, feed_id, post):
        self.feed_provider.add(feed_id, post)


class PostService:

    @inject
    def __init__(self, repo: PostsRepo, feed: FeedService):
        self.repo = repo
        self.feed = feed

    def create(self, author: Profile, content: str):
        post = self.repo.save(Post(
            author_id=author.id,
            content=content,
            author=author,
            created_at=datetime.utcnow()
        ))
        self.repo.db.commit()
        self.feed.add_post(author.id, post)
