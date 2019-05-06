from Database import CursorFromConnectionPool
from psycopg2 import ProgrammingError
import traceback


class DatabaseManager:

    def __init__(self, **kwargs):
        """
        The DatabaseManager is a simple class for managing and storing data to the database.
        The class also provides a simple method for authenticating a login based on data in the connected db.
        :param kwargs: host, database, user, password, port (for external connections)
        Example: host="localhost", database="Sakila", user="postgres", password="mypass123"
        """
        self._database = CursorFromConnectionPool(**kwargs)

    def store_user_info(self, email, password, name, fiken_manager, admin):
        """
        Creates a record in the database.
        :param email: The email used to login the user
        :param password: The password to hash and store
        :param name: The users name
        :param fiken_manager: The fiken manager. Should be stored as a pickled byte object.
        :param admin: '0' / false implies not admin, this is default. '1' / true is admin.
        """

        # Then, store the record in the database
        with self._database as cursor:
            try:
                cursor.execute('INSERT INTO UserInfo VALUES (%s, %s, %s, %s, %s) ', (email, password, name,
                                                                                     fiken_manager, admin))
            except ProgrammingError:
                traceback.print_exc()

    def get_user_info_by_email(self, email):
        """
        Queries the database for user info belonging to the user with the specified email.'
        The user info is returned as a single tuple.
        :param email: The email to search by.
        :return: If the mail is present in the database, the corresponding data is returned as a tuple.
        If not, None is returned.
        """
        with self._database as cursor:
            cursor.execute("SELECT * FROM userinfo WHERE email LIKE '{}'".format(email))
            return cursor.fetchone()

    def edit_user_info(self, pk_email, **kwargs):
        """
        Used for editing a relation in the UserInfo table. Since email is pk, we filter by it.
        Provide column_name and new value in kwargs. Ex: fiken_manager=FikenManager().
        :param pk_email: The email of the relation to edit.
        :param kwargs: The columns we want to edit, and the new values.
        """
        if self.get_user_info_by_email(pk_email) is not None:
            update_str = ""  # The string that will specify what to update
            values = []  # The values for the query
            for arg in kwargs:  # For each of the values we want to update, add to upd_str and add value to values
                update_str += "{} = %s, ".format(arg)
                values.append(kwargs[arg])
            update_str = update_str[:len(update_str)-2]  # Remove trailing " " and ,
            values.append(pk_email)  # Add email to values to specify what relation is being updated
            values = tuple(values)  # Create a tuple of the values

            update_str = "UPDATE userinfo SET {} WHERE email = %s".format(update_str)

            try:
                with self._database as cursor:
                    cursor.execute(update_str, values)
            except ProgrammingError:
                traceback.print_exc()

        else:
            raise ValueError("{} not belonging to any user. Cannot update values.".format(pk_email))

    def delete_user_by_email(self, email):
        """
        Deletes the relation in the userinfo-table that has the provided email, if any.
        :param email: The email of the relation to delete.
        """
        with self._database as cursor:
            cursor.execute('DELETE FROM userinfo WHERE email = %s', (email,))












