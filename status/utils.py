import sqlite3

import discord

from briefing import briefing
from utils import job_posts


async def gen_status_text(guild):
    members = guild.members
    in_voice = []
    not_in_voice = []
    text = ""

    for i in members:
        if i.bot is False:
            if i.voice is None:
                not_in_voice.append(i)
            else:
                in_voice.append(i)

    for i in in_voice:
        # check if it should record a brief
        # if true, then the person is idle
        # if false, then read the brief
        if not briefing.should_record_brief(driver=str(guild.id), doer=str(i)):
            # now read the brief
            b = briefing.get_last_brief(driver=str(guild.id), doer=str(i))

            # remove "   id:" and set job_id
            b = b.split("   id:")
            try:
                job_id = int(b[1])
                url = await job_posts.get_job_link(job_id=job_id, guild=guild)
                if url is None:
                    link = ""
                else:
                    link = f"   [view]({url})"
            except:  # noqa: E722
                link = ""
            b = b[0]

            b = b.replace("\n", " ")  # replace new lines with " "
            if len(b) > 54:
                b = b[:51]  # only show first 51 charachters
                b = b + "..."
            text = (
                text
                + ":green_circle:   "
                + i.mention
                + f"  --->    {b}"
                + link
                + "\n\n"
            )
        else:
            text = text + ":yellow_circle:  " + i.mention + "\n\n"

    # for i in not_in_voice:
    #     text = text + ":white_circle:   " + i.mention + "\n\n"

    category = discord.utils.get(guild.categories, name="JOBS")
    if category is None:
        category = await guild.create_category("JOBS")
    da_channel = discord.utils.get(guild.text_channels, name="📊-status")
    if da_channel is None:
        da_channel = await guild.create_text_channel(category=category, name="📊-status")

    if text == "":
        text = "Nobody's here! 👻"
    else:
        text = "‌\n" + text + "‌"

    da_msg = await da_channel.send(text)

    try:
        # Connect to DB and create a cursor
        sqliteConnection = sqlite3.connect("jobs.db")
        cursor = sqliteConnection.cursor()
        print("DB Init")

        # Creating table
        table_query = """   CREATE TABLE IF NOT EXISTS status_txt(
                                guild_id INT NOT NULL,
                                channel_id INT NOT NULL,
                                msg_id INT NOT NULL); """

        cursor.execute(table_query)

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS idles(
                                guild_id INT NOT NULL,
                                member_id INT NOT NULL); """
        )

        # Deleting the row just in case
        cursor.execute(f"DELETE FROM status_txt WHERE guild_id = {guild.id};")
        sqliteConnection.commit()
        # Inserting data
        msg_query = f"""     INSERT INTO status_txt VALUES
                                ({guild.id}, {da_channel.id}, {da_msg.id});"""

        cursor.execute(msg_query)
        sqliteConnection.commit()

        # Close the cursor
        cursor.close()

    # Handle errors
    except sqlite3.Error as error:
        print("Error occurred - ", error)

    # Close DB Connection irrespective of success
    # or failure
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("SQLite Connection closed")


def get_status_text(guild_id: int):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM status_txt WHERE guild_id = {guild_id};")

    result = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    return result


async def update_status_text(guild):
    text_row = get_status_text(guild_id=guild.id)
    if text_row is None:
        gen_status_text(guild)
        text_row = get_status_text(guild_id=guild.id)

    members = guild.members
    idles = get_idles(guild=guild)
    in_voice = []
    not_in_voice = []
    text = ""

    for i in members:
        if i.bot is False:
            if i.voice is None:
                not_in_voice.append(i)
            else:
                in_voice.append(i)

    for i in in_voice:
        # check if it should record a brief
        # if true, then the person is idle
        # if false, then read the brief

        # skip if she is in idles
        if idles is not None:
            if i in idles:
                continue

        if not briefing.should_record_brief(driver=str(guild.id), doer=str(i)):
            # now read the brief
            b = briefing.get_last_brief(driver=str(guild.id), doer=str(i))

            # remove "   id:" and set job_id
            b = b.split("   id:")
            try:
                job_id = int(b[1])
                url = await job_posts.get_job_link(job_id=job_id, guild=guild)
                if url is None:
                    link = ""
                else:
                    link = f"   [view]({url})"
            except:  # noqa: E722
                link = ""
            b = b[0]

            b = b.replace("\n", " ")  # replace new lines with " "
            if len(b) > 54:
                b = b[:51]  # only show first 51 charachters
                b = b + "..."
            text = (
                text
                + ":green_circle:   "
                + i.mention
                + f"  --->    {b}"
                + link
                + "\n\n"
            )
        else:
            if i not in idles:
                text = text + ":yellow_circle:  " + i.mention + "\n\n"

    # Now adding idle ones
    if idles is not None:
        for i in idles:
            if i not in not_in_voice:
                text = text + ":yellow_circle:  " + i.mention + "\n\n"

    # for i in not_in_voice:
    #     text = text + ":white_circle:   " + i.mention + "\n\n"

    # fetching the message
    try:
        # channel id is text_row[1]
        channel = guild.get_channel(text_row[1])
        # the message id is text_row[2]
        msg = await channel.fetch_message(text_row[2])

        if text == "":
            text = "Nobody's here! 👻"
        else:
            text = "‌\n" + text + "‌"

        await msg.edit(content=text)

    except:  # noqa: E722
        pass


def set_as_idle(guild_id, member_id):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS idles(
                                guild_id INT NOT NULL,
                                member_id INT NOT NULL,
                                UNIQUE(guild_id, member_id)
                                ); """
    )
    cursor.execute(f"""INSERT INTO idles VALUES ({guild_id}, {member_id});""")

    conn.commit()
    cursor.close()
    conn.close()


def remove_idle(guild_id, member_id):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute(
        f"DELETE FROM idles WHERE guild_id = {guild_id} AND member_id = {member_id};"
    )

    conn.commit()
    cursor.close()
    conn.close()


def get_idles(guild):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT member_id FROM idles WHERE guild_id = {guild.id}")
    result = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    if result is None:
        return None
    else:
        members = []
        for each in result:
            m = guild.get_member(each[0])
            members.append(m)
        return members


def is_idle(guild, member):
    idles_list = get_idles(guild)
    if member in idles_list:
        return True
    else:
        return False


def whatsup(guild, member):
    # b_and_id = briefing.get_last_brief_and_id(driver=str(guild.id), doer=str(member))
    b_and_id = briefing.get_last_brief_and_id(driver=guild, doer=member)
    last_brief = b_and_id[1]
    b_id = b_and_id[0]
    if b_and_id == "N/A":
        raise Exception("user has no brief!")
    result = {}

    last_brief = last_brief.split("   id:")
    if len(last_brief) == 2:
        # this means that last_brief has an id at the end
        # which means it was created by a job
        result["isjob"] = True
        result["id"] = int(last_brief[1])
        result["title"] = last_brief[0]
    else:
        result["isjob"] = False
        result["id"] = b_id
        result["title"] = last_brief[0]

    return result
