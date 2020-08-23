from app import di
from app.database.models import Friendship, FriendshipStatus
from app.events import event_manager
from app.friends.services import SubscribeManager


@event_manager.subscribe('friendship_started')
def create_subscribers(app, friendship: Friendship):
    if friendship.status != FriendshipStatus.CONFIRMED:
        return

    subscribe: SubscribeManager = di.get(SubscribeManager)
    subscribe.add_subscribe(friendship.source_id, friendship.destination_id)
    subscribe.add_subscribe(friendship.destination_id, friendship.source_id)
