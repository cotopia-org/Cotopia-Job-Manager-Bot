import discord

class AskBriefView(discord.ui.View):
    @discord.ui.button(label="Write A Task", style=discord.ButtonStyle.primary)
    async def write(self, interaction: discord.Integration, button: discord.ui.Button):
        pass
    @discord.ui.button(label="Your Tasks", style=discord.ButtonStyle.primary)
    async def tasks(self, interaction: discord.Integration, button: discord.ui.Button):
        pass
    @discord.ui.button(label="Browse Requests", style=discord.ButtonStyle.primary)
    async def job_requests(self, interaction: discord.Integration, button: discord.ui.Button):
        pass