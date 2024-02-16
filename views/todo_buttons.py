import asyncio
from datetime import datetime
from typing import List

import discord
import requests
from discord.components import SelectOption

from bot_auth import create_token
from briefing import briefing
from status import utils as status
from timetracker.utils import start as record_start
from utils.job_posts import get_job_link, get_job_post_author_id
from views.todo_whendoing_btns import TodoWhenDoingButtons


class TodoButtons(discord.ui.View):
    def __init__(self, *, timeout: float | None = 1900800):
        super().__init__(timeout=timeout)
        self.headers = None
        self.job_id = 0
        self.job_title = ""
        self.ask_msg_id = 0

    @discord.ui.button(label="▶️ Start", style=discord.ButtonStyle.green)
    async def startjob(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        url = f"https://jobs-api.cotopia.social/bot/accepted_jobs/{self.job_id}"
        pl = {"acceptor_status": "doing"}
        r = requests.put(url=url, json=pl, headers=self.headers)
        data = r.json()
        if r.status_code == 200:
            print(f"status code: {r.status_code}\n{data}")
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                content="Task Status: Doing!",
                view=None,
            )
            briefing.write_to_db(
                brief=self.job_title + "   id:" + str(self.job_id),
                doer=str(interaction.user),
                driver=str(interaction.guild.id),
            )
            try:
                url = await get_job_link(job_id=self.job_id, guild=interaction.guild)
                if url is None:
                    link = ""
                else:
                    link = f"[view]({url})"
            except:  # noqa: E722
                link = ""
            desc_first_part = "I'm working on\n**"
            author_id = get_job_post_author_id(
                job_id=self.job_id, guild_id=interaction.guild.id
            )
            if author_id is not None and author_id != -1:
                if author_id != interaction.user.id:
                    # this means the task is writen by someone else
                    desc_first_part = f"I'm helping <@{author_id}> on\n**"
            em = discord.Embed(
                title="📣",
                description=desc_first_part + self.job_title + "**\n" + link,
                color=discord.Color.blue(),
            )
            # em.set_author(name=str(JalaliDate.today()))
            channel = interaction.guild.system_channel
            if channel is None:
                channel = interaction.guild.text_channels[0]
            webhook = await channel.create_webhook(name=interaction.user.name)
            if interaction.user.nick is None:
                the_name = interaction.user.name
            else:
                the_name = interaction.user.nick
            await webhook.send(
                embed=em,
                username=the_name,
                avatar_url=interaction.user.avatar,
            )
            webhooks = await channel.webhooks()
            for w in webhooks:
                await w.delete()

            # deleting the ask msg
            try:
                the_ask_msg = await channel.fetch_message(self.ask_msg_id)
                await the_ask_msg.delete()
            except:  # noqa: E722
                pass

            try:
                (task,) = [
                    task
                    for task in asyncio.all_tasks()
                    if task.get_name()
                    == f"ask for brief {str(interaction.user)}@{interaction.guild.id}"
                ]
                task.cancel()
            except:  # noqa: E722
                print("Asking for brief was not canceled! Don't panic tho.")

            # updating job status
            status.remove_idle(
                guild_id=interaction.guild.id, member_id=interaction.user.id
            )
            await status.update_status_text(interaction.guild)

            # user just started a task
            # we should check the voice state
            # if ok
            # record start
            if interaction.user.voice is not None:
                if (
                    interaction.user.voice.channel is not None
                    and interaction.user.voice.self_deaf is False
                ):
                    print("IN A VOICE CHANNEL AND NOT DEAFENED")
                    # no need to check idle
                    try:
                        wu = status.whatsup(
                            guild=interaction.guild, member=interaction.user
                        )
                        record_start(
                            guild_id=interaction.guild.id,
                            discord_id=interaction.user.id,
                            isjob=wu["isjob"],
                            id=wu["id"],
                            title=wu["title"],
                        )
                    except Exception as e:
                        print(e)

        else:
            print(f"status code: {r.status_code}\n{data}")
            await interaction.followup.send(
                content=f"status code: {r.status_code}\n{data}", ephemeral=True
            )

    @discord.ui.button(label="✅ Done", style=discord.ButtonStyle.secondary)
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        url = f"https://jobs-api.cotopia.social/bot/accepted_jobs/{self.job_id}"
        pl = {"acceptor_status": "done"}
        r = requests.put(url=url, json=pl, headers=self.headers)
        data = r.json()
        if r.status_code == 200:
            print(f"status code: {r.status_code}\n{data}")
            # sending request to get todos
            url = "https://jobs-api.cotopia.social/bot/aj/me/by/todo"
            r = requests.get(url=url, headers=self.headers)
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
                        ask_msg_id=0,
                    )
                    await interaction.followup.edit_message(
                        message_id=interaction.message.id,
                        content="Task moved to 'Done'!\nSelect the task that you want to work on:",
                        view=todo_view,
                    )
                # todo list is empty
                else:
                    await interaction.followup.edit_message(
                        message_id=interaction.message.id,
                        content="Task moved to 'Done'!\nYour TO-DO list is empty! 🥳",
                    )
            # request error
            else:
                await interaction.followup.send(
                    f"ERROR {status_code}\n{data}", ephemeral=True
                )
        else:
            print(f"status code: {r.status_code}\n{data}")
            await interaction.followup.send(
                content=f"status code: {r.status_code}\n{data}", ephemeral=True
            )

    @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.secondary)
    async def decline(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        url = f"https://jobs-api.cotopia.social/bot/jobs/decline/{self.job_id}"
        r = requests.delete(url=url, headers=self.headers)
        try:
            data = r.json()
        except:  # noqa: E722
            data = r.text
        if r.status_code == 204:
            # TO_DO
            # edit the job post and remove user in acceptors
            print(f"status code: {r.status_code}\n{data}")
            # sending request to get todos
            url = "https://jobs-api.cotopia.social/bot/aj/me/by/todo"
            r = requests.get(url=url, headers=self.headers)
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
                        ask_msg_id=0,
                    )
                    await interaction.followup.edit_message(
                        message_id=interaction.message.id,
                        content="Task declined!\nSelect the task that you want to work on:",
                        view=todo_view,
                    )
                # todo list is empty
                else:
                    await interaction.followup.edit_message(
                        message_id=interaction.message.id,
                        content="Task declined!\nYour TO-DO list is empty! 🥳",
                    )
            # request error
            else:
                await interaction.followup.send(
                    f"ERROR {status_code}\n{data}", ephemeral=True
                )
        else:
            print(f"status code: {r.status_code}\n{data}")
            await interaction.followup.send(
                content=f"status code: {r.status_code}\n{data}", ephemeral=True
            )


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
