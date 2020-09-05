import abc
from typing import List

from flask import jsonify

from app.database.models import DialogMessage, Dialog


class ResourceDto(abc.ABC):

    @abc.abstractmethod
    def as_dict(self):
        pass


def resource(dto: ResourceDto):
    return dto.as_dict()


class DialogListDto(ResourceDto):

    def __init__(self, profile_id, dialogs: List[Dialog]):
        self.profile_id = profile_id
        self.dialogs = dialogs

    def as_dict(self):
        return {
            'items': [DialogDto(self.profile_id, dialog).as_dict() for dialog in self.dialogs]
        }


class DialogDto(ResourceDto):

    def __init__(self, profile_id, dialog: Dialog):
        self.profile_id = profile_id
        self.dialog = dialog

    def as_dict(self):
        return {
            'id': self.dialog.id,
            'name': self.dialog.name(self.profile_id)
        }


class MessageDto(ResourceDto):
    def __init__(self, message: DialogMessage):
        self.message = message

    def as_dict(self):
        return {
            'id': self.message.id,
            'text': self.message.text,
            'created_at': self.message.created_at,
            'sender_id': self.message.sender_id,
        }


class ChatDto(ResourceDto):

    def __init__(self, profile_id, dialog: Dialog, messages: List[DialogMessage]):
        self.profile_id = profile_id
        self.dialog = dialog
        self.messages = messages

    def as_dict(self):
        return {
            'dialog': DialogDto(self.profile_id, self.dialog).as_dict(),
            'messages': [MessageDto(message).as_dict() for message in self.messages]
        }


class ErrorsDto(ResourceDto):
    def __init__(self, errors):
        self.errors = errors

    def as_dict(self):
        return {
            'success': False,
            'errors': self.errors
        }


class CreatedDto(ResourceDto):
    def __init__(self, entity):
        self.entity = entity

    def as_dict(self):
        return {
            'success': True,
            'id': self.entity.id
        }
