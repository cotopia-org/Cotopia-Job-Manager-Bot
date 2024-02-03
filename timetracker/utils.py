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
            start_epoch BIGINT NOT NULL,
            end_epoch BIGINT NULL,
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
            """INSERT INTO job_event (guild_id, discord_id, start_epoch, is_job, job_id, title)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            ;""",
            (guild_id, discord_id, start, isjob, id, title),
        )
    else:
        cur.execute(
            """INSERT INTO job_event (guild_id, discord_id, start_epoch, is_job, brief_id, title)
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
    if result is None:
        raise Exception("No Pending!")
    cursor.execute(
        f"""DELETE FROM job_pendings
                   WHERE guild_id = {guild_id}
                   AND discord_id = {discord_id};"""
    )
    conn.commit()
    cursor.close()
    conn.close()
    return result[2]


# guild_id, discord_id, isjob, id(job or brief), title
def start(guild_id: int, discord_id: int, isjob: bool, id: int, title: str):
    try: # check for pending
        event_id = find_pending(guild_id=guild_id, discord_id=discord_id)
        # if no Exception, continue to "end" that pending. then call start again!
        print("WOW, an unexpected pending found!")
        end_epoch = rightnow()
        conn = psycopg2.connect(
            host="localhost",
            dbname="postgres",
            user="postgres",
            password="Tp\ZS?gfLr|]'a",
            port=5432,
        )
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM job_event WHERE id = {event_id}")
        db_event = cur.fetchone()
        if db_event is None:
            raise Exception("Could not find the event!")
        
        start_epoch = db_event[3]
        duration = end_epoch - start_epoch
        cur.execute(
            "UPDATE job_event SET end_epoch = %s, duration = %s WHERE id = %s;",
            (end_epoch, duration, event_id),
        )
        conn.commit()
        cur.close()
        conn.close()
        print("Don't worry. I ended the pending event successfully.")

        print("Now I try to call the start() again.")
        start(guild_id, discord_id, isjob, id, title)

    except Exception as e:
        print(e)
        title_255 = title[:255]
        event_id = record_event(
            guild_id=guild_id, discord_id=discord_id, isjob=isjob, id=id, title=title_255
        )
        record_pending(guild_id=guild_id, discord_id=discord_id, event_id=event_id)


def end(guild_id: int, discord_id: int):
    end_epoch = rightnow()
    try:
        event_id = find_pending(guild_id=guild_id, discord_id=discord_id)
        conn = psycopg2.connect(
            host="localhost",
            dbname="postgres",
            user="postgres",
            password="Tp\ZS?gfLr|]'a",
            port=5432,
        )
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM job_event WHERE id = {event_id}")
        db_event = cur.fetchone()
        if db_event is None:
            raise Exception("Could not find the event!")
        
        start_epoch = db_event[3]
        duration = end_epoch - start_epoch
        cur.execute(
            "UPDATE job_event SET end_epoch = %s, duration = %s WHERE id = %s;",
            (end_epoch, duration, event_id),
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return e


# make report
