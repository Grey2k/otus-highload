from dataclasses import dataclass, asdict, fields
from typing import List

from pymysql import Date


@dataclass
class Model:

    def to_dict(self):
        return asdict(self)

    @classmethod
    def fields(cls):
        return [field.name for field in fields(cls)]


@dataclass
class Profile(Model):
    first_name: str
    last_name: str
    id: int = None

    @property
    def name(self):
        return f'{self.last_name} {self.first_name}'


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
