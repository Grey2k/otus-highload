from flask import render_template, request, Blueprint, redirect, url_for
from flask_login import login_required, current_user

from app.database.models import DialogMessage, Dialog, DialogParticipant
from app.database.repositories import DialogsRepo, DialogMessagesRepo, DialogParticipantsRepo
from app.dialogs.forms import MessageForm

bp = Blueprint('dialogs', __name__, url_prefix='/dialogs')


@bp.route('/')
@login_required
def index(dialogs_repo: DialogsRepo):
    return render_template(
        'dialogs/index.html',
        dialogs=dialogs_repo.find_dialogs(current_user.profile_id),
    )


@bp.route('/direct/<profile_id>')
@login_required
def direct(profile_id: int, dialogs_repo: DialogsRepo, participants_repo: DialogParticipantsRepo):
    current_profile = current_user.profile_id
    dialog = dialogs_repo.find_direct(current_profile, profile_id)
    if not dialog:
        dialog = Dialog(created_by=current_profile)
        dialogs_repo.save(dialog)
        participants_repo.save(DialogParticipant(dialog_id=dialog.id, profile_id=current_profile))
        participants_repo.save(DialogParticipant(dialog_id=dialog.id, profile_id=profile_id))
        dialogs_repo.db.commit()

    return redirect(url_for('dialogs.detail', dialog_id=dialog.id))


@bp.route('/<dialog_id>', methods=['GET', 'POST'])
@login_required
def detail(dialog_id: int, dialogs_repo: DialogsRepo, messages_repo: DialogMessagesRepo):
    form = MessageForm(request.form)
    if request.method == 'POST' and form.validate():
        messages_repo.save(DialogMessage(
            sender_id=current_user.profile_id,
            text=form.message.data,
            dialog_id=dialog_id,
        ))
        dialogs_repo.db.commit()
        return redirect(url_for('dialogs.detail', dialog_id=dialog_id))
    messages = messages_repo.find_by_dialog(dialog_id)
    dialog = dialogs_repo.find_by_id(dialog_id)
    return render_template(
        'dialogs/detail.html',
        messages=messages,
        dialog=dialog,
        form=form
    )

