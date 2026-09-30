import psycopg

from models import UserReg


def create_table_users(cursor: psycopg.cursor) -> bool:
    try:
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS
                    users (
                    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    name VARCHAR(16) UNIQUE NOT NULL,
                    email VARCHAR(32) UNIQUE NOT NULL,
                    password VARCHAR(128) NOT NULL
                    );
                """)
    except Exception as e:
        print(e)
        return False
    return True


def create_user(cursor: psycopg.cursor, user: UserReg) -> bool:
    try:
        cursor.execute(f"""
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s);
        """, (user.username, user.email, user.password))
        return True
    except Exception as e:
        print(e)
        return False


def seach_by_name(cursor: psycopg.cursor, name: str) -> str | None:
    row = cursor.execute(f"""
            SELECT password FROM users 
            WHERE name = %s;
            """, (name, )).fetchone()
    return row[0] if row else None


def drop_table(cursor: psycopg.cursor, name: str) -> None:
    cursor.execute(f"DROP TABLE IF EXISTS {name}")

