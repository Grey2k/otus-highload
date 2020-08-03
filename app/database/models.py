from dataclasses import dataclass, asdict

from flask_login import UserMixin
from pymysql import Date


@dataclass
class Model:

    def to_dict(self):
        return asdict(self)


@dataclass
class City(Model):
    name: str
    id: int = None


@dataclass
class Profile(Model):
    first_name: str
    last_name: str
    interests: str
    birth_date: Date
    gender: str
    city_id: int
    user_id: int
    id: int = None


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
        return f'{self.profile.first_name} {self.profile.last_name}'


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


@dataclass
class Dialog(Model):
    sender_id: int
    recipient_id: int
    message: str
    id: int = None
    created_at: Date = None
    updated_at: Date = None
