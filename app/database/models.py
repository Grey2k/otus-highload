from dataclasses import dataclass

from pymysql import Date


@dataclass
class City:
    id: int
    name: str


@dataclass
class User:
    id: int
    email: str
    password: str


@dataclass
class Profile:
    id: int
    first_name: str
    last_name: str
    interests: str
    birth_date: Date
    gender: str
    city_id: int
    user_id: int


@dataclass
class Friendship:
    id: int
    source_id: int
    destination_id: int
    status: int
    created_at: Date

    @property
    def confirmed(self):
        return self.status == 1

    def wait_confirmation(self, profile_id):
        return self.destination_id == profile_id and self.status == 0
