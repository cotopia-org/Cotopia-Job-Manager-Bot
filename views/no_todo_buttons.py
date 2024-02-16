import discord

from modals.submit import JobSubmitModal


class NoTodoButtons(discord.ui.View):
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
