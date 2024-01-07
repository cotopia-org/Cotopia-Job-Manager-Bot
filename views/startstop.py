import asyncio

import discord
import requests
from persiantools.jdatetime import JalaliDate

from briefing import briefing


class StartView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.headers = None
        self.job_id = 0
        self.job_title = ""
        self.ask_msg_id = 0

    @discord.ui.button(label="▶️ Start", style=discord.ButtonStyle.green)
    async def startjob(
        self, interaction: discord.Integration, button: discord.ui.Button
    ):
        url = f"https://jobs.cotopia.social/bot/accepted_jobs/{self.job_id}"
        pl = {"acceptor_status": "doing"}
        r = requests.put(url=url, json=pl, headers=self.headers)
        data = r.json()
        if r.status_code == 200:
            print(f"status code: {r.status_code}\n{data}")
            await interaction.response.send_message(
                "Task Status: Doing!", ephemeral=True
            )
            briefing.write_to_db(
                brief=self.job_title + "   id:" + str(self.job_id),
                doer=str(interaction.user),
                driver=str(interaction.guild.id),
            )
            em = discord.Embed(
                title="#brief",
                description=self.job_title,
                color=discord.Color.blue(),
            )
            em.set_author(name=str(JalaliDate.today()))
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
            the_ask_msg = await channel.fetch_message(self.ask_msg_id)
            await the_ask_msg.delete()

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
        else:
            print(f"status code: {r.status_code}\n{data}")
            await interaction.response.send_message(
                f"status code: {r.status_code}\n{data}", ephemeral=True
            )
