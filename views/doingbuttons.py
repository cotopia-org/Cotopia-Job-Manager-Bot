import discord
import requests

from status import utils as status


class DoingButtons(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.headers = None
        self.job_id = 0

    @discord.ui.button(label="✅ Done", style=discord.ButtonStyle.secondary)
    async def done(self, interaction: discord.Integration, button: discord.ui.Button):
        url = f"https://jobs-api.cotopia.social/bot/accepted_jobs/{self.job_id}"
        pl = {"acceptor_status": "done"}
        r = requests.put(url=url, json=pl, headers=self.headers)
        data = r.json()
        if r.status_code == 200:
            print(f"status code: {r.status_code}\n{data}")
            await interaction.response.send_message(
                "Task moved to DONE!", ephemeral=True
            )
            # updating job status
            status.set_as_idle(guild_id=interaction.guild.id, member_id=interaction.user.id)
            await status.update_status_text(guild=interaction.guild)
        else:
            print(f"status code: {r.status_code}\n{data}")
            await interaction.response.send_message(
                f"status code: {r.status_code}\n{data}", ephemeral=True
            )

    @discord.ui.button(label="⏸️ Pause", style=discord.ButtonStyle.secondary)
    async def todo(self, interaction: discord.Integration, button: discord.ui.Button):
        url = f"https://jobs-api.cotopia.social/bot/accepted_jobs/{self.job_id}"
        pl = {"acceptor_status": "todo"}
        r = requests.put(url=url, json=pl, headers=self.headers)
        data = r.json()
        if r.status_code == 200:
            print(f"status code: {r.status_code}\n{data}")
            await interaction.response.send_message(
                "Task moved to TODO!", ephemeral=True
            )
            # updating job status
            status.set_as_idle(guild_id=interaction.guild.id, member_id=interaction.user.id)
            await status.update_status_text(guild=interaction.guild)
        else:
            print(f"status code: {r.status_code}\n{data}")
            await interaction.response.send_message(
                f"status code: {r.status_code}\n{data}", ephemeral=True
            )
