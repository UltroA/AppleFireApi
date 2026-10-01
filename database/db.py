from psycopg_pool import ConnectionPool
from config import DB_DSN

pool = ConnectionPool(DB_DSN, open=False)
