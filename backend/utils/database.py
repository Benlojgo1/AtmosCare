import psycopg
import os

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
        return conn
    
    except psycopg.Error as e:
        # Print a descriptive error message if the connection fails
        print(f"--- DATABASE CONNECTION ERROR ---")
        print(f"Failed to connect to PostgreSQL. Check .env variables and ensure the server is running.")
        print(f"Details: {e}")
        return None

    # Code block below was made to test if connection was successful (it was)
# if __name__ == '__main__':
#     from dotenv import load_dotenv

#     # 1. Load environment variables (CRITICAL for testing)
#     load_dotenv() 
    
#     print("Attempting to connect to the database...")
    
#     conn = get_db_connection()
    
#     if conn:
#         print("SUCCESS: Database connection established!")
        
#         try:
#             # Optional: Execute a simple query to confirm database responsiveness
#             cursor = conn.cursor()
#             cursor.execute('SELECT 1 + 1;')
#             result = cursor.fetchone()
#             print(f"   Test Query Result: {result}")
#             cursor.close()
#         except Exception as e:
#             print(f" WARNING: Failed to execute simple query: {e}")
#         finally:
#             conn.close()
#             print("   Connection closed gracefully.")
#     else:
#         print("FAILURE: Could not connect to the database. Check logs above.")