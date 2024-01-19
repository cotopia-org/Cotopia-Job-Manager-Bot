import discord
import requests


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
        else:
            print(f"status code: {r.status_code}\n{data}")
            await interaction.response.send_message(
                f"status code: {r.status_code}\n{data}", ephemeral=True
            )
