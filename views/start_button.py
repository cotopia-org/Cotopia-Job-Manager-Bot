import asyncio

import discord
import requests

from briefing import briefing
from status import utils as status
from timetracker.utils import start as record_start
from utils.event_recorder import write_event_to_db
from utils.job_posts import get_job_link


class StartView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 1900800):
        super().__init__(timeout=timeout)
        self.headers = None
        self.job_id = 0
        self.job_title = ""
        self.ask_msg_id = 0

    @discord.ui.button(label="▶️ Start", style=discord.ButtonStyle.green)
    async def startjob(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        url = f"https://jobs-api.cotopia.social/bot/accepted_jobs/{self.job_id}"
        pl = {"acceptor_status": "doing"}
        r = requests.put(url=url, json=pl, headers=self.headers)
        data = r.json()
        if r.status_code == 200:
            print(f"status code: {r.status_code}\n{data}")
            write_event_to_db(
                driver=str(interaction.guild.id),
                kind="TASK STARTED",
                doer=str(interaction.user.id),
                isPair=False,
            )
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                content="Task Status: Doing!",
                view=None,
            )
            briefing.write_to_db(
                brief=self.job_title + "   id:" + str(self.job_id),
                doer=str(interaction.user),
                driver=str(interaction.guild.id),
            )
            try:
                url = await get_job_link(job_id=self.job_id, guild=interaction.guild)
                if url is None:
                    link = ""
                else:
                    link = f"[view]({url})"
            except:  # noqa: E722
                link = ""
            em = discord.Embed(
                title="📣",
                description="I'm working on\n**" + self.job_title + "**\n" + link,
                color=discord.Color.blue(),
            )
            # em.set_author(name=str(JalaliDate.today()))
            channel = interaction.guild.system_channel
            if channel is None:
                channel = interaction.guild.text_channels[0]
            webhook = await channel.create_webhook(name=interaction.user.name)
            if interaction.user.nick is None:
                the_name = interaction.user.name
            else:
                the_name = interaction.user.nick
            await webhook.send(
                embed=em,
                username=the_name,
                avatar_url=interaction.user.avatar,
            )
            webhooks = await channel.webhooks()
            for w in webhooks:
                await w.delete()

            # deleting the ask msg
            try:
                the_ask_msg = await channel.fetch_message(self.ask_msg_id)
                await the_ask_msg.delete()
            except:  # noqa: E722
                pass

            try:
                (task,) = [
                    task
                    for task in asyncio.all_tasks()
                    if task.get_name()
                    == f"ask for brief {str(interaction.user)}@{interaction.guild.id}"
                ]
                task.cancel()
            except:  # noqa: E722
                print("Asking for brief was not canceled! Don't panic tho.")

            # updating job status
            status.remove_idle(
                guild_id=interaction.guild.id, member_id=interaction.user.id
            )
            await status.update_status_text(interaction.guild)

            # user just started a task
            # we should check the voice state
            # if ok
            # record start
            if interaction.user.voice is not None:
                if (
                    interaction.user.voice.channel is not None
                    and interaction.user.voice.self_deaf is False
                ):
                    print("IN A VOICE CHANNEL AND NOT DEAFENED")
                    # no need to check idle
                    try:
                        wu = status.whatsup(
                            guild=interaction.guild, member=interaction.user
                        )
                        record_start(
                            guild_id=interaction.guild.id,
                            discord_id=interaction.user.id,
                            isjob=wu["isjob"],
                            id=wu["id"],
                            title=wu["title"],
                        )
                    except Exception as e:
                        print(e)

        else:
            print(f"status code: {r.status_code}\n{data}")
            await interaction.followup.send(
                content=f"status code: {r.status_code}\n{data}", ephemeral=True
            )
