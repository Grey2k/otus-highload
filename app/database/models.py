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
