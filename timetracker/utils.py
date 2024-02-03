import sqlite3
import time

import psycopg2


# returns epoch of NOW: int
def rightnow():
    epoch = int(time.time())
    return epoch


def record_event(guild_id: int, discord_id: int, isjob: bool, id: int, title: str):
    conn = psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="Tp\ZS?gfLr|]'a",
        port=5432,
    )
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS job_event(
            id SERIAL NOT NULL PRIMARY KEY,
            guild_id BIGINT NOT NULL,
            discord_id BIGINT NOT NULL,
            start BIGINT NOT NULL,
            end BIGINT NULL,
            duration INT NULL,
            is_job BOOLEAN DEFAULT TRUE,
            job_id INT NULL,
            brief_id INT NULL,
            title VARCHAR(255) NULL)
            ;"""
    )

    start = rightnow()

    if isjob:
        cur.execute(
            """INSERT INTO job_event (guild_id, discord_id, start, is_job, job_id, title)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            ;""",
            (guild_id, discord_id, start, isjob, id, title),
        )
    else:
        cur.execute(
            """INSERT INTO job_event (guild_id, discord_id, start, is_job, brief_id, title)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            ;""",
            (guild_id, discord_id, start, isjob, id, title),
        )

    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    # returning row id
    return result[0]


def record_pending(guild_id: int, discord_id: int, event_id: int):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS job_pendings(
                                guild_id INT NOT NULL,
                                discord_id INT NOT NULL,
                                event_id INT NOT NULL,
                                UNIQUE(guild_id, discord_id)
                                ); """
    )
    cursor.execute(
        f"""INSERT INTO job_pendings
                   VALUES ({guild_id}, {discord_id}, {event_id});"""
    )
    conn.commit()
    cursor.close()
    conn.close()


def find_pending(guild_id: int, discord_id: int):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT * FROM job_pendings
                   WHERE guild_id = {guild_id}
                   AND discord_id = {discord_id};"""
    )
    result = cursor.fetchone()
    cursor.execute(
        f"""DELETE FROM job_pendings
                   WHERE guild_id = {guild_id}
                   AND discord_id = {discord_id};"""
    )
    conn.commit()
    cursor.close()
    conn.close()
    return result[2]


# start
# guild_id, discord_id, isjob, id(job or brief), title

# end
# guild_id, discord_id
# who is pending what
# find row in events, calculate duration for it
# handle errors


# make report
