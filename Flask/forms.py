from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField

class LoginForm(FlaskForm):
    email = StringField('Email')
    password = PasswordField('Password')

class ForgotForm(FlaskForm):
    email = StringField('Email')

class KjopForm(FlaskForm):
    type_kjop = StringField('Type Kjøp')
    leverandor = SelectField('Leverandør', choices=[('1', 'Meny'), ('2', 'Kiwi')])
    fakturadato = StringField('Faktura')
    forfallsdato = StringField('Forfall')
    fakturanummer = StringField('Fakturanummer')

    tekst = StringField('Tekst')
    kostnadskonto = SelectField('Kostnadskonto', choices=[("100", "Matkonto"), ("101", "Utstyrskonto")]) 
    bruttobelop = StringField('Bruttobeløp')
    mva = StringField("Mva")
    nettobelop = StringField("Nettobeløp")

    betalt = BooleanField('Betalt')

