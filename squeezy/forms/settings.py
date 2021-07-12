from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class SettingsForm(FlaskForm):
    http_port = StringField('Proxy Listening Port',
                            validators=[DataRequired()])
