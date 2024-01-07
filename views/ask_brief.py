import discord
from modals.submit import JobSubmitModal



class AskBriefView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.addressee = None  # the user that is asked for brief
        self.ask_msg_id = 0

    @discord.ui.button(label="➕ Write A Task", style=discord.ButtonStyle.primary)
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

    # @discord.ui.button(label="Your Tasks", style=discord.ButtonStyle.primary)
    # async def tasks(self, interaction: discord.Integration, button: discord.ui.Button):
    #     if self.addressee == interaction.user:
    #         pass
    #     else:
    #         await interaction.response.send_message(
    #             "You are not the addressee!", ephemeral=True
    #         )

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
