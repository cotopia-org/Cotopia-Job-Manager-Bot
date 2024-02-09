import asyncio
import time

import discord
from persiantools.jdatetime import JalaliDate

from status import utils as status
from timetracker.utils import start as record_start

from . import briefing


class BriefModal(discord.ui.Modal, title="Submit your brief!"):
    brief = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="Your Brief",
        required=True,
        placeholder="What are you going to do in this session?",
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        channel = interaction.guild.system_channel
        embed = discord.Embed(
            title="#brief", description=self.brief.value, color=discord.Color.blue()
        )
        embed.set_author(name=str(JalaliDate.today()))
        briefing.write_to_db(
            brief=self.brief.value, doer=str(self.user), driver=str(self.driver)
        )
        webhook = await channel.create_webhook(name=self.user.name)
        if self.user.nick is None:
            the_name = self.user.name
        else:
            the_name = self.user.nick
        await webhook.send(embed=embed, username=the_name, avatar_url=self.user.avatar)
        webhooks = await channel.webhooks()
        for w in webhooks:
            await w.delete()
        try:
            (task,) = [
                task
                for task in asyncio.all_tasks()
                if task.get_name() == f"ask for brief {str(self.user)}@{self.driver}"
            ]
            task.cancel()
        except Exception as e:
            print("No briefing tasks were canceled!")
            print(e)

        # updating job status
        status.remove_idle(guild_id=interaction.guild.id, member_id=interaction.user.id)
        await status.update_status_text(interaction.guild)

        # user just added a brief
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
                    print(f"Exception at {int(time.time())}")
                    print("brief_modal.py line 80")
                    print(e)

        await interaction.followup.send(
            f"Your brief was submitted {self.user.mention}!", ephemeral=True
        )
