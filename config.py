import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
DB_DSN = os.getenv("DATABASE_URL", "dbname=postgres user=postgres")
SECRET_KEY = os.getenv("SECRET_KEY", "just_for_test")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
HOST = os.getenv("HOST", "0.0.0.0")
