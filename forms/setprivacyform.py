from flask_wtf import Form
from wtforms import BooleanField, RadioField
from wtforms.validators import DataRequired, Length

class SetPrivacyForm(Form):
    #shared = BooleanField('Check to make this board publicly shared')
    privacy = RadioField('Set Privacy for this board', validators=[DataRequired()], choices=[('share', 'Shared'),('private', 'Private')], default='private')
