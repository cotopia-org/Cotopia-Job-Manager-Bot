import sqlite3


def record_id(job_id: int, post_id: int, channel_id: int, guild_id: int):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS job_posts(
                   guild_id INT NOT NULL,
                   channel_id INT NOT NULL,
                   post_id INT NOT NULL,
                   job_id INT NOT NULL
                   );"""
    )
    cursor.execute(
        f"""INSERT INTO job_posts(guild_id, channel_id, post_id, job_id)
                   VALUES({guild_id}, {channel_id}, {post_id}, {job_id});"""
    )

    conn.commit()
    cursor.close()
    conn.close()


def get_job_id(post_id: int, channel_id: int, guild_id: int):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT job_id FROM job_posts 
        WHERE guild_id = {guild_id}
        AND channel_id = {channel_id}
        AND post_id = {post_id};"""
    )
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    if result is None:
        return None
    else:
        return result[0]


async def get_job_link(job_id: int, guild):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT * FROM job_posts WHERE guild_id = {guild.id} AND job_id = {job_id};"
    )
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    if result is None:
        return None
    else:
        try:
            channel = guild.get_channel(result[1])
            msg = await channel.fetch_message(result[2])
            return msg.jump_url
        except:  # noqa: E722
            return None
