import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='Ambadnya@108'
    )
    if connection.is_connected():
        print("Successfully connected to MySQL!")
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")
        print("\nExisting databases:")
        for db in cursor.fetchall():
            print(db[0])
except Error as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("\nMySQL connection closed.")
