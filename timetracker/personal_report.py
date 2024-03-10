import time

import psycopg2


# returns epoch of NOW: int
def rightnow():
    epoch = int(time.time())
    return epoch


async def send_personal_msg(guild, member):
    if should_send(guild_id=guild.id, discord_id=member.id):
        await member.send("yoooo")


def should_send(guild_id: int, discord_id: int):
    conn = psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="Tp\ZS?gfLr|]'a",
        port=5432,
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
            if rightnow() - db_result[3] > 86300:  # 24 hours - 100 seconds 
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
