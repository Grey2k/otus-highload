from injector import inject

from app.database.models import DialogMessage, DialogParticipant, MessageStatus
from app.database.repositories import MessageStatusRepo
from app.gateway import CountersGateway


class NewUnreadMessageSaga:

    @inject
    def __init__(self, status_repo: MessageStatusRepo, counters_gw: CountersGateway):
        self.status_repo = status_repo
        self.counters_gw = counters_gw

    def execute(self, message: DialogMessage, participant: DialogParticipant):
        ms = self.__create_unread_message(message.id, participant.profile_id)
        is_success = self.__increase_counters(message.dialog_id, participant.profile_id)
        if not is_success:
            self.__set_read_status(ms)
            return False

        return message

    def __increase_counters(self, dialog_id, profile_id):
        return self.counters_gw.inc_chat_counter(dialog_id, profile_id)

    def __create_unread_message(self, message_id, profile_id):
        message_status = self.status_repo.save(self.status_repo.model_class(
            message_id=message_id,
            recepient_id=profile_id,
            status=MessageStatus.STATUS_NOT_READ,
        ))
        self.status_repo.db.commit()
        return message_status

    def __set_read_status(self, ms: MessageStatus):
        ms.status = MessageStatus.STATUS_NOT_READ
        self.status_repo.save(ms)
        self.status_repo.db.commit()


class ReadMessageSaga:

    @inject
    def __init__(self, status_repo: MessageStatusRepo, counters_gw: CountersGateway):
        self.status_repo = status_repo
        self.counters_gw = counters_gw

    def execute(self, dialog_id, message_id, profile_id):
        ms = self.__find_unread_message(message_id, profile_id)
        if not ms:
            return False
        self.__set_message_status(ms, MessageStatus.STATUS_READ)
        is_success = self.__decrease_counters(dialog_id, profile_id)
        if not is_success:
            self.__set_message_status(ms, MessageStatus.STATUS_NOT_READ)
            return False
        return True

    def __find_unread_message(self, message_id, profile_id):
        return self.status_repo.find_unread(profile_id, message_id)

    def __set_message_status(self, ms: MessageStatus, status: str):
        ms.status = status
        self.status_repo.save(ms)
        self.status_repo.db.commit()

    def __decrease_counters(self, dialog_id, profile_id):
        return self.counters_gw.dec_chat_counter(dialog_id, profile_id)
