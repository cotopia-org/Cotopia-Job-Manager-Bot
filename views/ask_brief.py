from datetime import datetime
from typing import List

import discord
import requests
from discord.components import SelectOption

from bot_auth import create_token
from modals.submit import JobSubmitModal
from utils.job_id_coder import gen_code


class AskBriefView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 3600):
        super().__init__(timeout=timeout)
        self.addressee = None  # the user that is asked for brief
        self.ask_msg_id = 0

    @discord.ui.button(label="➕ Create NEW Task", style=discord.ButtonStyle.primary)
    async def write(self, interaction: discord.Integration, button: discord.ui.Button):
        if self.addressee == interaction.user:
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
            job_submit_modal.self_accept = True
            job_submit_modal.ask_msg_id = self.ask_msg_id

            await interaction.response.send_modal(job_submit_modal)
        else:
            await interaction.response.send_message(
                "You are not the addressee!", ephemeral=True
            )

    @discord.ui.button(label="🗂️ Your TO-DOs", style=discord.ButtonStyle.secondary)
    async def tasks(self, interaction: discord.Integration, button: discord.ui.Button):
        # check if the adressee is the one who clicked the button
        if self.addressee == interaction.user:
            # showing that the bot is thinking...
            await interaction.response.defer(ephemeral=True, thinking=True)
            # getting users todos
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
            url = "https://jobs.cotopia.social/bot/aj/me/by/todo"
            r = requests.get(url=url, headers=headers)
            data = r.json()
            status_code = r.status_code
            # request is ok
            if status_code == 200:
                # todo list is not empty
                if len(data) > 0:
                    # making a drop down menu
                    rows = []
                    for each in data:
                        rows.append(
                            discord.SelectOption(
                                label=each["job"]["title"],
                                value=each["job"]["id"],
                            )
                        )

                    todo_view = TodoView(options=rows, placeholder="Select a TO-DO!")
                    await interaction.followup.send(
                        "Select the task that you want to work on:", view=todo_view
                    )
                # todo list is empty
                else:
                    await interaction.followup.send("Your TO-DO list is empty! 🥳")
            # request error
            else:
                await interaction.followup.send(
                    f"ERROR {status_code}\n{data}", ephemeral=True
                )

        # someone else clicked the button
        else:
            await interaction.response.send_message(
                "You are not the addressee!", ephemeral=True
            )

    # @discord.ui.button(label="Browse Requests", style=discord.ButtonStyle.primary)
    # async def job_requests(
    #     self, interaction: discord.Integration, button: discord.ui.Button
    # ):
    #     if self.addressee == interaction.user:
    #         pass
    #     else:
    #         await interaction.response.send_message(
    #             "You are not the addressee!", ephemeral=True
    #         )


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

    async def callback(self, interaction: discord.Integration):
        job_id = self.values[0]
        await interaction.response.send_message(
            f"you have choosen {job_id}", ephemeral=True
        )

    def create_job_post_text(self, guild, data):
        LINE = "\n-----------------------------------------------------\n"

        title = "## " + data["title"]

        if data["description"]:
            body = "**Description:**\n" + data["description"] + "\n"
        else:
            body = "**Description:** " + "-" + "\n"
        ws = data["workspace"].replace(guild.name + "/", "")
        if len(ws) > 0:
            body = body + "**Workspace:** " + ws + "\n"
        else:
            body = body + "**Workspace:** " + "-" + "\n"
        if data["deadline"]:
            deadline = datetime.strptime(data["deadline"], "%Y-%m-%dT%H:%M:%S")
            body = body + "**Deadline:** " + deadline.strftime("%Y-%m-%d  %H:%M") + "\n"
        else:
            body = body + "**Deadline:** " + "-" + "\n"
        tags = ""
        if data["tags"]:
            for t in data["tags"]:
                tags = tags + "**[" + t + "]** "
        body = body + tags

        # if "acceptors" in data:
        #     acceptors = "**Accepted By:**\n" + data["acceptors"][0].mention
        # else:
        #     acceptors = "**Accepted By:** " + "-" + "\n"

        id_line = "id: " + gen_code(data["id"])

        content = title + LINE + body + LINE + id_line

        return content


class TodoView(discord.ui.View):
    def __init__(
        self,
        *,
        options: List[SelectOption],
        placeholder: str,
        timeout: float | None = 3600,
    ):
        super().__init__(timeout=timeout)
        self.add_item(TodoDropDown(options=options, placeholder=placeholder))
