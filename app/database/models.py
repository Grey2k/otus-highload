from dataclasses import dataclass, asdict, fields
from typing import List

from flask_login import UserMixin
from pymysql import Date


@dataclass
class Model:

    def to_dict(self):
        return asdict(self)

    @classmethod
    def fields(cls):
        return [field.name for field in fields(cls)]


@dataclass
class City(Model):
    name: str
    id: int = None


@dataclass
class Profile(Model):
    first_name: str
    last_name: str
    interests: str = None
    birth_date: Date = None
    gender: str = None
    city_id: int = None
    user_id: int = None
    id: int = None

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'


@dataclass
class User(UserMixin, Model):
    email: str
    password: str
    id: int = None
    profile: Profile = None

    @property
    def profile_id(self):
        return self.profile.id if self.profile else None

    @property
    def name(self):
        return f'{self.profile.name}'


class FriendshipStatus:
    WAITING = 0
    CONFIRMED = 1


@dataclass
class Friendship(Model):
    source_id: int
    destination_id: int
    status: int
    id: int = None
    created_at: Date = None

    @property
    def confirmed(self):
        return self.status == FriendshipStatus.CONFIRMED

    def wait_confirmation(self, profile_id):
        return self.destination_id == profile_id and self.status == FriendshipStatus.WAITING


class DialogType:
    DIRECT = 1


@dataclass
class Dialog(Model):
    created_by: int
    type: int = DialogType.DIRECT
    id: int = None
    created_at: Date = None
    participants: List[Profile] = None

    def name(self, skip_profile=None):
        if not self.participants:
            return 'Empty dialog'
        participants = self.participants
        if skip_profile:
            participants = filter(lambda p: p.id != skip_profile, participants)
        return ', '.join(map(lambda p: p.name, participants))


@dataclass
class DialogMessage(Model):
    text: str
    sender_id: int
    dialog_id: int
    id: int = None
    created_at: Date = None


@dataclass
class DialogParticipant(Model):
    profile_id: int
    dialog_id: int


@dataclass
class Post(Model):
    author_id: int
    content: str
    id: int = None
    created_at: Date = None
    updated_at: Date = None
    author: Profile = None


@dataclass
class FeedItem(Model):
    feed_id: int
    author: str
    author_id: int
    content: str
    id: int = None
    publish_date: Date = None


@dataclass
class Subscribe(Model):
    subscriber: int
    subscribe_to: int
    id: int = None
