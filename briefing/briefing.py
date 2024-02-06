# from discord import VoiceState, Member
import datetime
import time

import psycopg2


# ✅
def should_record_brief(doer: str, driver: str):
    last = get_last_brief_ts(doer, driver)
    if last == -1:
        return True
    now = today()
    # print(f"last recorded brief for {doer}@{driver} was from {last}")
    if last == now:
        return False
    else:
        return True


# ✅
def get_last_brief(doer: str, driver: str):
    conn = psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="Tp\ZS?gfLr|]'a",
        port=5432,
    )
    cur = conn.cursor()
    cur.execute(
        """
                   SELECT content FROM brief
                   WHERE doer = %s AND driver = %s
                   ORDER BY ts DESC;
                   """,
        (doer, driver),
    )

    result = cur.fetchone()

    if result is None:
        # print("no brief found!")
        conn.commit()
        cur.close()
        conn.close()
        return "N/A"
    else:
        conn.commit()
        cur.close()
        conn.close()
        return result[0]


def get_last_brief_and_id(doer: str, driver: str):
    conn = psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="Tp\ZS?gfLr|]'a",
        port=5432,
    )
    cur = conn.cursor()
    cur.execute(
        """
                   SELECT id, content FROM brief
                   WHERE doer = %s AND driver = %s
                   ORDER BY ts DESC;
                   """,
        (doer, driver),
    )

    result = cur.fetchone()

    if result is None:
        # print("no brief found!")
        conn.commit()
        cur.close()
        conn.close()
        return "N/A"
    else:
        conn.commit()
        cur.close()
        conn.close()
        return result


# ✅
def get_last_brief_epoch(doer: str, driver: str):
    conn = psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="Tp\ZS?gfLr|]'a",
        port=5432,
    )
    cur = conn.cursor()
    cur.execute(
        """
                   SELECT epoch FROM brief
                   WHERE doer = %s AND driver = %s
                   ORDER BY epoch DESC;
                   """,
        (doer, driver),
    )

    result = cur.fetchone()

    if result is None:
        # print("no brief found!")
        conn.commit()
        cur.close()
        conn.close()
        return -1
    else:
        conn.commit()
        cur.close()
        conn.close()
        return result[0]


# returns epoch of NOW: int
def rightnow():
    epoch = int(time.time())
    return epoch


# ✅
def write_to_db(brief: str, doer: str, driver: str):
    conn = psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="Tp\ZS?gfLr|]'a",
        port=5432,
    )
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO brief (driver, epoch, doer, content) VALUES (%s, %s, %s, %s);",
        (driver, rightnow(), doer, brief),
    )
    # print("trying to write a brief to db!")
    conn.commit()
    cur.close()
    conn.close()


# ✅
def create_table():
    conn = psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="Tp\ZS?gfLr|]'a",
        port=5432,
    )
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS brief(
            id SERIAL NOT NULL PRIMARY KEY,
            driver VARCHAR(255) null,
            ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            epoch INTEGER null,
            doer VARCHAR(255) null,
            content TEXT null);"""
    )
    conn.commit()
    cur.close()
    conn.close()


def today():
    the_string = datetime.datetime.today().strftime("%Y-%m-%d")
    return the_string


def get_last_brief_ts(doer: str, driver: str):
    conn = psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="Tp\ZS?gfLr|]'a",
        port=5432,
    )
    cur = conn.cursor()
    cur.execute(
        """
                   SELECT ts FROM brief
                   WHERE doer = %s AND driver = %s
                   ORDER BY epoch DESC;
                   """,
        (doer, driver),
    )

    result = cur.fetchone()

    if result is None:
        # print("no brief found!")
        conn.commit()
        cur.close()
        conn.close()
        return -1
    else:
        conn.commit()
        cur.close()
        conn.close()
        return result[0].strftime("%Y-%m-%d")
