from flask_bcrypt import Bcrypt
from string import ascii_letters, digits
import random


class PasswordHandler:
    """
    A simple class for handling password.
    This includes hashing them, and comparing plaintext with hashed passwords.
    """

    _bcrypt_agent = Bcrypt()  # A bcrypt-agent shared between all password-handlers.

    @staticmethod
    def generate_hashed_password(password):
        """
        This method hashes the provided clear-text password using bcrypt.
        :param password: The password to be hashed.
        :return: A hashed version of the password, using bcrypt.
        """
        return str(PasswordHandler._bcrypt_agent.generate_password_hash(password).decode('utf-8'))

    @staticmethod
    def compare_hash_with_text(hashed_password, text_password):
        """
        Compares a hashed password with a clear-text password for verification.
        :param hashed_password: The hashed password
        :param text_password: The clear-text password
        :return: True if the passwords match, else false.
        """
        matching = PasswordHandler._bcrypt_agent.check_password_hash(hashed_password, text_password)
        return matching

    @staticmethod
    def generate_random_password():
        """
        Generates a random password of upper- and lowercase letters and digits.
        Password has random length from 6 to 9 (including boundaries).
        :return: Returns a random password.
        """
        password = ""
        valid_chars = ascii_letters + digits
        for i in range(random.randint(6, 9)):
            password += random.choice(valid_chars)
        return password
