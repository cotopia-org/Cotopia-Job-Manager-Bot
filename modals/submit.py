import json
from datetime import datetime

import discord
import requests

from bot_auth import create_token
from utils.job_id_coder import gen_code
from views.submitted_job import SubmittedJobView


class JobSubmitModal(discord.ui.Modal, title="Submit Job"):
    users_info = None
    self_accept = False

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
        post_data = {}
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
            print(f"status code: {r.status_code}\n{data}")
            post_data = data

            # self accept
            if self.self_accept:
                job_id = data["id"]
                url = f"https://jobs.cotopia.social/bot/accept/{job_id}"
                self_accept_req = requests.post(url=url, headers=headers)
                self_accept_data = self_accept_req.json()
                if self_accept_req.status_code == 201:
                    print(
                        f"status code: {self_accept_req.status_code}\n{self_accept_data}"
                    )
                    post_data["acceptors"] = [interaction.user]

                    url = f"https://jobs.cotopia.social/bot/accepted_jobs/{job_id}"
                    pl = {"acceptor_status": "doing"}
                    update_status_req = requests.put(url=url, json=pl, headers=headers)
                    update_status_data = update_status_req.json()
                    if update_status_req.status_code == 200:
                        print(
                            f"status code: {update_status_req.status_code}\n{update_status_data}"
                        )
                    else:
                        print(
                            f"status code: {update_status_req.status_code}\n{update_status_data}"
                        )
                else:
                    print(
                        f"status code: {self_accept_req.status_code}\n{self_accept_data}"
                    )

        else:
            await interaction.response.send_message(
                f"ERROR {r.status_code}\n{data}", ephemeral=True
            )
            print(f"ERROR {r.status_code}\n{data}")

        if post_data != {}:
            await self.post_the_job_to_channel(
                guild=interaction.guild,
                channel=interaction.guild.get_channel(1186373857062436954),
                user=interaction.user,
                data=post_data,
            )

    async def post_the_job_to_channel(self, guild, channel, user, data):
        content = self.create_job_post_text(guild=guild, data=data)

        webhook = await channel.create_webhook(name=user.name)
        if user.nick is None:
            the_name = user.name
        else:
            the_name = user.nick

        view = SubmittedJobView()
        await webhook.send(
            content=content,
            username=the_name,
            avatar_url=user.avatar,
            view=view,
        )

        webhooks = await channel.webhooks()
        for w in webhooks:
            await w.delete()

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

        if data["acceptors"]:
            acceptors = "**Accepted By:**\n" + data["acceptors"][0].mention
        else:
            acceptors = "**Accepted By:** " + "-" + "\n"

        id_line = "id: " + gen_code(data["id"])

        content = title + LINE + body + LINE + acceptors + LINE + id_line

        return content
