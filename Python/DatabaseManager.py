from flask_bcrypt import Bcrypt
from Database import CursorFromConnectionPool


class DatabaseManager:

    def __init__(self, app=None, **kwargs):
        """
        The DatabaseManager is a simple class for managing and storing data to the database.
        The class also provides mean for safe storing and verification of passwords.
        :param app: Any flask app object to wrap in the Bcrypt. Defaults to none.
        :param kwargs: host, database, user, password, port (for external connections)
        Example: host="localhost", database="Sakila", user="postgres", password="mypass123"
        """
        self._database = CursorFromConnectionPool(**kwargs)
        self._bcrypt_agent = Bcrypt(app)

    def store_user_info(self, email, password, fiken_username=None, fiken_password=None,
                        first_name=None, last_name=None):
        """
        Creates a record in the database, storing the specified email and a hashed version of the supplied password.
        :param email: The email used to login the user
        :param password: The password to hash and store
        :param fiken_username: The users fiken login
        :param fiken_password: The users fiken password
        :param first_name: Users first name
        :param last_name: Users last name
        """
        # First, hash the password before storing
        hashed_password = self._generate_hashed_password(password)

        # Then, store the record in the database
        with self._database as cursor:
            try:
                cursor.execute('INSERT INTO UserInfo VALUES (%s, %s, %s, %s, %s, %s)',
                                    (email, hashed_password, fiken_username, fiken_password, first_name, last_name))
                return True
            except:
                return False

    def authenticate_login(self, email, password):
        """
        Checks whether a requested login is valid.
        I.e. does the email and password correspond to a valid login.
        :param email: The email login.
        :param password: The corresponding password.
        :return: True if valid, else False.
        """
        user_info = self.get_user_info_by_email(email)
        hashed_password = user_info[1]
        return self._compare_hash_with_text(hashed_password, password)

    def get_user_info_by_email(self, email):
        """
        Queries the database for user info belonging to the user with the specified email.
        The user info is returned as a single tuple.
        :param email: The email to search by.
        :return: If the mail is present in the database, the corresponding data is returned as a tuple.
        If not, None is returned.
        """
        with self._database as cursor:
            cursor.execute("SELECT * FROM UserInfo WHERE email LIKE '{}'".format(email))
            return cursor.fetchone()

    def _generate_hashed_password(self, password):
        """
        This method hashes the provided clear-text password using bcrypt.
        :param password: The password to be hashed.
        :return: A hashed version of the password, using bcrypt.
        """
        return str(self._bcrypt_agent.generate_password_hash(password).decode('utf-8'))

    def _compare_hash_with_text(self, hashed_password, text_password):
        """
        Compares a hashed password with a clear-text password for verification.
        :param hashed_password: The hashed password
        :param text_password: The clear-text password
        :return: True if the passwords match, else false.
        """
        matching = self._bcrypt_agent.check_password_hash(hashed_password, text_password)
        return matching









