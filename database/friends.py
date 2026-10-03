import psycopg


def create_table_couples(cursor: psycopg.cursor) -> None:
    """
    Creates table couples if not exists
    :param cursor: just psycopg cursor object
    :return:
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS 
    couples (
        coupleId BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        motherId BIGINT references users(id) NOT NULL,
        fatherId BIGINT references users(id) NOT NULL
    );
    """)


def create_couple(cursor: psycopg.cursor, mother_id: int, father_id: int) -> int | None:
    """
    Creates couple
    :param cursor: just psycopg cursor object
    :param mother_id: id of first user
    :param father_id: id of second user
    :return: coupleId
    """
    cursor.execute(
        """
        INSERT INTO couples (motherId, fatherId)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING 
        RETURNING coupleid;
        """, (mother_id, father_id)
    )
    row = cursor.fetchone()
    return row[0] if row else None


def get_all_couples(cursor: psycopg.cursor, userId: int) -> list[tuple]:
    row = cursor.execute("""
            SELECT ALL coupleid FROM couples
            WHERE motherId = %s OR fatherId = %s;
            """, (userId, userId))

    couples = [row[0] for row in cursor.fetchall()]
    return couples
