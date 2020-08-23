from injector import inject

from app.database.models import FriendshipStatus, Friendship, Subscribe
from app.database.repositories import FriendRepo, SubscribersRepo
from app.events import event_manager


class FriendshipManager:

    @inject
    def __init__(self, friend_repo: FriendRepo):
        self.friend_repo = friend_repo

    def start_friendship(self, source, destination):
        friendship = self.friend_repo.find_friendship(source, destination)
        if friendship:
            friendship.status = FriendshipStatus.CONFIRMED
        else:
            friendship = Friendship(source_id=source, destination_id=destination, status=FriendshipStatus.WAITING)
        self.friend_repo.save(friendship)
        self.friend_repo.db.commit()
        event_manager.trigger('friendship_started', friendship=friendship)
        return friendship

    def stop_friendship(self, source, destination):
        friendship = self.friend_repo.find_friendship(source, destination)
        if friendship is None:
            return
        self.friend_repo.remove(friendship)
        event_manager.trigger('friendship_stopped', source=source, destination=destination)


class SubscribeManager:

    @inject
    def __init__(self, subscribers_repo: SubscribersRepo):
        self.subscribers_repo = subscribers_repo

    def add_subscribe(self, subscriber, subscribe_to):
        self.subscribers_repo.save(
            Subscribe(subscriber=subscriber, subscribe_to=subscribe_to)
        )
        self.subscribers_repo.db.commit()
