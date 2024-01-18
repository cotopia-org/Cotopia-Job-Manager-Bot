import discord
import requests

from bot_auth import create_token
from utils.job_id_coder import PREFIX, decode

LINE = "-----------------------------------------------------\n"


class SubmittedJobView(discord.ui.View):
    @discord.ui.button(label="🤝 Accept", style=discord.ButtonStyle.secondary)
    async def accept(self, interaction: discord.Integration, button: discord.ui.Button):
        users_info = {}
        users_info["discord_guild"] = interaction.guild_id
        users_info["discord_id"] = interaction.user.id
        users_info["discord_name"] = interaction.user.name
        users_info["guild_name"] = interaction.guild.name
        roles = interaction.user.roles
        roles_list = []
        for r in roles:
            roles_list.append(r.name)
        users_info["discord_roles"] = roles_list

        headers = {"Authorization": create_token(users_info)}

        text = interaction.message.content
        s = text.split("id: " + PREFIX, 1)
        job_id = decode(PREFIX + s[1])

        url = f"https://jobs-api.cotopia.social/bot/accept/{job_id}"

        r = requests.post(url=url, headers=headers)
        data = r.json()
        status_code = r.status_code

        if status_code == 201:
            new_text = (
                s[0]
                + "Accepted by:\n"
                + interaction.user.mention
                + "\n"
                + LINE
                + "id: "
                + PREFIX
                + s[1]
            )
            await interaction.response.edit_message(content=new_text)
        else:
            await interaction.response.send_message(
                f"status code: {status_code}\n{data}", ephemeral=True
            )
