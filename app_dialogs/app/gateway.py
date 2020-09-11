import requests
from flask import current_app


class IncRequest:
    path = '/counters/chat/{chat_id}/messages/{profile_id}/inc'

    def __init__(self, base_url, chat_id, profile_id):
        self.url = base_url + self.path.format_map({
            'chat_id': chat_id,
            'profile_id': profile_id
        })

    def __str__(self):
        return self.url


class DecRequest:
    path = '/counters/chat/{chat_id}/messages/{profile_id}/dec'

    def __init__(self, base_url, chat_id, profile_id):
        self.url = base_url + self.path.format_map({
            'chat_id': chat_id,
            'profile_id': profile_id
        })

    def __str__(self):
        return self.url


class ChatRequest:
    path = '/counters/user/{profile_id}/chats'

    def __init__(self, base_url, profile_id):
        self.url = base_url + self.path.format_map({
            'profile_id': profile_id
        })

    def __str__(self):
        return self.url


class CountersGateway:

    def __init__(self, base_url):
        self.base_url = base_url

    def get_chats(self, profile_id):
        response = requests.get(str(ChatRequest(self.base_url, profile_id)))
        return response.json()

    def inc_chat_counter(self, chat_id, profile_id):
        try:
            response = requests.post(str(IncRequest(self.base_url, chat_id, profile_id)))
            return response.json()['success']
        except Exception as e:
            current_app.logger.exception(e)
        return False

    def dec_chat_counter(self, chat_id, profile_id):
        try:
            response = requests.post(str(DecRequest(self.base_url, chat_id, profile_id)))
            return response.json()['success']
        except Exception as e:
            current_app.logger.exception(e)
        return False
