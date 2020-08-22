from injector import inject

from app.feed.providers import FeedProvider


class FeedService:

    @inject
    def __init__(self, feed_provider: FeedProvider):
        self.feed_provider = feed_provider

    def load(self, feed_id, page, count):
        return self.feed_provider.load(feed_id, page, count)
