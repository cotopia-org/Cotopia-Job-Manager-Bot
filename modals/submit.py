import json
from datetime import datetime

import discord
import requests

from bot_auth import create_token
from utils.job_posts import record_id
from utils.at_to_discord_mention import replace as at_to_mention
from views.start_button import StartView
from views.start_whendoing_btns import StartWhenDoingView
from views.submitted_job import SubmittedJobView
import dotenv_loader


class JobSubmitModal(discord.ui.Modal, title="Submit Job"):
    users_info = None
    self_accept = False
    ask_msg_id = 0

    job_title = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Title",
        placeholder="Title of the job",
        required=True,
    )
    description = discord.ui.TextInput(
        style=discord.TextStyle.paragraph,
        label="Description",
        placeholder="Please describe the job as clearly as possible.",
        max_length=512,
        required=True,
    )
    workspace = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Workspace",
        placeholder="What category/workspace it belongs to?",
        required=False,
    )
    tags = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Tags",
        placeholder="tag1, tag2, tag3, ...",
        required=False,
    )
    # weights = discord.ui.TextInput(
    #     style=discord.TextStyle.short,
    #     label="Weights",
    #     placeholder="key1: value1, key2: value2, ...",
    #     required=False,
    # )
    deadline = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Deadline",
        placeholder="yyyy-mm-dd HH:MM",
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        # creating the channel
        category = discord.utils.get(interaction.guild.categories, name="JOBS")
        if category is None:
            category = await interaction.guild.create_category("JOBS")
        da_channel = discord.utils.get(
            interaction.guild.text_channels, name="jobs-general"
        )
        if da_channel is None:
            da_channel = await interaction.guild.create_text_channel(
                category=category, name="jobs-general"
            )

        post_data = {}
        payload_dic = {}
        payload_dic["title"] = at_to_mention(
            text=self.job_title.value, guild=interaction.guild
        )
        payload_dic["workspace"] = (
            str(interaction.guild.id) + "/" + self.workspace.value
        )
        if self.description.value != "":
            payload_dic["description"] = at_to_mention(
                text=self.description.value, guild=interaction.guild
            )
        if self.tags.value != "":
            mentions_replaced = at_to_mention(
                text=self.tags.value, guild=interaction.guild
            )
            split = mentions_replaced.split(", ")
            payload_dic["tags"] = split
        if self.deadline.value != "":
            payload_dic["deadline"] = self.deadline.value

        headers = {"Authorization": create_token(self.users_info)}
        payload = json.dumps(payload_dic)
        url = dotenv_loader.API_BASE + "/bot/job"
        r = requests.post(url=url, data=payload, headers=headers)
        data = r.json()

        if r.status_code == 201:
            print(f"status code: {r.status_code}\n{data}")
            post_data = data

            # self accept
            if self.self_accept:
                job_id = data["id"]
                url = dotenv_loader.API_BASE + f"/bot/accept/{job_id}"
                self_accept_req = requests.post(url=url, headers=headers)
                self_accept_data = self_accept_req.json()
                if self_accept_req.status_code == 201:
                    print(
                        f"status code: {self_accept_req.status_code}\n{self_accept_data}"
                    )
                    post_data["acceptors"] = [interaction.user]

                else:
                    print(
                        f"status code: {self_accept_req.status_code}\n{self_accept_data}"
                    )

        else:
            await interaction.followup.send(
                f"ERROR {r.status_code}\n{data}", ephemeral=True
            )
            print(f"ERROR {r.status_code}\n{data}")

        if post_data != {}:
            post_msg = await self.post_the_job_to_channel(
                guild=interaction.guild,
                channel=da_channel,
                user=interaction.user,
                data=post_data,
            )
            if self.self_accept:
                # We should check if the user has a task in doing or not
                has_doing = False
                doing_job_id = 0
                url = dotenv_loader.API_BASE + "/bot/aj/me/by/doing"
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
                    startview = StartWhenDoingView()
                    startview.doing_job_id = doing_job_id
                else:
                    startview = StartView()
                startview.headers = headers
                startview.job_id = data["id"]
                startview.job_title = data["title"]
                startview.ask_msg_id = self.ask_msg_id
                await interaction.followup.send(
                    content=post_msg.content,
                    view=startview,
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    content="Job Request Posted!\n\n" + post_msg.jump_url,
                    ephemeral=True,
                )

    async def post_the_job_to_channel(self, guild, channel, user, data):
        content = self.create_job_post_text(guild=guild, data=data)

        webhook = await channel.create_webhook(name=user.name)
        if user.nick is None:
            the_name = user.name
        else:
            the_name = user.nick

        view = SubmittedJobView()
        msg = await webhook.send(
            content=content,
            username=the_name,
            avatar_url=user.avatar,
            view=view,
            wait=True,
        )
        record_id(
            job_id=data["id"],
            author_id=user.id,
            post_id=msg.id,
            channel_id=channel.id,
            guild_id=guild.id,
        )

        webhooks = await channel.webhooks()
        for w in webhooks:
            await w.delete()

        return msg

    def create_job_post_text(self, guild, data):
        LINE = "\n-----------------------------------------------------\n"

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

        if "acceptors" in data:
            acceptors = "**Accepted By:**\n" + str(data["acceptors"][0])
        else:
            acceptors = "**Accepted By:** " + "-" + "\n"

        content = title + body + LINE + acceptors

        return content
