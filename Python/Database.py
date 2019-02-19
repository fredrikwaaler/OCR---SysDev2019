from psycopg2 import pool


class Database:
    """
    Class represents a database.
    The database takes use of a connection pool to save run time on operations.
    """

    def __init__(self, **kwargs):
        """
        The database object has a connection-pool that is used for managing connections to the specified database.
        Note: Must be provided with sufficient data to establish a connection.
        :param database: The name of the database to connect to
        :param host: The host address
        :param user: The user logging in to the dbsm
        :param password: Users password for dbsm
        :param port: Port for external host
        """
        self.connectionPool = pool.SimpleConnectionPool(minconn=1, maxconn=10, **kwargs)

    def get_connection(self):
        """
        Returns a connection from the connection pool to the database.
        @:return Returns a connection from the connection pool to the database.
        """
        return self.connectionPool.getconn()

    def return_connection(self, connection):
        """
        Is used to put back an active connection to the connection pool.
        :param connection: The active connection
        """
        self.connectionPool.putconn(connection)

    def close_all_connections(self):
        """
        Closes all active connections for the connection pool.
        """
        self.connectionPool.closeall()


class CursorFromConnectionPool:

    def __init__(self, **kwargs):
        self.database = Database(**kwargs)
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """
        When a Cursor is used, we get a connection from the pool and a cursor on that connection,
        the cursor is returned.
        :return: A cursor for the database.
        """
        self.connection = self.database.get_connection()
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        When we are done with the cursor, it will close itself,
        make sure that it's connection commits and then puts itself back in the database.
        If some error occurs when using the cursor, it will by default perform a rollback on its connection.
        """
        if exc_val is not None:
            self.connection.rollback()
        else:
            self.cursor.close()
            self.connection.commit()
        self.database.return_connection(self.connection)

