from psycopg2 import pool


class Database:
    """
    Class represents a database.
    The class is 'static-only', meaning there can only be one database connection open at once.
    The database takes use of a connection pool to save run time on operations.
    The initialize method is used to open a connection pool from the database,
    and must always be called before taking use of the database.

    """
    __connectionPool = None

    @classmethod
    def initialize(cls, **kwargs):
        """
        Initializes the object for connection to a database by setting up a connection pool for it.
        Must be provided with sufficient data to make a connection.
        NOTE: This method must always be called once before making getting interacting with the database.
        :param kwargs: database, host, user, password
        """
        cls.__connectionPool = pool.SimpleConnectionPool(minconn=1, maxconn=10, **kwargs)

    @classmethod
    def get_connection(cls):
        """
        Returns a connection from the connection pool to the database.
        @:return Returns a connection from the connection pool to the database.
        """
        return cls.__connectionPool.getconn()

    @classmethod
    def return_connection(cls, connection):
        """
        Is used to put back an active connection to the connection pool.
        :param connection: The active connection
        """
        cls.__connectionPool.putconn(connection)

    @classmethod
    def close_all_connections(cls):
        """
        Closes all active connections for the connection pool.
        """
        cls.__connectionPool.closeall()


class CursorFromConnectionPool:
    """
    This class is in close conjunction with the Database class,
    and takes direct use of whatever Database is initialized.
    I.e, if a Database has not yet been initialized using 'Database.initialize' this class will not work.
    Represents a cursor for a connection from the databases connection pool.
    Is used like this: 'with CursorFromConnectionPool as someName:'.
    This will automatically open a cursor on someName.
    The cursor will automatically commit and close when the 'with' statement ends.
    The connection will automatically be put pack in the connection pool.
    """
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """
        When a Cursor is used, we get a connection from the pool and a cursor on that connection,
        the cursor is returned.
        :return: A cursor for the database initialized.
        """
        self.connection = Database.get_connection()
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        When we are done with the cursor, it will close itself,
        make sure that it's connection commits and then puts itself back in the database.
        If some error occurs when using the cursor, it will by default perform a rollback on its connection.
        :return:
        """
        if exc_val is not None:
            self.connection.rollback()
        else:
            self.cursor.close()
            self.connection.commit()
        Database.return_connection(self.connection)
