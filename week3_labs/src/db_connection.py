import mysql.connector
from mysql.connector import Error

def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root123",
            database="fletapp"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

if __name__ == "__main__":
    conn = connect_db()
    if conn:
        conn.close()