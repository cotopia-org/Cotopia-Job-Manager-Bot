import discord
import json
import requests
from bot_auth import create_token





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
        payload_dic['title'] = self.job_title.value
        payload_dic['workspace'] = interaction.guild.name + "/" + self.workspace.value
        if self.description.value != "":
            payload_dic['description'] = self.description.value
        if self.tags.value != "":
            split = self.tags.value.split(", ")
            payload_dic['tags'] = split
        if self.deadline.value != "":
            payload_dic['deadline'] = self.deadline.value

        headers = {"Authorization": create_token(self.users_info)}
        payload = json.dumps(payload_dic)
        url = "https://jobs.cotopia.social/bot/job"
        r = requests.post(url=url, data=payload, headers=headers)
        data = r.json()

        if r.status_code == 201:
            await interaction.response.send_message("Job Successfully Submitted!", ephemeral=True)
            guild = interaction.guild
            channel = guild.get_channel(1186373857062436954)
            body = str(data['created_at']) + "\n"
            ws = data['workspace'].replace(guild.name+ "/", "")
            body = body + "Workspace: " + ws + "\n"
            body = body + "Description: " + data["description"] + "\n"
            body = body + "Deadline: " + data["deadline"]
            embed = discord.Embed(title=data['title'], description=body, color=discord.Color.dark_blue())
            embed.set_author(name = "by <@" + str(data['creator']['discord_user_id']) + ">")
            await channel.send(embed=embed)
        else:
            await interaction.response.send_message(f"ERROR {r.status_code}\n{data}", ephemeral=True)
    
    def job_json_to_text(data: dict, guild_name: str):
        ws = data['workspace'].replace(guild_name + "/", "")
        body = "Workspace: " + ws + "\n"
        body = body + "Description: " + data["description"] + "\n"
        body = body + "Deadline: " + data["deadline"]
        embed = discord.Embed(title=data['title'], description=body, color=discord.Color.dark_blue())
        embed.set_author(name = "by <@" + data['creator']['discord_user_id'] + ">", url=data['created_at'])
        return embed
