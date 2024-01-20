import discord
from persiantools.jdatetime import JalaliDate
from . import briefing
import asyncio


class BriefModal(discord.ui.Modal, title="Submit your brief!"):
    brief = discord.ui.TextInput(
        style = discord.TextStyle.long,
        label = "Your Brief",
        required = True,
        placeholder = "What are you going to do in this session?"
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.system_channel
        embed = discord.Embed(title="#brief",
                               description=self.brief.value, color=discord.Color.blue())
        embed.set_author(name=str(JalaliDate.today()))
        briefing.write_to_db(brief=self.brief.value, doer=str(self.user), driver=str(self.driver))
        webhook = await channel.create_webhook(name=self.user.name)
        if (self.user.nick is None):
            the_name = self.user.name
        else:
            the_name = self.user.nick
        await webhook.send(
            embed=embed, username=the_name, avatar_url=self.user.avatar)
        webhooks = await channel.webhooks()
        for w in webhooks:
                await w.delete()
        try:
            task, = [task for task in asyncio.all_tasks() if task.get_name() == f"ask for brief {str(self.user)}@{self.driver}"]
            task.cancel() 
        except:  # noqa: E722
            print("No briefing tasks were canceled!")
            
        await interaction.response.send_message(f"Your brief was submitted {self.user.mention}!", ephemeral=True)