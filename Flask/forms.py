from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, RadioField, DecimalField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, InputRequired


class LoginForm(FlaskForm):
    """
    Form for login (email and password).
    """
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class ForgotForm(FlaskForm):
    """
    Form for email if password is forgotten.
    """
    email = StringField('Email')


class PurchaseForm(FlaskForm):
    """
    Purchase form. Contains fields for detailing info about a purchase.
    """
    purchase_type = RadioField('Label', choices=[('0', ''), ('1','Kjøp fra leverandør'),('2','Kontantkjøp')])
    invoice_date = DateField('Faktura', validators=[DataRequired(), InputRequired()])
    maturity_date = DateField('Forfall')
    invoice_number = StringField('Fakturanummer')

    text = StringField('Tekst')
    gross_amount = DecimalField('Bruttobeløp')
    net_amount = DecimalField("Nettobeløp")

    paid = BooleanField('Betalt')
    account = SelectField('Betalt fra', choices=[('0', ''), ('1', 'Bankkonto'),('2', 'Kontanter') ])
    amount = DecimalField('Amount')


class SaleForm(FlaskForm):
    """
    Sales form. Contains fields for detailing info about a sale.
    """
    sale_type = SelectField('Type', choices=[('0', ''), ('1', 'Faktura')])
    date = DateField('Dato', validators=[DataRequired(), InputRequired()])
    days_to_maturity = StringField("Dager til forfalll")
    comment = TextAreaField('Kommentar')
    account_number = SelectField('Kontonummer', choices=[('1', 'Demokonto')])

    contact = SelectField('Kontakt', choices=[('0', ''), ("1", "Kontakt 1"), ("2", "Kontakt 2") ])
    our_reference = StringField('Din Referanse')
    their_reference = StringField('Deres Referanse')

    description = StringField('Beskrivelse')
    
    product = SelectField('Produkt', choices=[("1", "KAKE")])
    price = StringField('Pris')
    amount = StringField('Antall')
    discount = StringField('Rabatt')
    vat = StringField('Mva')


class ProfileForm(FlaskForm):
    """
    Form for the profile-page.
    """
    # For changing name
    new_name = StringField('Name')
    # For changing email
    new_email = StringField('Email')
    # For changing password
    new_password = PasswordField('Nytt Passord')
    repeat_password = PasswordField('Gjenta Passord')


class FikenModalForm(FlaskForm):
    """
    Modal form for changing fiken-user.
    """
    # For changing fiken-user
    email = StringField('Email')
    password = PasswordField('Passord')


class ConfirmPasswordForm(FlaskForm):
    """
    Form for confirming password.
    """
    password = PasswordField('Bekreft Passordet')


class CustomerForm(FlaskForm):
    """
    Form for creating a new contact
    """
    name = StringField('Navn', validators=[InputRequired(), DataRequired()])
    org_nr = StringField('Org.nr')
    email = StringField('Epost')
    telephone = StringField('Telefonnummer')
    account_number = StringField('Kontonummer')
    member_number = DecimalField('Medlemsnummer') #Stepper?
    country = StringField('Land')
    address1 = StringField('Adresse 1')
    address2 = StringField('Adresse 2')
    zip_code = StringField('Postnummer')
    postal_area = StringField('Poststed')


class AccountForm(FlaskForm):
    """
    Form for creating accounts.
    """
    account_name = StringField('Navn')
    account_type = SelectField('Type', choices=[('Vanlig', 'Vanlig'), ('Uvanlig', 'Utenlandsk / betalingstjeneste')])
    account_bank = SelectField('Bank', choices=[('0', ''), ('1', 'Stripe'), ('2', 'PayPal')])
    account_number = StringField('Bankkontonummer')


class SignUpForm(FlaskForm):
    """
    Form for sign-up.
    """
    name = StringField('Name')
    email = StringField('Email')
    admin = BooleanField('Admin')
