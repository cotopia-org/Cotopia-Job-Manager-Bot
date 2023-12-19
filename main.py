import json

import discord
import requests
from discord.ext import commands

import settings
from bot_auth import create_token

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

    @bot.hybrid_command()
    async def submit(ctx):
        d = {}
        d["discord_guild"] = ctx.guild.id
        d["discord_id"] = ctx.author.id
        d["discord_name"] = ctx.author.name
        d["guild_name"] = ctx.guild.name
        roles = ctx.author.roles
        roles_list = []
        for r in roles:
            roles_list.append(r.name)
        d["discord_roles"] = roles_list

        token = create_token(d)
        headers = {"Authorization": token}
        payload_dic = {"title": "Job Tilte", "workspace": d["guild_name"]}
        payload = json.dumps(payload_dic)
        url = "https://jobs.cotopia.social/bot/job"
        r = requests.post(url=url, data=payload, headers=headers)
        data = r.json()

        await ctx.send(data)

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    run()
