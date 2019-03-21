from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, RadioField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired


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
    dato = DateField('Dato')
    dager_til_forfall = StringField("Dager til forfalll")
    kommentar = StringField('Kommentar')
    kontonummer = StringField('Kontonummer')

    kunde = SelectField('Kunde', choices=[])

    kontakt = SelectField('Kontakt', choices=[("1", "Kontakt 1"), ("2", "Kontakt 2") ])
    vaar_referanse = StringField('Din Referanse')
    deres_referanse = StringField('Deres Referanse')

    beskrivelse = StringField('Beskrivelse')
    
    produkt = SelectField('Produkt', choices=[("1", "KAKE")])
    pris = StringField('Pris')
    antall = StringField('Antall')
    rabatt = StringField('Rabatt')
    mva = StringField('Mva')


class ProfilForm(FlaskForm):
    # For changing name
    new_name = StringField('Name')
    # For changing email
    new_email = StringField('Email')
    # For changing password
    new_password = PasswordField('Nytt Passord')
    repeat_password = PasswordField('Gjenta Passord')


class FikenModalForm(FlaskForm):
    # For changing fiken-user
    email = StringField('Email')
    password = PasswordField('Passord')


class CustomerForm(FlaskForm):
    navn = StringField('Navn')
    org_nr = StringField('Org.nr')
    email = StringField('Epost')
    telefonnummer = StringField('Telefonnummer')
    kontonummer = StringField('Kontonummer')
    #CHECKBOXES
    medlemsnummer = StringField('Medlemsnummer') #Stepper?
    land = StringField('Land')
    adresse1 = StringField('Adresse 1')
    adresse2 = StringField('Adresse 2')
    postnummer = StringField('Postnummer')
    poststed = StringField('Poststed')


class SignUpForm(FlaskForm):
    first_name = StringField('First name')
    last_name = StringField('Last name')
    email = StringField('Email')
    password = PasswordField('Password')
    repeat_password = PasswordField('Password')
