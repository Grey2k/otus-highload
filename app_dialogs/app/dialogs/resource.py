from typing import List

from flask import jsonify

from app.database.models import DialogMessage, Dialog


def dialog_list(profile_id, items):
    return jsonify({
        'success': True,
        'items': _dialog_list(profile_id, items)
    })


def _dialog_list(profile_id, items: List[Dialog]):
    return [_dialog_detail(profile_id, item) for item in items]


def dialog_detail(profile_id, dialog: Dialog, messages: List[DialogMessage]):
    return jsonify({
        'success': True,
        'dialog': _dialog_detail(profile_id, dialog),
        'messages':  _dialog_messages(messages)
    })


def _dialog_detail(profile_id, dialog: Dialog):
    return {
        'id': dialog.id,
        'name': dialog.name(profile_id)
    }


def _dialog_messages(messages: List[DialogMessage]):
    return [
        {
            'id': message.id,
            'text': message.text,
            'created_at': message.created_at,
            'sender_id': message.sender_id,
        }
        for message in messages
    ]
