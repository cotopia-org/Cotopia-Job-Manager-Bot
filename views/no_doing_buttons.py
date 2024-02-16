import discord
import requests

from bot_auth import create_token
from modals.submit import JobSubmitModal
from views.no_todo_buttons import NoTodoButtons
from views.todo_dropdown import TodoView


class NoDoingButtons(discord.ui.View):
    def __init__(self, *, timeout: float | None = 1900800):
        super().__init__(timeout=timeout)
        self.ask_msg_id = 0

    @discord.ui.button(label="➕ Create NEW Task", style=discord.ButtonStyle.primary)
    async def write(self, interaction: discord.Interaction, button: discord.ui.Button):
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

    @discord.ui.button(label="🗂️ Your TO-DOs", style=discord.ButtonStyle.secondary)
    async def tasks(self, interaction: discord.Interaction, button: discord.ui.Button):
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
        url = "https://jobs-api.cotopia.social/bot/aj/me/by/todo"
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

                todo_view = TodoView(
                    options=rows,
                    placeholder="Select a TO-DO!",
                    ask_msg_id=self.ask_msg_id,
                )
                await interaction.followup.send(
                    "Select the task that you want to work on:", view=todo_view
                )
            # todo list is empty
            else:
                buttons = NoTodoButtons()
                da_msg = await interaction.followup.send(
                    content="Your TO-DO list is empty! 🥳", view=buttons
                )
                buttons.ask_msg_id = da_msg.id

        # request error
        else:
            await interaction.followup.send(
                f"ERROR {status_code}\n{data}", ephemeral=True
            )
