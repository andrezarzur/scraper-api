import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

config = {
 'user': 'root',
 'password': '',
 'host': 'localhost',
 'database': 'fastapiscraper'
}


@contextmanager
def get_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(**config)
        yield connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise e
    finally:
        if connection and connection.is_connected():
            connection.close()
