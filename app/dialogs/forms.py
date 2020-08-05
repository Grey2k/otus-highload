from wtforms import Form, StringField


class MessageForm(Form):
    message = StringField('Message')
