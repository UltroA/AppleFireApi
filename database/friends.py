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


def check_couples_exist(cursor: psycopg.cursor, mother_id: int, father_id: int) -> bool:
    """
    Checks if couples exist
    :param cursor: just psycopg cursor object
    :param mother_id: id of first user
    :param father_id: id of second user
    :return: 0 if not exist, 1 otherwise
    """
    count = cursor.execute(
        """
        SELECT COUNT(*) FROM couples
        WHERE fatherId = %s AND motherId = %s
        OR motherId = %s AND fatherId = %s;
        """, (mother_id, father_id, mother_id, father_id)
    ).fetchone()[0]

    return count > 0


def get_all_couples(cursor: psycopg.cursor, userId: int) -> list[tuple]:
    row = cursor.execute("""
            SELECT ALL coupleid FROM couples
            WHERE motherId = %s OR fatherId = %s;
            """, (userId, userId))

    couples = [row[0] for row in cursor.fetchall()]
    return couples


def check_friend(cursor: psycopg.cursor, user_id: int, coupleId) -> bool:
    row = cursor.execute("""
            SELECT motherId, fatherId FROM couples 
            WHERE coupleId = %s;   
            """, coupleId).fetchall()
    if user_id in row:
        return True
    return False


def get_couple_id(cursor: psycopg.cursor, mother_id: int, father_id: int) -> int | None:
    coupleid = cursor.execute(
        """
        SELECT coupleId FROM couples
        WHERE motherId = %s AND fatherId = %s
        OR fatherid = %s AND motherId = %s;
        """, (mother_id, father_id, mother_id, father_id)).fetchone()[0]

    return coupleid if coupleid else None
