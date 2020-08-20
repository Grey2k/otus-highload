from wtforms import Form, StringField, validators


class PostAddForm(Form):
    content = StringField('Content', [validators.DataRequired()])
