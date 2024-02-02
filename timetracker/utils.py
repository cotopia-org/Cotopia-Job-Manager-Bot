import psycopg2


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
    if isjob:
        cur.execute(
            """INSERT INTO job_event (guild_id, discord_id, is_job, job_id, title)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            ;""",
            (guild_id, discord_id, isjob, id, title),
        )
    else:
        cur.execute(
            """INSERT INTO job_event (guild_id, discord_id, is_job, brief_id, title)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            ;""",
            (guild_id, discord_id, isjob, id, title),
        )
    
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    # returning row id
    return result[0]


# who is pending what
# guild_id, discord_id, id of main table row

# start
# guild_id, discord_id, isjob, id(job or brief), title

# end
# guild_id, discord_id
# who is pending what
# find row in events, calculate duration for it
# handle errors


# make report
