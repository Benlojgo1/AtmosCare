import databases
import os
from dotenv import load_dotenv

# 1. Load environment variables immediately
load_dotenv()

# 2. Get database components from .env
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'atmoscare')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

# 3. Construct the connection string
if DB_USER and DB_PASSWORD:
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # Fallback for local testing if .env is missing
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/atmoscare"

# 4. Create the database object
database = databases.Database(DATABASE_URL)