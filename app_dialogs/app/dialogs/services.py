from flask import current_app
from injector import inject

from app.database.models import Dialog, DialogParticipant, DialogMessage
from app.database.repositories import DialogsRepo, DialogParticipantsRepo, DialogMessagesRepo, MessageStatusRepo
from app.dialogs.saga import NewUnreadMessageSaga, ReadMessageSaga


class DialogService:

    @inject
    def __init__(self, dialogs_repo: DialogsRepo, participants_repo: DialogParticipantsRepo):
        self.dialogs_repo = dialogs_repo
        self.participants_repo = participants_repo

    def create_dialog(self, initiator_id, profile_id):
        dialog = self.dialogs_repo.find_direct(initiator_id, profile_id)
        if dialog:
            return dialog

        dialog = self.dialogs_repo.save(Dialog(created_by=initiator_id))
        self.participants_repo.save(DialogParticipant(dialog_id=dialog.id, profile_id=initiator_id))
        self.participants_repo.save(DialogParticipant(dialog_id=dialog.id, profile_id=profile_id))
        self.dialogs_repo.db.commit()

        return dialog


class MessageService:

    @inject
    def __init__(self,
                 message_repo: DialogMessagesRepo,
                 participant_repo: DialogParticipantsRepo,
                 read_saga: ReadMessageSaga,
                 create_saga: NewUnreadMessageSaga):
        self.message_repo = message_repo
        self.participant_repo = participant_repo
        self.read_saga = read_saga
        self.create_saga = create_saga

    def add_message(self, dialog_id, sender_id, text):
        message = self.__create_message(dialog_id, sender_id, text)
        for participant in self.__find_participants(dialog_id, sender_id):
            try:
                self.create_saga.execute(message, participant)
            except Exception as e:
                current_app.logger.exception(e)
        return message

    def __create_message(self, dialog_id, sender_id, text):
        message = self.message_repo.save(DialogMessage(
            sender_id=sender_id,
            text=text,
            dialog_id=dialog_id,
        ))
        self.message_repo.db.commit()
        return message

    def __find_participants(self, dialog_id, sender_id):
        return [p for p in self.participant_repo.find_by_dialog(dialog_id) if p.profile_id != sender_id]

    def read_message(self, dialog_id, message_id, profile_id):
        return self.read_saga.execute(dialog_id, message_id, profile_id)
