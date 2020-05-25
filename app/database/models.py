from dataclasses import dataclass, asdict

from pymysql import Date


@dataclass
class Model:

    def to_dict(self):
        return asdict(self)


@dataclass
class City(Model):
    id: int
    name: str


@dataclass
class User(Model):
    id: int
    email: str
    password: str


@dataclass
class Profile(Model):
    id: int
    first_name: str
    last_name: str
    interests: str
    birth_date: Date
    gender: str
    city_id: int
    user_id: int


@dataclass
class Friendship(Model):
    source_id: int
    destination_id: int
    status: int
    id: int = None
    created_at: Date = None

    @property
    def confirmed(self):
        return self.status == 1

    def wait_confirmation(self, profile_id):
        return self.destination_id == profile_id and self.status == 0
