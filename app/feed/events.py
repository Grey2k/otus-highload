from app.database.models import Post
from app.events import event_manager
from app.feed.tasks import add_post


@event_manager.subscribe('add_post')
def update_subscribers_feed(app, post: Post):
    add_post.delay(post.author_id, post.id)
