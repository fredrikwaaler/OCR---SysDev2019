from flask_login import UserMixin
from DatabaseManager import DatabaseManager
from FikenManager import FikenManager
from PasswordHandler import PasswordHandler
import pickle
import settings


class User(UserMixin):
    """
    This class represents a user in the application.
    """

    # The database shared by all users for storing/retrieving users
    Dm = DatabaseManager(host=settings.DB_HOST, user=settings.DB_USER, password=settings.DB_PASSWORD, database=settings.DB_DATABASE)

    def __init__(self, email, password, name, admin=False):
        """
        A user has an email, a password and a name.
        A user also has a associated FikenManager.
        This is retrieved automatically if the user already has one. Else, a new one is created.
        :param email: The users email
        :param password: The users password - should be hashed.
        :param name: The users name (first and last).
        :param admin: Specifies whether or not the user is admin.
        """
        self.email = email
        self.password = password
        self.name = name
        self.admin = admin
        self.active = True
        self.fiken_manager = self._get_fiken_manager()

    def get_id(self):
        """
        Returns the email of the user. Needed for LoginManager when logging in and out users.
        :return: The email of the user
        """
        return self.email

    @property
    def is_active(self):
        """
        Returns whether or not the user is active. Used by the LoginManager to handle sessions.
        :return: True if the user is active, else false.
        """
        return self.active

    @property
    def is_admin(self):
        """
        Returns whether or not the user is admin.
        :return: True if the user is admin, else False.
        """
        return self.admin

    def change_password(self, new_pass):
        """
        Changes the password of the user. Hashes upon setting.
        :param new_pass: The new password.
        """
        self.password = PasswordHandler.generate_hashed_password(new_pass)
        self.store_user()

    def change_email(self, new_email):
        """
        Changes the mail of the current user.
        :param new_email: The new email
        """
        # Validate that the supplied user is valid before changing password.
        if self.Dm.get_user_info_by_email(self.email):
            self.Dm.edit_user_info(self.email, email=new_email)
            self.email = new_email

    def store_user(self):
        """
        Stores the user to the database.
        """
        # Make the users fiken_manager ready for storing.
        fm_to_store = pickle.dumps(self.fiken_manager)
        # If the user already exists, edit existing relation.
        if self.Dm.get_user_info_by_email(self.email):
            self.Dm.edit_user_info(self.email, password=self.password, name=self.name, fiken_manager=fm_to_store,
                                   admin=self.admin)
        # If the user does not exits, create a new relation.
        else:
            self.Dm.store_user_info(email=self.email, password=self.password, name=self.name, fiken_manager=fm_to_store,
                                    admin=self.admin)

    def _get_fiken_manager(self):
        """
        Returns the users associated FikenManager if one exists. Else, it returns a new FikenManager.
        :return: The users associated FikenManager if one exists. Else, it returns a new FikenManager.
        """
        user_data = self.Dm.get_user_info_by_email(email=self.email)
        if user_data:  # If there is such a user:
            if user_data[3]:  # If the user has a stored fiken_manager
                return pickle.loads(user_data[3])
        else:
            return FikenManager()

    def delete_user(self):
        self.Dm.delete_user_by_email(self.email)

    def generate_new_password(self):
        """
        Generates a new random password for the user.
        :return: The new random password.
        """
        new_password = PasswordHandler.generate_random_password()
        self.password = PasswordHandler.generate_hashed_password(new_password)
        self.store_user()
        return new_password

    @staticmethod
    def get_user(email):
        """
        Retrieves a the user-object, if any, with the specified email.
        :param email: The email of the user we want to retrieve.
        :return: The user with the specified email, if any. If not, return None.
        """
        # Get the user data from db if exists:
        user_data = User.Dm.get_user_info_by_email(email)
        if user_data:
            return User(user_data[0], user_data[1], user_data[2], user_data[4])
        else:
            return None

    @staticmethod
    def user_exists(email):
        """
        Returns whether or not a user with the given email exists in the database used for users.
        :param email: The email to check for.
        :return: True if such a user exists, else False.
        """
        if User.Dm.get_user_info_by_email(email):
            return True
        else:
            return False



