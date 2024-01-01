import discord
import requests
from discord.ext import commands

import settings
from bot_auth import create_token
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

    @bot.hybrid_command()
    async def my_tasks(ctx):
        users_info = {}
        users_info["discord_guild"] = ctx.guild.id
        users_info["discord_id"] = ctx.author.id
        users_info["discord_name"] = ctx.author.name
        users_info["guild_name"] = ctx.guild.name
        roles = ctx.author.roles
        roles_list = []
        for r in roles:
            roles_list.append(r.name)
        users_info["discord_roles"] = roles_list

        headers = {"Authorization": create_token(users_info)}
        url = "https://jobs.cotopia.social/bot/accepted_jobs/me"
        r = requests.get(url=url, headers=headers)
        data = r.json()
        status_code = r.status_code
        await ctx.send(f"status code: {status_code}\n{data}")
    
    @bot.tree.context_menu(name="Pause Task!")
    async def pause_task(interaction: discord.Interaction, message: discord.Message):
        await interaction.response.send_message("this is not a task!")

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    run()
