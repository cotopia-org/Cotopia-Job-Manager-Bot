import discord
import requests

from bot_auth import create_token
from utils.event_recorder import write_event_to_db
from utils.job_posts import get_job_id


class SubmittedJobView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 1900800):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="🤝 Accept", style=discord.ButtonStyle.secondary)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
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

        job_id = get_job_id(
            post_id=interaction.message.id,
            channel_id=interaction.channel.id,
            guild_id=interaction.guild.id,
        )

        url = f"https://jobs-api.cotopia.social/bot/accept/{job_id}"

        r = requests.post(url=url, headers=headers)
        data = r.json()
        status_code = r.status_code

        if status_code == 201:
            write_event_to_db(
                driver=str(interaction.guild.id),
                kind="JOB ACCEPTED",
                doer=str(interaction.user.id),
                isPair=False,
            )
            old_text = interaction.message.content
            s = old_text.split("**Accepted By:**")
            new_text = s[0]
            if s[1] == " -":
                new_text = new_text + "**Accepted By:**\n" + str(interaction.user)
            else:
                new_text = (
                    new_text + "**Accepted By:**" + s[1] + ", " + str(interaction.user)
                )
            await interaction.followup.edit_message(
                message_id=interaction.message.id, content=new_text
            )
        else:
            await interaction.followup.send(
                content=f"status code: {status_code}\n{data}", ephemeral=True
            )
