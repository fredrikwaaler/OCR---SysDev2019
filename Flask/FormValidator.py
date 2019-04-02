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
        errors.append("New name cannot be empty.")

    else:
        # Check that name only contain letters
        for name in new_name.split():
            if not name.isalpha():
                errors.append("New name must be only letters")
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
        errors.append("Email is already in use.")

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
        errors.append("Passwords do not match.")

    # Validate password
    good_pass, pass_errors = validate_password(new_pass)
    if not good_pass:
        errors += pass_errors

    return len(errors) == 0, errors


def validate_password(password):
    errors = []
    if not re.match('^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,20}$', password):
        errors.append("Password should contain uppercase letter, lowercase letter, number, and be between 8"
                      " and 20 characters.")
    return len(errors) == 0, errors


def validate_email(email):
    errors = []
    if not re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email):
        errors.append("Email is not valid.")
    return len(errors) == 0, errors


def validate_new_fiken_user(login, password):
    errors = []
    # Validate email
    good_email, email_errors = validate_email(login)
    # Validate password, no need, cant login unless password is correct.
    # good_pass, pass_errors = validate_password(password)

    if not FikenManager.is_valid_credentials(login, password):
        errors.append("Not valid fiken credentials")
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
        email_errors += ["The email is already in use."]
    if not good_email:
        errors += email_errors

    good_name, name_errors = validate_new_name(name)
    if not good_name:
        errors += name_errors

    return len(errors) == 0, errors

