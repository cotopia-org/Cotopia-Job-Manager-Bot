from briefing import briefing
from status.utils import is_idle, whatsup
from timetracker.utils import end as record_end
from timetracker.utils import start as record_start


def check(guild, member, before, after):
    if before.channel is None:
        # USER JOINED VOICE
        print("USER JOINED VOICE")
        if after.self_deaf is False:
            # USER IS NOT ON PAUSE
            print("USER IS NOT ON PAUSE")
            # RECORD START EVENT IF NEEDED
            if not is_idle(guild=guild, member=member):
                # USER IS NOT IDLE
                print("USER IS NOT IDLE")
                # we should check if she has a brief AKA should_record_brief() is False
                # this means she is already up to something
                if not briefing.should_record_brief(
                    driver=str(guild.id), doer=str(member)
                ):
                    # USER HAS A BRIEF
                    print("USER HAS A BRIEF")
                    try:
                        wu = whatsup(guild=guild, member=member)
                        record_start(
                            guild_id=guild.id,
                            discord_id=member.id,
                            isjob=wu["isjob"],
                            id=wu["id"],
                            title=wu["title"],
                        )
                    except Exception as e:
                        print(e)

        # WE ARE DONE HERE, LETS RETURN
        return

    elif after.channel is None:
        # USER LEAVED VOICE
        print("USER LEAVED VOICE")
        if before.self_deaf is False:
            # USER WAS NOT ON PAUSE
            print("USER WAS NOT ON PAUSE")
            # RECORD END EVENT IF NEEDED
            if not is_idle(guild=guild, member=member):
                # USER IS NOT IDLE
                print("USER IS NOT IDLE")
                # user may not have a brief, but we don't need to check it here
                # cuz record_end() checks for a pending and raises an exception if
                # no pending is recorded
                try:
                    record_end(guild_id=guild.id, discord_id=member.id)
                except Exception as e:
                    print(e)

        # WE ARE DONE HERE, LETS RETURN
        return

    if before.self_deaf is False and after.self_deaf is True:
        # USER PAUSED
        print("USER PAUSED")
        # RECORD END EVENT IF NEEDED
        if not is_idle(guild=guild, member=member):
            # USER IS NOT IDLE
            print("USER IS NOT IDLE")
            # user may not have a brief, but we don't need to check it here
            # cuz record_end() checks for a pending and raises an exception if
            # no pending is recorded
            try:
                record_end(guild_id=guild.id, discord_id=member.id)
            except Exception as e:
                print(e)

        # WE ARE DONE HERE, LETS RETURN
        return

    elif before.self_deaf is True and after.self_deaf is False:
        # USER RESUMED
        print("USER RESUMED")
        # RECORD START EVENT IF NEEDED
        if not is_idle(guild=guild, member=member):
            # USER IS NOT IDLE
            print("USER IS NOT IDLE")
            # we should check if she has a brief AKA should_record_brief() is False
            # this means she is already up to something
            if not briefing.should_record_brief(driver=str(guild.id), doer=str(member)):
                # USER HAS A BRIEF
                print("USER HAS A BRIEF")
                try:
                    wu = whatsup(guild=guild, member=member)
                    record_start(
                        guild_id=guild.id,
                        discord_id=member.id,
                        isjob=wu["isjob"],
                        id=wu["id"],
                        title=wu["title"],
                    )
                except Exception as e:
                    print(e)
