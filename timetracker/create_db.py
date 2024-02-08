import psycopg2


def create_tables():
    conn = psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="Tp\ZS?gfLr|]'a",
        port=5432,
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
                                guild_id INT NOT NULL,
                                discord_id INT NOT NULL,
                                event_id INT NOT NULL,
                                UNIQUE(guild_id, discord_id)
                                ); """
    )

    print("job_pendings created! @postgres")

    cursor.execute(
            """CREATE TABLE IF NOT EXISTS idles(
                                guild_id INT NOT NULL,
                                member_id INT NOT NULL); """
    )

    print("idles created! @postgres")

    cursor.execute("""   CREATE TABLE IF NOT EXISTS status_txt(
                                guild_id INT NOT NULL,
                                channel_id INT NOT NULL,
                                msg_id INT NOT NULL); """
    )

    print("status_txt created! @postgres")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS job_posts(
                   guild_id INT NOT NULL,
                   channel_id INT NOT NULL,
                   post_id INT NOT NULL,
                   job_id INT NOT NULL
                   );"""
    )

    print("job_posts created! @postgres")

    conn.commit()
    cursor.close()
    conn.close()


create_tables()
