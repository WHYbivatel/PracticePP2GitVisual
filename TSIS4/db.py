import psycopg2
from psycopg2.extras import RealDictCursor

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


SCHEMA_SQL = '''
CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    level_reached INTEGER NOT NULL,
    played_at TIMESTAMP DEFAULT NOW()
);
'''


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
        conn.commit()


def get_or_create_player(username: str) -> int:
    username = username.strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM players WHERE username = %s', (username,))
            row = cur.fetchone()
            if row:
                return row[0]
            cur.execute(
                'INSERT INTO players(username) VALUES(%s) RETURNING id',
                (username,),
            )
            player_id = cur.fetchone()[0]
        conn.commit()
    return player_id


def save_result(username: str, score: int, level_reached: int):
    player_id = get_or_create_player(username)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                '''
                INSERT INTO game_sessions(player_id, score, level_reached)
                VALUES(%s, %s, %s)
                ''',
                (player_id, score, level_reached),
            )
        conn.commit()


def get_personal_best(username: str) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                '''
                SELECT COALESCE(MAX(gs.score), 0)
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                WHERE p.username = %s
                ''',
                (username,),
            )
            return cur.fetchone()[0] or 0


def get_top_scores(limit: int = 10):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                '''
                SELECT
                    p.username,
                    gs.score,
                    gs.level_reached,
                    gs.played_at
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC, gs.level_reached DESC, gs.played_at ASC
                LIMIT %s
                ''',
                (limit,),
            )
            return list(cur.fetchall())
