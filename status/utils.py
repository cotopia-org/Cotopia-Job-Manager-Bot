import sqlite3

import discord

from briefing import briefing


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
            text = text + ":green_circle:   " + i.mention + f"  --->    {b}\n"
        else:
            text = text + ":yellow_circle:  " + i.mention + "\n"

    # for i in not_in_voice:
    #     text = text + ":white_circle:   " + i.mention + "\n"

    category = discord.utils.get(guild.categories, name="JOBS")
    if category is None:
        category = await guild.create_category("JOBS")
    da_channel = discord.utils.get(guild.text_channels, name="status")
    if da_channel is None:
        da_channel = await guild.create_text_channel(category=category, name="status")

    if text == "":
        text = "Nobody's here! 👻"

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


async def update_status_text(guild, idles = None):
    print("yooo we are here!")
    text_row = get_status_text(guild_id=guild.id)
    if text_row is None:
        gen_status_text(guild)
        text_row = get_status_text(guild_id=guild.id)

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

        # skip if she is in idles
        if idles is not None:
            if i in idles:
                continue

        if not briefing.should_record_brief(driver=str(guild.id), doer=str(i)):
            # now read the brief
            b = briefing.get_last_brief(driver=str(guild.id), doer=str(i))
            text = text + ":green_circle:   " + i.mention + f"  --->    {b}\n"
        else:
            text = text + ":yellow_circle:  " + i.mention + "\n"
    
    # Now adding idle ones
    if idles is not None:
        for i in idles:
            text = text + ":yellow_circle:  " + i.mention + "\n"


    # for i in not_in_voice:
    #     text = text + ":white_circle:   " + i.mention + "\n"

    # fetching the message
    try:
        # channel id is text_row[1]
        channel = guild.get_channel(text_row[1])
        # the message id is text_row[2]
        msg = await channel.fetch_message(text_row[2])

        if text == "":
            text = "Nobody's here! 👻"

        await msg.edit(content=text)

    except:  # noqa: E722
        pass


def set_as_idle(guild_id, member_id):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute( """CREATE TABLE IF NOT EXISTS idles(
                                guild_id INT NOT NULL,
                                member_id INT NOT NULL); """)
    cursor.execute(f"""INSERT INTO status_txt VALUES ({guild_id}, {member_id});""")

    conn.commit()
    cursor.close()
    conn.close()

def remove_idle(guild_id, member_id):
    pass

def get_idles(guild):
    pass