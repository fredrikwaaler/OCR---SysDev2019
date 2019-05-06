import re
from user import User
from FikenManager import FikenManager


def validate_new_name(new_name):
    """
    Validates a new name upon change of name.
    Only the most important error will be returned, if several.
    Returns a tuple, first value is True if validated, else False.
    Second value is a list containing the error, if any, else the list is empty.
    :param new_name:
    :return: A tuple containing info of whether or not the form was validated and a list of any errors.
    """
    errors = []
    if new_name.strip() == "":  # Check that name is not empty
        errors.append("Obs: Det nye navnet kan ikke være tomt.")

    else:
        # Check that name only contain letters
        for name in new_name.split():
            if not name.isalpha():
                errors.append("Obs: Det nye navnet kan kun inneholde bokstaver.")
                break

    return len(errors) == 0, errors


def validate_new_email(new_email):
    """
    Validates a new email upon change of email.
    Only the most important error will be returned, if several.
    Returns a tuple, first value is True if validated, else False.
    Second value is a list containing the error, if any, else the list is empty.
    :param new_email: The new email.
    :return: A tuple containing info of whether or not the form was validated and a list of any errors.
    """
    errors = []
    # Validate email
    good_email, email_errors = validate_email(new_email)
    if not good_email:
        errors += email_errors
    # Check whether the email is already in use.
    elif User.Dm.get_user_info_by_email(new_email):
        errors.append("Obs: Denne eposten er allerede i bruk, vennligst velg en annen.")

    return len(errors) == 0, errors


def validate_new_password(new_pass, repeat_new_pass):
    """
    Validates new password upon change of password.
    Only the most important error will be returned, if several.
    Returns a tuple, first value is True if validated, else False.
    Second value is a list containing the error, if any, else the list is empty.
    :param new_pass: The new password
    :param repeat_new_pass: The "repeated" new password.
    :return: A tuple containing info of whether or not the form was validated and a list of any errors.
    """
    errors = []
    if new_pass != repeat_new_pass:
        errors.append("Obs: Passordene samsvarer ikke.")

    # Validate password
    good_pass, pass_errors = validate_password(new_pass)
    if not good_pass:
        errors += pass_errors

    return len(errors) == 0, errors


def validate_password(password):
    errors = []
    if not re.match('^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,20}$', password):
        errors.append( "Obs: Passordet må inneholde store bokstaver, små bokstaver og tall. Passordet må være mellom"
                       " 8 og 20 tegn.")
    return len(errors) == 0, errors


def validate_email(email):
    errors = []
    if not re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email):
        errors.append("Obs: Eposten er ikke gyldig.")
    return len(errors) == 0, errors


def validate_new_fiken_user(login, password):
    errors = []
    # Validate email
    good_email, email_errors = validate_email(login)
    # Validate password, no need, cant login unless password is correct.
    # good_pass, pass_errors = validate_password(password)

    if not FikenManager.is_valid_credentials(login, password):
        errors.append("Obs: Eposten eller passordet du har angitt er ikke riktig. Prøv på nytt.")
    elif not good_email:
        errors += email_errors
    # elif not good_pass:
        # errors += pass_errors

    return len(errors) == 0, errors


def validate_sign_up(name, email):
    errors = []
    # Validate email
    good_email, email_errors = validate_email(email)
    if User.user_exists(email):
        good_email = False
        email_errors += ["Eposten er allerede i bruk."]
    if not good_email:
        errors += email_errors

    good_name, name_errors = validate_new_name(name)
    if not good_name:
        errors += name_errors

    return len(errors) == 0, errors


def validate_sales_form(form):
    errors = []

    # Validate that all line totals are positive
    prices = form.getlist('price') + form.getlist('price_free')
    quantities = form.getlist('quantity') + form.getlist('quantity_free')
    total = 0
    for price in prices:
        # JS ensures that only numerical values can be put in price fields. Safely typecast.
        total += float(price)

    if not total >= 0:
        errors.append("Obs: Totalbeløpet må være positivt")

    # No point in checking for errors in quantities if one is already found
    if len(errors) == 0:
        for quantity in quantities:
            # JS ensures safe typecast.
            if not float(quantity) > 0:
                errors.append("Obs: Kvantitet kan ikke være null.")

    return len(errors) == 0, errors


def validate_purchase_form(form):
    errors = []

    # Validate that all lines have a positive sum
    grosses = form.getlist('gross_amount')
    total = 0
    for gross in grosses:
        total += float(gross) # JS ensures that only numerical values can be put in price fields.

    if not total >= 0:
        errors.append("Obs: Totalbeløpet må være positivt")

    return len(errors) == 0, errors
