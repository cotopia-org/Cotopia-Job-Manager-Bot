import psycopg2
from os import getenv
from dotenv import load_dotenv


def create_tables():
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

    print("job_event created! @postgres")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS job_pendings(
                                guild_id BIGINT NOT NULL,
                                discord_id BIGINT NOT NULL,
                                event_id INT NOT NULL,
                                UNIQUE(guild_id, discord_id)
                                ); """
    )

    print("job_pendings created! @postgres")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS idles(
                                guild_id BIGINT NOT NULL,
                                member_id BIGINT NOT NULL); """
    )

    print("idles created! @postgres")

    cursor.execute(
        """   CREATE TABLE IF NOT EXISTS status_txt(
                                guild_id BIGINT NOT NULL,
                                channel_id BIGINT NOT NULL,
                                msg_id BIGINT NOT NULL); """
    )

    print("status_txt created! @postgres")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS job_posts(
                   guild_id BIGINT NOT NULL,
                   channel_id BIGINT NOT NULL,
                   post_id BIGINT NOT NULL,
                   job_id INT NOT NULL
                   );"""
    )

    print("job_posts created! @postgres")

    conn.commit()
    cursor.close()
    conn.close()


create_tables()
