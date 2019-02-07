from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField

class ForgotForm(FlaskForm):
    email = StringField('Email')
