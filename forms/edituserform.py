from flask_wtf import Form
from wtforms import StringField, DateTimeField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length

class EditUserForm(Form):
    name = StringField('Username', validators=[DataRequired()])