from injector import inject

from app.database.models import FriendshipStatus, Friendship
from app.database.repositories import FriendRepo


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
        return friendship

    def stop_friendship(self, source, destination):
        friendship = self.friend_repo.find_friendship(source, destination)
        if friendship:
            self.friend_repo.remove(friendship)
