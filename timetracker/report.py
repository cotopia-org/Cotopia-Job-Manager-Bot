import psycopg2


def get_user_events(guild_id: int, discord_id: int, start_epoch: int, end_epoch: int):
    conn = psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="Tp\ZS?gfLr|]'a",
        port=5432,
    )
    cursor = conn.cursor()
    cursor.execute(
        """
                   SELECT * FROM job_event
                   WHERE guild_id = %s
                   AND discord_id = %s
                   AND start_epoch >= %s
                   AND start_epoch <= %s
                   AND duration IS NOT NULL
                   ORDER BY id
                   ;""",
        (guild_id, discord_id, start_epoch, end_epoch),
    )
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result


def process_events(user_events: list):
    if len(user_events) == 0:
        return False
    result = {}
    for each in user_events:
        if each[6]:
            key = f"job-{each[7]}"
            if key not in result:
                result[key] = {}
                result[key]["number of events"] = 0
            result[key]["title"] = each[9]
            result[key]["job_id"] = each[7]
            if "duration" in result[key]:
                result[key]["duration"] = result[key]["duration"] + each[5]
            else:
                result[key]["duration"] = each[5]
            result[key]["number of events"] = result[key]["number of events"] + 1

        else:
            key = f"brief-{each[8]}"
            if key not in result:
                result[key] = {}
                result[key]["number of events"] = 0
            result[key]["title"] = each[9]
            if "duration" in result[key]:
                result[key]["duration"] = result[key]["duration"] + each[5]
            else:
                result[key]["duration"] = each[5]
            result[key]["number of events"] = result[key]["number of events"] + 1

    return result


def seconds_to_hours(processed_events: dict):
    result = {}
    for each in processed_events:
        if "duration" in processed_events[each]:
            processed_events[each]["duration"] = round(
                processed_events[each]["duration"] / 3600, 2
            )
        result.update({each: processed_events[each]})
    return result


def gen_user_report(guild_id: int, discord_id: int, start_epoch: int, end_epoch: int):
    user_events = get_user_events(
        guild_id=guild_id,
        discord_id=discord_id,
        start_epoch=start_epoch,
        end_epoch=end_epoch,
    )
    the_dict = process_events(user_events=user_events)
    if the_dict is False:
        return {200: "No Events Found!"}
    else:
        the_dict = seconds_to_hours(the_dict)
        the_dict["time"] = {"From": start_epoch, "To": end_epoch}
        the_dict["user"] = {"guild_id": guild_id, "discord_id": discord_id}
        return the_dict
