import psycopg


def create_table_users(cursor: psycopg.cursor) -> None:
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
    cursor.execute(f"""
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING 
        RETURNING id;
    """, (username, email, password))
    row = cursor.fetchone()
    return row[0] if row else None


def search_by_email(cursor: psycopg.cursor, email: str) -> list | None:
    row = cursor.execute(f"""
            SELECT id, password FROM users 
            WHERE email = %s;
            """, (email, )).fetchone()
    return row if row else None



def drop_table(cursor: psycopg.cursor, name: str) -> None:
    cursor.execute(f"DROP TABLE IF EXISTS {name}")

