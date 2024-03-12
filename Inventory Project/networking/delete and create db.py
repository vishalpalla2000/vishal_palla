import mysql.connector

# MySQL database configuration
# db_config = {
#     'host': '148.100.147.113',       # Host where the MySQL server is running
#     'user': 'sneha',   # Your MySQL username
#     'password': 'dara', # Your MySQL password
# }
db_config = {
    'host': 'localhost',       # Host where the MySQL server is running
    'user': 'sriram',   # Your MySQL username
    'password': 'sriram', # Your MySQL password
}

# Database name to delete and create
database_name = 'ups'

try:
    # Connect to MySQL Server
    conn = mysql.connector.connect(**db_config)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Delete the database if it exists
    cursor.execute(f"DROP DATABASE IF EXISTS {database_name}")

    # Create a new database
    cursor.execute(f"CREATE DATABASE {database_name}")

    print(f"Database '{database_name}' deleted and recreated successfully!")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    # Close the cursor and connection
    if cursor:
        cursor.close()
    if conn:
        conn.close()
