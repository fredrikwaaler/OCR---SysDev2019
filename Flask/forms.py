from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, RadioField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class ForgotForm(FlaskForm):
    email = StringField('Email')


class PurchaseForm(FlaskForm):
    purchase_type = RadioField('Label', choices=[('1','Kjøp fra leverandør'),('2','Kontantkjøp')])
    supplier = SelectField('Leverandør', choices=[('1', 'Meny'), ('2', 'Kiwi')])
    invoice_date = DateField('Faktura')
    maturity_date = DateField('Forfall')
    invoice_number = StringField('Fakturanummer')

    text = StringField('Tekst')
    billing_account = SelectField('Kostnadskonto', choices=[("100", "Matkonto"), ("101", "Utstyrskonto")])
    gross_amount = StringField('Bruttobeløp')
    vat = SelectField("Mva", choices=[('1', '25%'), ('2', '12%')])
    net_amount = StringField("Nettobeløp")

    paid = BooleanField('Betalt')


class SaleForm(FlaskForm):
    sale_type = SelectField('Type', choices=[])
    date = DateField('Dato')
    days_to_maturity = StringField("Dager til forfalll")
    comment = StringField('Kommentar')
    account_number = StringField('Kontonummer')

    contact = SelectField('Kontakt', choices=[("1", "Kontakt 1"), ("2", "Kontakt 2") ])
    our_reference = StringField('Din Referanse')
    their_reference = StringField('Deres Referanse')

    description = StringField('Beskrivelse')
    
    product = SelectField('Produkt', choices=[("1", "KAKE")])
    price = StringField('Pris')
    amount = StringField('Antall')
    discount = StringField('Rabatt')
    vat = StringField('Mva')


class ProfileForm(FlaskForm):
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


class ConfirmPasswordForm(FlaskForm):
    password = PasswordField('Bekreft Passordet')


class CustomerForm(FlaskForm):
    name = StringField('Navn')
    org_nr = StringField('Org.nr')
    email = StringField('Epost')
    telephone = StringField('Telefonnummer')
    account_number = StringField('Kontonummer')
    #CHECKBOXES
    member_number = StringField('Medlemsnummer') #Stepper?
    country = StringField('Land')
    address1 = StringField('Adresse 1')
    address2 = StringField('Adresse 2')
    zip_code = StringField('Postnummer')
    postal_area = StringField('Poststed')


class SignUpForm(FlaskForm):
    name = StringField('Name')
    email = StringField('Email')
    admin = BooleanField('Admin')
