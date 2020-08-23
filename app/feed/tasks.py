from app import di
from app.celery import celery
from app.feed.services import FeedService, PostService
from app.friends import SubscribeManager


@celery.task
def add_post(author_id, post_id):
    subscribe_manager: SubscribeManager = di.get(SubscribeManager)

    for items in subscribe_manager.get_subscribers_generator(author_id):
        update_feeds.delay(feed_ids=[item.subscriber for item in items], post_id=post_id)


@celery.task
def update_feeds(feed_ids, post_id):
    post_service: PostService = di.get(PostService)
    post = post_service.get(post_id)

    feed_service: FeedService = di.get(FeedService)
    for feed_id in feed_ids:
        feed_service.add_post(feed_id, post)
