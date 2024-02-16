from datetime import datetime
from typing import List

import discord
import requests
from discord.components import SelectOption

from bot_auth import create_token
from views.todo_buttons import TodoButtons
from views.todo_whendoing_btns import TodoWhenDoingButtons


class TodoDropDown(discord.ui.Select):
    def __init__(
        self,
        *,
        # custom_id: str = ...,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        options: List[SelectOption] = ...,
        disabled: bool = False,
        row: int | None = None,
    ) -> None:
        super().__init__(
            # custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            options=options,
            disabled=disabled,
            row=row,
        )
        self.ask_msg_id = 0

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        job_id = self.values[0]
        # creating token
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

        headers = {"Authorization": create_token(d)}
        # sending the request
        url = f"https://jobs-api.cotopia.social/bot/job/{job_id}"
        r = requests.get(url=url, headers=headers)
        data = r.json()
        status_code = r.status_code
        if status_code == 200:
            content = self.create_job_post_text(guild=interaction.guild, data=data)
            # We should check if the user has a task in doing or not
            has_doing = False
            doing_job_id = 0
            url = "https://jobs-api.cotopia.social/bot/aj/me/by/doing"
            r = requests.get(url=url, headers=headers)
            doing_data = r.json()
            status_code = r.status_code
            if status_code == 200:
                if len(doing_data) > 0:
                    # so doing is not empty
                    has_doing = True
                    doing_job_id = doing_data[len(doing_data) - 1]["job"]["id"]
            else:
                print("problem getting doings of the user!")
                print(f"ERROR {status_code}\n{data}")

            if has_doing:
                todobuttonsview = TodoWhenDoingButtons()
                todobuttonsview.doing_job_id = doing_job_id
            else:
                todobuttonsview = TodoButtons()

            todobuttonsview.headers = headers
            todobuttonsview.job_id = data["id"]
            todobuttonsview.job_title = data["title"]
            todobuttonsview.ask_msg_id = self.ask_msg_id
            await interaction.followup.edit_message(
                message_id=interaction.message.id, content=content, view=todobuttonsview
            )

        else:
            await interaction.followup.send(
                content=f"ERROR {status_code}\n{data}", ephemeral=True
            )

    def create_job_post_text(self, guild, data):
        # LINE = "\n-----------------------------------------------------\n"

        title = "## " + data["title"]
        body = ""

        if data["description"]:
            body = "\n" + data["description"] + "\n"
        else:
            # body = "\n**Description:** " + "-" + "\n"
            pass
        ws = data["workspace"].replace(str(guild.id) + "/", "")
        if len(ws) > 0:
            body = body + "📁 **Workspace:** " + ws + "\n"
        else:
            # body = body + "**Workspace:** " + "-" + "\n"
            pass
        if data["deadline"]:
            deadline = datetime.strptime(data["deadline"], "%Y-%m-%dT%H:%M:%S")
            body = (
                body + "⌛ **Deadline:** " + deadline.strftime("%Y-%m-%d  %H:%M") + "\n"
            )
        else:
            # body = body + "**Deadline:** " + "-" + "\n"
            pass
        tags = ""
        if data["tags"]:
            for t in data["tags"]:
                tags = tags + "**[" + t + "]** "
        body = body + tags

        content = title + body

        return content


class TodoView(discord.ui.View):
    def __init__(
        self,
        *,
        options: List[SelectOption],
        placeholder: str,
        ask_msg_id: int,
        timeout: float | None = 1900800,
    ):
        super().__init__(timeout=timeout)
        todo_dropdown = TodoDropDown(options=options, placeholder=placeholder)
        todo_dropdown.ask_msg_id = ask_msg_id
        self.add_item(todo_dropdown)
