from flask_login import UserMixin
from DatabaseManager import DatabaseManager
from FikenManager import FikenManager
import pickle


class User(UserMixin):
    """
    This class represents a user in the application.
    """

    # The database shared by all users for storing/retrieving users
    Dm = DatabaseManager(host="localhost", user="postgres", password="Sebas10an99", database="Sukkertoppen")

    def __init__(self, email, password, name):
        """
        A user has an email, a password and a name.
        A user also has a associated FikenManager.
        This is retrieved automatically if the user already has one. Else, a new one is created.
        :param email: The users email
        :param password: The users password (not hashed - hashed automatically upon storing)
        :param name: The users name (first and last).
        """
        self.email = email
        self.password = password
        self.name = name
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

    def store_user(self):
        """
        Stores the user to the database.
        """
        # Make the users fiken_manager ready for storing.
        fm_to_store = pickle.dumps(self.fiken_manager)
        # If the user already exists, edit existing relation.
        if self.Dm.get_user_info_by_email(self.email):
            self.Dm.edit_user_info(self.email, password=self.password, name=self.name, fiken_manager=fm_to_store)
        # If the user does not exits, create a new relation.
        else:
            self.Dm.store_user_info(email=self.email, password=self.password, name=self.name, fiken_manager=fm_to_store)

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
            return User(user_data[0], user_data[1], user_data[2])
        else:
            return None




