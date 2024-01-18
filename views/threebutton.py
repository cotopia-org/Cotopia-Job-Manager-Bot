import asyncio

import discord
import requests
from persiantools.jdatetime import JalaliDate

from bot_auth import create_token
from briefing import briefing
from views.ask_brief import AskBriefView



class ThreeButtonView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.addressee = None  # the user that is asked for brief
        self.job_id = 0
        self.job_title = ""
        self.ask_msg_id = 0
        self.channel = None

    @discord.ui.button(label="Yes!", style=discord.ButtonStyle.primary)
    async def yes(self, interaction: discord.Integration, button: discord.ui.Button):
        if self.addressee == interaction.user:
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

            # canceling ask
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
            await interaction.response.send_message(
                "You are not the addressee!", ephemeral=True
            )

    @discord.ui.button(label="No, it's done!", style=discord.ButtonStyle.secondary)
    async def no_done(
        self, interaction: discord.Integration, button: discord.ui.Button
    ):
        if self.addressee == interaction.user:
            # make token and headers
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
            headers = {"Authorization": create_token(d)}
            # change the status to done
            url = f"https://jobs-api.cotopia.social/bot/accepted_jobs/{self.job_id}"
            pl = {"acceptor_status": "done"}
            r = requests.put(url=url, json=pl, headers=headers)
            data = r.json()
            if r.status_code == 200:
                print(f"status code: {r.status_code}\n{data}")
                await interaction.response.send_message(
                    "Task Status: Done!", ephemeral=True
                )
                # deleting the ask msg
                the_ask_msg = await self.channel.fetch_message(self.ask_msg_id)
                await the_ask_msg.delete()

                # ask again what she's gonna do
                ask_view = AskBriefView()
                ask_view.addressee = interaction.user
                ask_msg = await self.channel.send(
                    "Welcome "
                    + interaction.user.mention
                    + "!\nWhat are you going to do today?",
                    view=ask_view,
                )
                ask_view.ask_msg_id = ask_msg.id
                print(f"the ask msg id is {ask_view.ask_msg_id}")

            else:
                print(f"status code: {r.status_code}\n{data}")
                await interaction.response.send_message(
                    f"status code: {r.status_code}\n{data}", ephemeral=True
                )

        else:
            await interaction.response.send_message(
                "You are not the addressee!", ephemeral=True
            )

    @discord.ui.button(label="No, it's paused!", style=discord.ButtonStyle.secondary)
    async def no_later(
        self, interaction: discord.Integration, button: discord.ui.Button
    ):
        if self.addressee == interaction.user:
            # make token and headers
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
            headers = {"Authorization": create_token(d)}
            # change the status to todo
            url = f"https://jobs-api.cotopia.social/bot/accepted_jobs/{self.job_id}"
            pl = {"acceptor_status": "todo"}
            r = requests.put(url=url, json=pl, headers=headers)
            data = r.json()
            if r.status_code == 200:
                print(f"status code: {r.status_code}\n{data}")
                await interaction.response.send_message(
                    "Task Status: Todo!!", ephemeral=True
                )
                # deleting the ask msg
                the_ask_msg = await self.channel.fetch_message(self.ask_msg_id)
                await the_ask_msg.delete()

                # ask again what she's gonna do
                ask_view = AskBriefView()
                ask_view.addressee = interaction.user
                ask_msg = await self.channel.send(
                    "Welcome "
                    + interaction.user.mention
                    + "!\nWhat are you going to do today?",
                    view=ask_view,
                )
                ask_view.ask_msg_id = ask_msg.id
                print(f"the ask msg id is {ask_view.ask_msg_id}")

            else:
                print(f"status code: {r.status_code}\n{data}")
                await interaction.response.send_message(
                    f"status code: {r.status_code}\n{data}", ephemeral=True
                )

        else:
            await interaction.response.send_message(
                "You are not the addressee!", ephemeral=True
            )
