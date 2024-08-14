import json
import time

import psycopg2
from os import getenv
from dotenv import load_dotenv


# returns epoch of NOW: int
def rightnow():
    epoch = int(time.time())
    return epoch


# INSERTS INTO discord_event (epoch, kind, doer, isPair, note)
# retuns the id of the added row
# 🚗
def write_event_to_db(
    driver: str, kind: str, doer: str, isPair: bool, note: str = None
):
    if note is None:
        default_note_dic = {"note": "sent by job bot"}
        note = json.dumps(default_note_dic)

    load_dotenv()
    conn = psycopg2.connect(
        host=getenv("DB_HOST"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
    )
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO discord_event
        (driver, epoch, kind, doer, isPair, note)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (driver, rightnow(), kind, doer, isPair, note),
    )
    id_of_added_row = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    print(f"EVENT ADDED id:{id_of_added_row}")
    return id_of_added_row
