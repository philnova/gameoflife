from flask_wtf import Form
from wtforms import StringField, DateTimeField, SelectField, IntegerField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length

class SaveForm(Form):
    nickname = StringField('Nickname for this board', validators=[DataRequired()])
    shared = BooleanField('Check to make this board publicly shared')
    # xdim = IntegerField('X dimension', validators=[DataRequired()])
    # ydim = IntegerField('Y dimension', validators=[DataRequired()])
    # seed = StringField('Seed', validators=[DataRequired()])
    # rules = StringField('Rules', validators=[DataRequired()])
