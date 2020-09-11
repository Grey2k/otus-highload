import requests
from flask import request, Blueprint
from flask_jwt import jwt_required, current_identity
from werkzeug.datastructures import MultiDict

from app.database.repositories import DialogsRepo, DialogMessagesRepo
from app.dialogs.form import MessageForm, DialogForm
from app.dialogs.resource import resource, DialogListDto, ChatDto, ErrorsDto, CreatedDto, SuccessDto
from app.dialogs.services import DialogService, MessageService
from app.gateway import CountersGateway

v1 = Blueprint('dialogs_v1', __name__, url_prefix='/v1')


@v1.route('/')
@jwt_required()
def index(dialogs_repo: DialogsRepo, counters_gw: CountersGateway):
    profile_id = int(current_identity)
    chats_counters = counters_gw.get_chats(profile_id)
    return resource(DialogListDto(profile_id, dialogs_repo.find_dialogs(profile_id), chats_counters['items']))


@v1.route('/', methods=['POST'])
@jwt_required()
def create(dialog_service: DialogService):
    profile_id = int(current_identity)
    form = DialogForm(MultiDict(request.get_json()))
    if not form.validate():
        return resource(ErrorsDto(form.errors))

    dialog = dialog_service.create_dialog(profile_id, form.profile_id.data)

    return resource(CreatedDto(dialog))


@v1.route('/<int:dialog_id>', methods=['GET'])
@jwt_required()
def detail(dialog_id: int, dialogs_repo: DialogsRepo, messages_repo: DialogMessagesRepo):
    profile_id = int(current_identity)
    messages = messages_repo.find_by_dialog(dialog_id, profile_id)
    dialog = dialogs_repo.find_by_id(dialog_id)
    return resource(ChatDto(profile_id, dialog, messages))


@v1.route('/<int:dialog_id>', methods=['POST'])
@jwt_required()
def add_message(dialog_id: int, ms: MessageService):
    form = MessageForm(MultiDict(request.get_json()))
    if not form.validate():
        return resource(ErrorsDto(form.errors))

    message = ms.add_message(dialog_id, int(current_identity), form.message.data)
    return resource(CreatedDto(message))


@v1.route('/<int:dialog_id>/<int:message_id>', methods=['POST'])
@jwt_required()
def read_message(dialog_id: int, message_id: int, ms: MessageService):
    status = ms.read_message(dialog_id, message_id, int(current_identity))
    return resource(SuccessDto(status))
