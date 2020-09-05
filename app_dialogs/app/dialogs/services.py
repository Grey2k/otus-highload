from injector import inject

from app.database.models import Dialog, DialogParticipant
from app.database.repositories import DialogsRepo, DialogParticipantsRepo


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
