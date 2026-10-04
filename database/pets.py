import psycopg


def create_table_pets(cursor: psycopg.cursor) -> bool:
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS
            pets (
            petId BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            coupleId BIGINT references couples(coupleId) NOT NULL,
            name VARCHAR(16)  NOT NULL,
            dateStarted DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            isAlive BOOLEAN NOT NULL DEFAULT TRUE,
            currentLevel INTEGER NOT NULL DEFAULT 0
    );""")


def create_pet(cursor: psycopg.cursor, coupleId, name: str) -> int | None:
    cursor.execute("""
            INSERT INTO pets(coupleid, name) 
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            RETURNING petid;
            """, (coupleId, name))
    row = cursor.fetchone()
    return row[0] if row else None


def get_pet(cursor: psycopg.cursor, coupleId: int) -> int | None:
    cursor.execute("""
            SELECT * FROM pets
            WHERE coupleId = %s
            """, coupleId)
    row = cursor.fetchone()
    return row if row else None
