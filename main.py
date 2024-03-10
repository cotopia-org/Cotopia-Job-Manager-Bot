import asyncio
import time
from typing import Optional

import discord
import pytz
import requests
from discord.ext import commands
from persiantools.jdatetime import JalaliDate, JalaliDateTime, timedelta

import settings
from bot_auth import create_token
from briefing import briefing
from briefing.brief_modal import BriefModal
from modals.submit import JobSubmitModal
from status import utils as status
from status.utils import whatsup
from timetracker.report import pretty_report
from timetracker.utils import start as record_start
from timetracker.voice_checker import check as event_checker
from views.ask_brief import AskBriefView
from views.doing_buttons import DoingButtons
from views.followup_buttons import FollowupButtonsView
from views.no_doing_buttons import NoDoingButtons
from views.no_todo_buttons import NoTodoButtons
from views.todo_dropdown import TodoView

logger = settings.logging.getLogger("bot")

last_brief_ask = {}


# returns epoch of NOW: int
def rightnow():
    epoch = int(time.time())
    return epoch


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.presences = True
    intents.members = True
    intents.reactions = True

    bot = commands.Bot(command_prefix="/", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")
        await bot.tree.sync()

    @bot.event
    async def on_guild_join(guild):
        try:
            await status.gen_status_text(guild)
            print("Text generated and sent!")
        except:  # noqa: E722
            print("Someting went wrong when status.gen_status_text() was called.")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        # RECORDING BRIEF
        try:
            replied_to = await message.channel.fetch_message(
                message.reference.message_id
            )
            if replied_to.author == bot.user:
                if "!\nWhat are you going to do today?" in replied_to.content:
                    if message.author in replied_to.mentions:
                        briefing.write_to_db(
                            brief=message.content,
                            doer=str(message.author),
                            driver=str(message.guild.id),
                        )
                        em = discord.Embed(
                            title="📣",
                            description="I'm working on\n**" + message.content + "**",
                            color=discord.Color.blue(),
                        )
                        # em.set_author(name=str(JalaliDate.today()))
                        channel = message.guild.system_channel
                        if channel is None:
                            channel = message.guild.text_channels[0]
                        webhook = await channel.create_webhook(name=message.author.name)
                        if message.author.nick is None:
                            the_name = message.author.name
                        else:
                            the_name = message.author.nick
                        await webhook.send(
                            embed=em,
                            username=the_name,
                            avatar_url=message.author.avatar,
                        )
                        webhooks = await channel.webhooks()
                        for w in webhooks:
                            await w.delete()
                        await replied_to.delete()
                        await message.delete()
                        try:
                            (task,) = [
                                task
                                for task in asyncio.all_tasks()
                                if task.get_name()
                                == f"ask for brief {str(message.author)}@{message.guild.id}"
                            ]
                            task.cancel()
                        except Exception as e:
                            print(f"Exception at {rightnow()}")
                            print("main.py line 107")
                            print(e)

                        # updating job status
                        status.remove_idle(
                            guild_id=message.guild.id, member_id=message.author.id
                        )
                        await status.update_status_text(message.guild)

                        # user just added a brief
                        # we should check the voice state
                        # if ok
                        # record start
                        if message.author.voice is not None:
                            if (
                                message.author.voice.channel is not None
                                and message.author.voice.self_deaf is False
                            ):
                                print("IN A VOICE CHANNEL AND NOT DEAFENED")
                                # no need to check idle
                                try:
                                    wu = whatsup(
                                        guild=message.guild, member=message.author
                                    )
                                    record_start(
                                        guild_id=message.guild.id,
                                        discord_id=message.author.id,
                                        isjob=wu["isjob"],
                                        id=wu["id"],
                                        title=wu["title"],
                                    )
                                except Exception as e:
                                    print(f"Exception at {rightnow()}")
                                    print("main.py line 140")
                                    print(e)

        except Exception as e:
            print("the message is not relevant!")
            print(f"Exception at {rightnow()}")
            print("main.py line 146")
            print(e)

    @bot.event
    async def on_voice_state_update(member, before, after):
        # Ignoring Bots
        if member.bot:
            return

        guild = member.guild

        await event_checker(guild=guild, member=member, before=before, after=after)

        # func that asks for brief after a while
        task2 = None

        async def ask_for_brief():
            await asyncio.sleep(8)  # 8 seconds

            # requesting doing tasks
            users_info = {}
            users_info["discord_guild"] = guild.id
            users_info["discord_id"] = member.id
            users_info["discord_name"] = member.name
            users_info["guild_name"] = guild.name
            roles = member.roles
            roles_list = []
            for r in roles:
                roles_list.append(r.name)
            users_info["discord_roles"] = roles_list

            headers = {"Authorization": create_token(users_info)}
            url = "https://jobs-api.cotopia.social/bot/aj/me/by/doing"
            r = requests.get(url=url, headers=headers)
            data = r.json()
            status_code = r.status_code
            # print(f"status code: {status_code}\n{data}")
            if status_code == 200 and len(data) > 0:
                task_index = len(data) - 1  # last one
                task_title = data[task_index]["job"]["title"]
                follow_up_view = FollowupButtonsView()
                follow_up_view.addressee = member
                follow_up_view.job_id = data[task_index]["job"]["id"]
                follow_up_view.job_title = task_title
                try:
                    ask_msg = await guild.system_channel.send(
                        "Welcome "
                        + member.mention
                        + f"!\nDo you want to continue working on **'{task_title}'**?",
                        view=follow_up_view,
                        delete_after=1800,
                    )
                    follow_up_view.channel = guild.system_channel
                except:  # noqa: E722
                    ask_msg = await guild.text_channels[0].send(
                        "Welcome "
                        + member.mention
                        + f"!\nDo you want to continue working on **'{task_title}'**?",
                        view=follow_up_view,
                        delete_after=1800,
                    )
                    follow_up_view.channel = guild.text_channels[0]

                follow_up_view.ask_msg_id = ask_msg.id

            else:
                ask_view = AskBriefView()
                ask_view.addressee = member
                try:
                    ask_msg = await guild.system_channel.send(
                        "Welcome "
                        + member.mention
                        + "!\nWhat are you going to do today?",
                        view=ask_view,
                        delete_after=1800,
                    )
                except:  # noqa: E722
                    ask_msg = await guild.text_channels[0].send(
                        "Welcome "
                        + member.mention
                        + "!\nWhat are you going to do today?",
                        view=ask_view,
                        delete_after=1800,
                    )

                ask_view.ask_msg_id = ask_msg.id
                # print(f"the ask msg id is {ask_view.ask_msg_id}")

        # When user leaves voice channels
        if after.channel is None:
            # cancelling asking for brief
            try:
                (task,) = [
                    task
                    for task in asyncio.all_tasks()
                    if task.get_name() == f"ask for brief {str(member)}@{guild.id}"
                ]
                task.cancel()
            except Exception as e:
                print(f"Exception at {rightnow()}")
                print("main.py line 246")
                print(e)

            # updating job status
            await status.update_status_text(guild)

        # ASKING FOR BRIEF
        global last_brief_ask

        def get_previous_ask(doer: str):
            try:
                return rightnow() - last_brief_ask[doer + "@" + str(guild.id)]
            except:  # noqa: E722
                return 1000000000

        def just_asked(doer: str):
            if get_previous_ask(doer) < 8:  # 8 seconds
                return True
            else:
                return False

        # When user enters voice channels
        if before.channel is None:
            if briefing.should_record_brief(driver=str(guild.id), doer=str(member)):
                if just_asked(str(member)) is False:
                    # Ask 8 seconds later
                    last_brief_ask[str(member) + "@" + str(guild.id)] = (
                        rightnow() + 8
                    )  # 8 seconds
                    task2 = asyncio.create_task(
                        ask_for_brief(), name=f"ask for brief {str(member)}@{guild.id}"
                    )
                    await task2

            # updating job status
            await status.update_status_text(guild)

    @bot.tree.command(
        description="Create a new Job Request, so others can accept it and do it for you!"
    )
    async def post_job_request(interaction: discord.Interaction):
        d = {}
        d["discord_guild"] = interaction.guild_id
        d["discord_id"] = interaction.user.id
        d["discord_name"] = interaction.user.name
        d["guild_name"] = interaction.guild.name
        roles = interaction.user.roles
        roles_list = []
        for r in roles:
            roles_list.append(r.name)
        d["discord_roles"] = roles_list

        job_submit_modal = JobSubmitModal()
        job_submit_modal.users_info = d

        await interaction.response.send_modal(job_submit_modal)

    @bot.tree.command(description="Create a new Job and accept it yourself!")
    async def new_task(interaction: discord.Interaction):
        d = {}
        d["discord_guild"] = interaction.guild_id
        d["discord_id"] = interaction.user.id
        d["discord_name"] = interaction.user.name
        d["guild_name"] = interaction.guild.name
        roles = interaction.user.roles
        roles_list = []
        for r in roles:
            roles_list.append(r.name)
        d["discord_roles"] = roles_list

        job_submit_modal = JobSubmitModal()
        job_submit_modal.users_info = d
        job_submit_modal.self_accept = True

        await interaction.response.send_modal(job_submit_modal)

    # @bot.hybrid_command()
    # async def my_tasks(ctx):
    #     users_info = {}
    #     users_info["discord_guild"] = ctx.guild.id
    #     users_info["discord_id"] = ctx.author.id
    #     users_info["discord_name"] = ctx.author.name
    #     users_info["guild_name"] = ctx.guild.name
    #     roles = ctx.author.roles
    #     roles_list = []
    #     for r in roles:
    #         roles_list.append(r.name)
    #     users_info["discord_roles"] = roles_list

    #     headers = {"Authorization": create_token(users_info)}
    #     url = "https://jobs-api.cotopia.social/bot/accepted_jobs/me"
    #     r = requests.get(url=url, headers=headers)
    #     data = r.json()
    #     status_code = r.status_code
    #     await ctx.send(f"status code: {status_code}\n{data}")

    @bot.hybrid_command()
    async def gen_status_text(ctx):
        try:
            await ctx.send("Trying to generate and send the text!", ephemeral=True)
            await status.gen_status_text(ctx.guild)
        except:  # noqa: E722
            await ctx.send("Someting went wrong!", ephemeral=True)

    @bot.hybrid_command()
    async def doing(ctx):
        users_info = {}
        users_info["discord_guild"] = ctx.guild.id
        users_info["discord_id"] = ctx.author.id
        users_info["discord_name"] = ctx.author.name
        users_info["guild_name"] = ctx.guild.name
        roles = ctx.author.roles
        roles_list = []
        for r in roles:
            roles_list.append(r.name)
        users_info["discord_roles"] = roles_list

        headers = {"Authorization": create_token(users_info)}
        url = "https://jobs-api.cotopia.social/bot/aj/me/by/doing"
        r = requests.get(url=url, headers=headers)
        data = r.json()
        status_code = r.status_code
        if status_code == 200:
            if len(data) <= 0:
                buttons = NoDoingButtons()
                de_msg = await ctx.send(
                    "You have no tasks in DOING!", view=buttons, ephemeral=True
                )
                buttons.ask_msg_id = de_msg.id
            else:
                task_index = len(data) - 1  # last one
                job_id = data[task_index]["job"]["id"]
                url = f"https://jobs-api.cotopia.social/bot/job/{job_id}"
                r = requests.get(url=url, headers=headers)
                data = r.json()
                status_code = r.status_code
                if status_code == 200:
                    jsm = JobSubmitModal()
                    doing_buttons = DoingButtons()
                    doing_buttons.headers = headers
                    doing_buttons.job_id = job_id
                    await ctx.send(
                        f"{jsm.create_job_post_text(guild=ctx.guild, data=data)}",
                        view=doing_buttons,
                        ephemeral=True,
                    )
                else:
                    await ctx.send(f"ERROR {status_code}\n{data}", ephemeral=True)
        else:
            await ctx.send(f"ERROR {status_code}\n{data}", ephemeral=True)

    @bot.hybrid_command()
    async def todos(ctx):
        await ctx.interaction.response.defer(ephemeral=True, thinking=True)
        users_info = {}
        users_info["discord_guild"] = ctx.guild.id
        users_info["discord_id"] = ctx.author.id
        users_info["discord_name"] = ctx.author.name
        users_info["guild_name"] = ctx.guild.name
        roles = ctx.author.roles
        roles_list = []
        for r in roles:
            roles_list.append(r.name)
        users_info["discord_roles"] = roles_list

        headers = {"Authorization": create_token(users_info)}
        # sending the request
        url = "https://jobs-api.cotopia.social/bot/aj/me/by/todo"
        r = requests.get(url=url, headers=headers)
        data = r.json()
        status_code = r.status_code
        # request is ok
        if status_code == 200:
            # todo list is not empty
            if len(data) > 0:
                # making a drop down menu
                rows = []
                for each in data:
                    rows.append(
                        discord.SelectOption(
                            label=each["job"]["title"],
                            value=each["job"]["id"],
                        )
                    )

                todo_view = TodoView(
                    options=rows,
                    placeholder="Select a TO-DO!",
                    ask_msg_id=0,
                )
                await ctx.interaction.followup.send(
                    "Select the task that you want to work on:", view=todo_view
                )
            # todo list is empty
            else:
                buttons = NoTodoButtons()
                da_msg = await ctx.interaction.followup.send(
                    content="Your TO-DO list is empty! 🥳", view=buttons
                )
                buttons.ask_msg_id = da_msg.id
        # request error
        else:
            await ctx.interaction.followup.send(
                f"ERROR {status_code}\n{data}", ephemeral=True
            )

    @bot.tree.command()
    async def quick_task(interaction: discord.Interaction):
        brief_modal = BriefModal()
        brief_modal.user = interaction.user
        brief_modal.driver = interaction.guild_id
        await interaction.response.send_modal(brief_modal)

    @bot.hybrid_command()
    async def report(
        ctx,
        member: discord.Member,
        start_ssss: Optional[int] = 1349,
        start_mm: Optional[int] = 1,
        start_rr: Optional[int] = 1,
        end_ssss: Optional[int] = 1415,
        end_mm: Optional[int] = 12,
        end_rr: Optional[int] = 29,
    ):
        emrooz = JalaliDate.today()
        avale_hafte = emrooz - timedelta(days=emrooz.weekday())
        # akhare_hafte = emrooz + timedelta(days=(6 - emrooz.weekday()))

        if start_ssss == 1349 and start_mm == 1 and start_rr == 1:
            start_dt = JalaliDateTime(
                year=avale_hafte.year,
                month=avale_hafte.month,
                day=avale_hafte.day,
                hour=0,
                minute=0,
                second=0,
            )
            localized_start_dt = pytz.timezone("Asia/Tehran").localize(dt=start_dt)
            start_epoch = int(localized_start_dt.timestamp())
        else:
            try:
                start_dt = JalaliDateTime(year=start_ssss, month=start_mm, day=start_rr)
                localized_start_dt = pytz.timezone("Asia/Tehran").localize(dt=start_dt)
                start_epoch = int(localized_start_dt.timestamp())
            except:  # noqa: E722
                await ctx.send("Please enter a valid date!", ephemeral=True)
                return

        if end_ssss == 1415 and end_mm == 12 and end_rr == 29:
            end_dt = JalaliDateTime(
                    year=emrooz.year,
                    month=emrooz.month,
                    day=emrooz.day,
                    hour=23,
                    minute=59,
                    second=59,
                )
            localized_end_dt = pytz.timezone("Asia/Tehran").localize(dt=end_dt)
            end_epoch = int(localized_end_dt.timestamp()) + 1

        else:
            try:
                end_dt = JalaliDateTime(
                    year=end_ssss,
                    month=end_mm,
                    day=end_rr,
                    hour=23,
                    minute=59,
                    second=59,
                )
                localized_end_dt = pytz.timezone("Asia/Tehran").localize(dt=end_dt)
                end_epoch = int(localized_end_dt.timestamp()) + 1
            except:  # noqa: E722
                await ctx.send("Please enter a valid date!", ephemeral=True)
                return

        if int(start_epoch) >= int(end_epoch):
            await ctx.send(
                "**Start Date** should be before **End Date**! Try Again!",
                ephemeral=True,
            )
            return

        report = await pretty_report(
            guild=ctx.guild,
            discord_id=member.id,
            start_epoch=start_epoch,
            end_epoch=end_epoch,
        )

        await ctx.send(report, ephemeral=True)

    # @bot.hybrid_command()
    # async def token(ctx):
    #     users_info = {}
    #     users_info["discord_guild"] = ctx.guild.id
    #     users_info["discord_id"] = ctx.author.id
    #     users_info["discord_name"] = ctx.author.name
    #     users_info["guild_name"] = ctx.guild.name
    #     roles = ctx.author.roles
    #     roles_list = []
    #     for r in roles:
    #         roles_list.append(r.name)
    #     users_info["discord_roles"] = roles_list

    #     await ctx.send(create_token(users_info), ephemeral=True)

    # @bot.tree.context_menu(name="Pause Task!")
    # async def pause_task(interaction: discord.Interaction, message: discord.Message):
    #     await interaction.response.send_message("this is not a task!")

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    run()
