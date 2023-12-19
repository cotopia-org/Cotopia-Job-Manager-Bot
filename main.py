import discord
from discord.ext import commands

import settings
from modals.submit import JobSubmitModal

logger = settings.logging.getLogger("bot")


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.presences = True
    intents.members = True
    intents.reactions = True

    bot = commands.Bot(command_prefix="/", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")
        await bot.tree.sync()

    @bot.tree.command()
    async def submit(interaction: discord.Interaction):
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

        job_submit_modal = JobSubmitModal()
        job_submit_modal.users_info = d

        await interaction.response.send_modal(job_submit_modal)

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    run()
