from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, RadioField
from wtforms.fields.html5 import DateField


class LoginForm(FlaskForm):
    email = StringField('Email')
    password = PasswordField('Password')


class ForgotForm(FlaskForm):
    email = StringField('Email')


class KjoopForm(FlaskForm):
    type_kjoop = RadioField('Label', choices=[('1','Kjøp fra leverandør'),('2','Kontantkjøp')])
    leverandor = SelectField('Leverandør', choices=[('1', 'Meny'), ('2', 'Kiwi')])
    fakturadato = DateField('Faktura')
    forfallsdato = DateField('Forfall')
    fakturanummer = StringField('Fakturanummer')

    tekst = StringField('Tekst')
    kostnadskonto = SelectField('Kostnadskonto', choices=[("100", "Matkonto"), ("101", "Utstyrskonto")])
    bruttobelop = StringField('Bruttobeløp')
    mva = SelectField("Mva", choices=[('1', '25%'), ('2', '12%')])
    nettobelop = StringField("Nettobeløp")

    betalt = BooleanField('Betalt')


class SalgForm(FlaskForm):
    type_salg = SelectField('Type', choices=[])
    kunde = SelectField('Kunde', choices=[])
    dato = StringField('Dato')
    kontakt = SelectField('kontakt', choices=[])
    kommentar = StringField('Kommentar')
    din_referanse = StringField('Din Referanse')
    kontonummer = StringField('Kontonummer')
    deres_referanse = StringField('Deres Referanse')

    beskrivelse = StringField('Beskrivelse')
    pris = StringField('Pris')
    antall = StringField('Antall')
    rabatt = StringField('Rabatt')
    mva = StringField('Mva')

class ProfilForm(FlaskForm):
    new_name = StringField('Name')
    new_email = StringField('Email')
    new_password = PasswordField('Nytt Passord')
    repeat_password = PasswordField('Gjenta Passord')