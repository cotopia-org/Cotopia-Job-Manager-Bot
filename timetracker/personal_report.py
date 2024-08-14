import time

import psycopg2

from timetracker.report import personal_report
from os import getenv
from dotenv import load_dotenv


# returns epoch of NOW: int
def rightnow():
    epoch = int(time.time())
    return epoch


async def send_personal_msg(guild, member):
    if should_send(guild_id=guild.id, discord_id=member.id):
        now = rightnow()
        report = await personal_report(
            guild=guild, discord_id=member.id, start_epoch=now - 259200, end_epoch=now
        )
        if report is not False:
            await member.send(report)


def should_send(guild_id: int, discord_id: int):
    load_dotenv()
    conn = psycopg2.connect(
        host=getenv("DB_HOST"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
    )
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS personal_report(
                                guild_id BIGINT NOT NULL,
                                discord_id BIGINT NOT NULL,
                                user_wants BOOLEAN DEFAULT TRUE,
                                last_send BIGINT NOT NULL,
                                UNIQUE(guild_id, discord_id)
                                ); """
    )
    cursor.execute(
        """SELECT * FROM personal_report
        WHERE guild_id = %s
        AND discord_id = %s;""",
        (guild_id, discord_id),
    )
    db_result = cursor.fetchone()
    if db_result is None:
        cursor.execute(
            """INSERT INTO personal_report(guild_id, discord_id, last_send)
            VALUES (%s, %s, %s)""",
            (guild_id, discord_id, rightnow()),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    else:
        if db_result[2]:
            if rightnow() - db_result[3] > 259200:
                # update
                cursor.execute(
                    """UPDATE personal_report
                    SET last_send = %s
                    WHERE guild_id = %s
                    AND discord_id = %s;""",
                    (rightnow(), guild_id, discord_id),
                )
                conn.commit()
                cursor.close()
                conn.close()
                return True
            else:
                conn.commit()
                cursor.close()
                conn.close()
                return False
        else:
            conn.commit()
            cursor.close()
            conn.close()
            return False


async def unsubscribe(member):
    load_dotenv()
    conn = psycopg2.connect(
        host=getenv("DB_HOST"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
    )
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE personal_report
                    SET user_wants = %s
                    WHERE discord_id = %s;""",
        (False, member.id),
    )
    conn.commit()
    cursor.close()
    conn.close()
    await member.send("Alright! I wont send reports to you any more.")
    await member.send("If you changed your mind, just send `!!subscribe`")


async def subscribe(member):
    load_dotenv()
    conn = psycopg2.connect(
        host=getenv("DB_HOST"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
    )
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE personal_report
                    SET user_wants = %s
                    WHERE discord_id = %s;""",
        (True, member.id),
    )
    conn.commit()
    cursor.close()
    conn.close()
    await member.send("Alright! I will send reports to you.")
    await member.send("If you changed your mind, just send `!!unsubscribe`")
