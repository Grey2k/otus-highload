from wtforms import Form, StringField, IntegerField, validators


class MessageForm(Form):
    message = StringField('Message')


class DialogForm(Form):
    type = StringField('type')
    profile_id = IntegerField('profile_id', [validators.DataRequired()])
