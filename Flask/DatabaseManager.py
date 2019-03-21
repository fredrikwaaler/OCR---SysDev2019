from Database import CursorFromConnectionPool
from psycopg2 import ProgrammingError
import traceback
from PasswordHandler import PasswordHandler


class DatabaseManager:

    def __init__(self, **kwargs):
        """
        The DatabaseManager is a simple class for managing and storing data to the database.
        The class also provides a simple method for authenticating a login based on data in the connected db.
        :param kwargs: host, database, user, password, port (for external connections)
        Example: host="localhost", database="Sakila", user="postgres", password="mypass123"
        """
        self._database = CursorFromConnectionPool(**kwargs)

    def store_user_info(self, email, password, name=None, fiken_manager=None):
        """
        Creates a record in the database, storing the specified email and a hashed version of the supplied password.
        :param email: The email used to login the user
        :param password: The password to hash and store
        :param name: The users name
        :param fiken_manager: The fiken manager. Should be stored as a pickled byte object.
        """
        # First, hash the password before storing
        hashed_password = PasswordHandler.generate_hashed_password(password)

        '''
        if fiken_manager:
            if type(fiken_manager) is not bytes:
                raise ValueError("The FikenManager must be a pickled byte object.")
        '''

        # Then, store the record in the database
        with self._database as cursor:
            try:
                cursor.execute('INSERT INTO UserInfo VALUES (%s, %s, %s, %s) ', (email, hashed_password, name,
                                                                                     fiken_manager))
            except ProgrammingError:
                traceback.print_exc()

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

    def edit_user_info(self, email, **kwargs):
        """
        Used for editing a relation in the UserInfo table. Since email is pk, we filter by it.
        Provide column_name and new value in kwargs. Ex: fiken_manager=FikenManager().
        :param email: The email of the relation to edit.
        :param kwargs: The columns we want to edit, and the new values.
        """
        if self.get_user_info_by_email(email) is not None:
            set_str = ""
            for arg in kwargs:
                set_str += "{} = '{}', ".format(arg, kwargs[arg])
            set_str = set_str[:len(set_str)-2]  # Remove trailing "," and " "

            update_str = "UPDATE  'user_info' SET {} WHERE email = '{}'".format(set_str, email)

            try:
                with self._database as cursor:
                    cursor.execute(update_str, (set_str, email))
            except ProgrammingError:
                traceback.print_exc()

        else:
            raise ValueError("{} not belonging to any user. Cannot update values.".format(email))

    def delete_user_by_email(self, email):
        """
        Deletes the relation in the userinfo-table that has the provided email, if any.
        :param email: The email of the relation to delete.
        """
        with self._database as cursor:
            cursor.execute("DELETE FROM UserInfo WHERE email = {}".format(email))






# a = DatabaseManager(host="localhost", user="postgres", password="Sebas10an99", database="Sukkertoppen")






