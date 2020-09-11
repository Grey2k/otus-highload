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

    def __init__(self, profile_id, dialogs: List[Dialog], counters: dict):
        self.profile_id = profile_id
        self.dialogs = dialogs
        self.counters = counters

    def as_dict(self):
        return {
            'items': [
                DialogDto(self.profile_id, dialog, self.counters.get(str(dialog.id))).as_dict()
                for dialog in self.dialogs]
        }


class DialogDto(ResourceDto):

    def __init__(self, profile_id, dialog: Dialog, unread_count: int = None):
        self.profile_id = profile_id
        self.dialog = dialog
        self.unread_count = unread_count

    def as_dict(self):
        return {
            'id': self.dialog.id,
            'name': self.dialog.name(self.profile_id),
            'unread_count': self.unread_count
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
            'is_read': self.message.is_read,
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


class SuccessDto(ResourceDto):
    def __init__(self, status):
        self.status = status

    def as_dict(self):
        return {
            'success': self.status,
        }
