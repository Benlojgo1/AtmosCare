# src/database.py

import psycopg
import os
# Note: In a real application, you would ensure load_dotenv() is called 
# in the main application file (e.g., app.py) before this function is called.

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database using environment variables.

    Returns:
        A psycopg connection object or None if the connection fails.
    """
    # Retrieve connection details from environment variables
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')

    try:
        # Establish the connection
        conn = psycopg.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        # Ensure the connection is set for automatic commits if needed, 
        # though explicit transaction management is generally better.
        # conn.autocommit = True 
        return conn
    
    except psycopg.Error as e:
        # Print a descriptive error message if the connection fails
        print(f"--- DATABASE CONNECTION ERROR ---")
        print(f"Failed to connect to PostgreSQL. Check .env variables and ensure the server is running.")
        print(f"Details: {e}")
        return None