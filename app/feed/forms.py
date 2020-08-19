from wtforms import Form, StringField


class PostAddForm(Form):
    content = StringField('Content')
