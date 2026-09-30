import psycopg


def create_table_users(cursor: psycopg.cursor) -> bool:
    try:
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS
                    users (
                    name text PRIMARY KEY NOT NULL,
                    email text UNIQUE NOT NULL,
                    password text NOT NULL
                    );
                """)
        print("SYSTEM: CREATED TABLE USERS")
    except Exception as e:
        print(e)
        return False
    return True


def create_user(cursor: psycopg.cursor, name: str, email: str, password: str) -> bool:
    try:
        cursor.execute(f"""
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s);
        """, (name, email, password))
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

