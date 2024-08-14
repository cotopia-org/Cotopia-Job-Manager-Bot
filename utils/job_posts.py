import psycopg2
from os import getenv
from dotenv import load_dotenv


# author_id id discord_id of the one who submitted the job
def record_id(
    job_id: int, author_id: int, post_id: int, channel_id: int, guild_id: int
):
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
        """CREATE TABLE IF NOT EXISTS job_posts(
                   guild_id BIGINT NOT NULL,
                   channel_id BIGINT NOT NULL,
                   post_id BIGINT NOT NULL,
                   job_id INT NOT NULL,
                   author_id BIGINT NOT NULL
                   );"""
    )
    cursor.execute(
        f"""INSERT INTO job_posts(guild_id, channel_id, post_id, job_id, author_id)
                   VALUES({guild_id}, {channel_id}, {post_id}, {job_id}, {author_id});"""
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("POST ID RECORDED!")


def get_job_id(post_id: int, channel_id: int, guild_id: int):
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


def get_job_post_author_id(job_id: int, guild_id: int):
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
        f"SELECT author_id FROM job_posts WHERE guild_id = {guild_id} AND job_id = {job_id};"
    )
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    if result is None:
        return None
    else:
        return result[0]


async def get_job_post(job_id: int, guild):
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
            return msg
        except:  # noqa: E722
            return None
