import psycopg


def create_table_users(cursor: psycopg.cursor) -> None:
    """
    Creates table users if not exists
    :param cursor: just psycopg cursor object
    :return: None
    """
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS
                users (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                name VARCHAR(16) NOT NULL,
                email VARCHAR(32) UNIQUE NOT NULL,
                password VARCHAR(128) NOT NULL
                );
            """)


def create_user(cursor: psycopg.cursor, username: str, email: str, password: str) -> int | None:
    """
    Creates user if not exists
    :param cursor: just psycopg cursor object
    :param username: new username to display
    :param email: user's email
    :param password: user's password
    :return: id
    """
    cursor.execute(f"""
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING 
        RETURNING id;
    """, (username, email, password))
    row = cursor.fetchone()
    return row[0] if row else None


def search_by_email(cursor: psycopg.cursor, email: str) -> list | None:
    """
    Search users by email
    :param cursor: just psycopg cursor object
    :param email: user's email
    :return: [userID, password]
    """
    row = cursor.execute(f"""
            SELECT id, password FROM users 
            WHERE email = %s;
            """, (email, )).fetchone()
    return row if row else None

