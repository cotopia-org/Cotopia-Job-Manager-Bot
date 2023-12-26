import discord


class SubmittedJobView(discord.ui.View):
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.primary)
    async def accept(self, interaction: discord.Integration, button: discord.ui.Button):
        pass
