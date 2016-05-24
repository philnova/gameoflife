from flask_wtf import Form
from wtforms import StringField, DateTimeField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length

class RenameBoardForm(Form):
    nickname = StringField('Nickname', validators=[DataRequired()])