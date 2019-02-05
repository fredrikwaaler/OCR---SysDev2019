from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import ImputRequired

class ForgotForm(Form):
    email = StringField('email')