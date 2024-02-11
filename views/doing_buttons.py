import discord
import requests

from status import utils as status
from timetracker.utils import end as record_end
from utils.event_recorder import write_event_to_db


class DoingButtons(discord.ui.View):
    def __init__(self, *, timeout: float | None = 1900800):
        super().__init__(timeout=timeout)
        self.headers = None
        self.job_id = 0

    @discord.ui.button(label="✅ Done", style=discord.ButtonStyle.secondary)
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = f"https://jobs-api.cotopia.social/bot/accepted_jobs/{self.job_id}"
        pl = {"acceptor_status": "done"}
        r = requests.put(url=url, json=pl, headers=self.headers)
        data = r.json()
        if r.status_code == 200:
            print(f"status code: {r.status_code}\n{data}")
            write_event_to_db(
                driver=str(interaction.guild.id),
                kind="TASK DONE",
                doer=str(interaction.user.id),
                isPair=False,
            )
            await interaction.response.edit_message(
                content="Task moved to DONE!", view=None, delete_after=60
            )
            # updating job status
            status.set_as_idle(
                guild_id=interaction.guild.id, member_id=interaction.user.id
            )
            await status.update_status_text(guild=interaction.guild)

            # user becomes idle
            # sending end to timetracker
            try:
                record_end(
                    guild_id=interaction.guild.id, discord_id=interaction.user.id
                )
            except Exception as e:
                print(e)
        
        else:
            print(f"status code: {r.status_code}\n{data}")
            await interaction.response.send_message(
                f"status code: {r.status_code}\n{data}", ephemeral=True
            )

    @discord.ui.button(label="⏸️ Pause", style=discord.ButtonStyle.secondary)
    async def todo(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = f"https://jobs-api.cotopia.social/bot/accepted_jobs/{self.job_id}"
        pl = {"acceptor_status": "todo"}
        r = requests.put(url=url, json=pl, headers=self.headers)
        data = r.json()
        if r.status_code == 200:
            print(f"status code: {r.status_code}\n{data}")
            write_event_to_db(
                driver=str(interaction.guild.id),
                kind="TASK PAUSED",
                doer=str(interaction.user.id),
                isPair=False,
            )
            await interaction.response.edit_message(
                content="Task moved to TODO!", view=None, delete_after=60
            )
            # updating job status
            status.set_as_idle(
                guild_id=interaction.guild.id, member_id=interaction.user.id
            )
            await status.update_status_text(guild=interaction.guild)

            # user becomes idle
            # sending end to timetracker
            try:
                record_end(
                    guild_id=interaction.guild.id, discord_id=interaction.user.id
                )
            except Exception as e:
                print(e)
        
        else:
            print(f"status code: {r.status_code}\n{data}")
            await interaction.response.send_message(
                f"status code: {r.status_code}\n{data}", ephemeral=True
            )
