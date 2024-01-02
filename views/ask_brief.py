import discord


class AskBriefView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.addressee = None  # the user that is asked for brief

    @discord.ui.button(label="Write A Task", style=discord.ButtonStyle.primary)
    async def write(self, interaction: discord.Integration, button: discord.ui.Button):
        if self.addressee == interaction.user:
            await interaction.response.send_message("Ok!", ephemeral=True)
        else:
            await interaction.response.send_message(
                "You are not the addressee!", ephemeral=True
            )

    @discord.ui.button(label="Your Tasks", style=discord.ButtonStyle.primary)
    async def tasks(self, interaction: discord.Integration, button: discord.ui.Button):
        if self.addressee == interaction.user:
            pass
        else:
            await interaction.response.send_message(
                "You are not the addressee!", ephemeral=True
            )

    @discord.ui.button(label="Browse Requests", style=discord.ButtonStyle.primary)
    async def job_requests(
        self, interaction: discord.Integration, button: discord.ui.Button
    ):
        if self.addressee == interaction.user:
            pass
        else:
            await interaction.response.send_message(
                "You are not the addressee!", ephemeral=True
            )
