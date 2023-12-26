import json
from datetime import datetime

import discord
import requests

from bot_auth import create_token
from views.submitted_job import SubmittedJobView
from utils.job_id_coder import gen_code


class JobSubmitModal(discord.ui.Modal, title="Submit Job"):
    users_info = None

    job_title = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Title",
        placeholder="Title of the job",
        required=True,
    )
    workspace = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Workspace",
        placeholder="What category/workspace it belongs to?",
        required=False,
    )
    description = discord.ui.TextInput(
        style=discord.TextStyle.paragraph,
        label="Description",
        placeholder="Please describe the job as clearly as possible.",
        max_length=512,
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
        placeholder="yyy-mm-dd HH:MM",
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        payload_dic = {}
        payload_dic["title"] = self.job_title.value
        payload_dic["workspace"] = interaction.guild.name + "/" + self.workspace.value
        if self.description.value != "":
            payload_dic["description"] = self.description.value
        if self.tags.value != "":
            split = self.tags.value.split(", ")
            payload_dic["tags"] = split
        if self.deadline.value != "":
            payload_dic["deadline"] = self.deadline.value

        headers = {"Authorization": create_token(self.users_info)}
        payload = json.dumps(payload_dic)
        url = "https://jobs.cotopia.social/bot/job"
        r = requests.post(url=url, data=payload, headers=headers)
        data = r.json()

        if r.status_code == 201:
            await interaction.response.send_message(
                "Job Successfully Submitted!", ephemeral=True
            )
            guild = interaction.guild
            channel = guild.get_channel(1186373857062436954)

            # created_at = datetime.strptime(data["created_at"], "%Y-%m-%dT%H:%M:%S.%f")
            # post_date = created_at.strftime("%Y-%m-%d  %H:%M")
            title = "**" + data["title"] + "**"

            if data["description"]:
                body = "**Description:**\n" + data["description"] + "\n\n"
            else:
                body = "**Description:** " + "-" + "\n\n"
            ws = data["workspace"].replace(guild.name + "/", "")
            if len(ws) > 0:
                body = body + "**Workspace:** " + ws + "\n"
            else:
                body = body + "**Workspace:** " + "-" + "\n"
            if data["deadline"]:
                deadline = datetime.strptime(data["deadline"], "%Y-%m-%dT%H:%M:%S")
                body = (
                    body
                    + "**Deadline:** "
                    + deadline.strftime("%Y-%m-%d  %H:%M")
                    + "\n"
                )
            else:
                body = body + "Deadline: " + "-" + "\n"
            tags = ""
            if data["tags"]:
                for t in data["tags"]:
                    tags = tags + "**[" + t + "]** "
            body = body + tags
            body = body + "\n\nid: " + gen_code(data['id'])
            
            content = title + "\n\n" + body

            webhook = await channel.create_webhook(name=interaction.user.name)
            if interaction.user.nick is None:
                the_name = interaction.user.name
            else:
                the_name = interaction.user.nick

            view = SubmittedJobView()
            await webhook.send(
                content=content,
                username=the_name,
                avatar_url=interaction.user.avatar,
                view=view,
            )

            webhooks = await channel.webhooks()
            for w in webhooks:
                await w.delete()

        else:
            await interaction.response.send_message(
                f"ERROR {r.status_code}\n{data}", ephemeral=True
            )
