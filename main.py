import asyncio
import time

import discord
import requests
from discord.ext import commands
from persiantools.jdatetime import JalaliDate

import settings
from bot_auth import create_token
from briefing import briefing
from modals.submit import JobSubmitModal

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
    async def on_message(message):
        if message.author == bot.user:
            return
        # RECORDING BRIEF
        try:
            replied_to = await message.channel.fetch_message(
                message.reference.message_id
            )
            if replied_to.author == bot.user:
                if "Reply to this message to submit a brief." in replied_to.content:
                    if message.author in replied_to.mentions:
                        briefing.write_to_db(
                            brief=message.content,
                            doer=str(message.author),
                            driver=str(message.guild.id),
                        )
                        em = discord.Embed(
                            title="#brief",
                            description=message.content,
                            color=discord.Color.blue(),
                        )
                        em.set_author(name=str(JalaliDate.today()))
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
                        except:  # noqa: E722
                            print("Asking for brief was not canceled! Don't panic tho.")

        except:  # noqa: E722
            print("the message is not relevant!")

    @bot.event
    async def on_voice_state_update(member, before, after):
        # Ignoring Bots
        if member.bot:
            return

        guild = member.guild

        # func that asks for brief after a while
        task2 = None

        async def ask_for_brief():
            await asyncio.sleep(8)  # 8 seconds
            try:
                await guild.system_channel.send(
                    "Welcome "
                    + member.mention
                    + "!\nWhat are you going to do today?\nReply to this message to submit a brief."
                )
            except:  # noqa: E722
                await guild.text_channels[0].send(
                    "Welcome "
                    + member.mention
                    + "!\nWhat are you going to do today?\nReply to this message to submit a brief."
                )

        # When user leaves voice channel
        if after.channel is None:
            # cancelling asking for brief
            try:
                (task,) = [
                    task
                    for task in asyncio.all_tasks()
                    if task.get_name() == f"ask for brief {str(member)}@{guild.id}"
                ]
                task.cancel()
            except:  # noqa: E722
                print("Asking for brief was not canceled! Don't panic tho.")

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

    @bot.tree.command()
    async def submit(interaction: discord.Interaction):
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

    @bot.hybrid_command()
    async def my_tasks(ctx):
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
        url = "https://jobs.cotopia.social/bot/accepted_jobs/me"
        r = requests.get(url=url, headers=headers)
        data = r.json()
        status_code = r.status_code
        await ctx.send(f"status code: {status_code}\n{data}")

    @bot.tree.context_menu(name="Pause Task!")
    async def pause_task(interaction: discord.Interaction, message: discord.Message):
        await interaction.response.send_message("this is not a task!")

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    run()
