import discord
from discord.ext import commands
from discord import ui
from utils.Tools import *

class UnbanView(ui.View):
    def __init__(self, user, author):
        super().__init__(timeout=120)
        self.user = user
        self.author = author
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("You are not allowed to interact with this!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

    @ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = UnbanReasonModal(user=self.user, author=self.author, view=self)
        await interaction.response.send_modal(modal)

    @ui.button(style=discord.ButtonStyle.gray, emoji="<:x_mark:1294218790082711553>")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()

class UnbanReasonModal(ui.Modal):
    def __init__(self, user, author, view):
        super().__init__(title="Unban Reason")
        self.user = user
        self.author = author
        self.view = view
        self.reason_input = ui.TextInput(label="Reason for Unbanning", placeholder="Provide a reason for unbanning or leave it blank.", required=False, max_length=512, style=discord.TextStyle.paragraph)
        self.add_item(self.reason_input)

    async def on_submit(self, interaction: discord.Interaction):
        reason = self.reason_input.value or "No reason provided"
        try:
            await self.user.send(f"<:success:1294218788689104957> You have been unbanned from **{self.author.guild.name}** by **{self.author}**. Reason: {reason}")
            dm_status = "Yes"
        except discord.Forbidden:
            dm_status = "No"
        except discord.HTTPException:
            dm_status = "No"

        await interaction.guild.unban(self.user, reason=f"Unban requested by {self.author} | Reason: {reason}")

        embed = discord.Embed(
            description=f"**<:user:1294654665895579721> Target User:** [{self.user}](https://discord.com/users/{self.user.id})\n"
                        f"<:mention:1294654604998475856> **User Mention:** {self.user.mention}\n"
                        f"**<:dm:1295595078122999915> DM Sent:** {dm_status}\n"
                        f"**<:reason:1295595129809141812> Reason:** {reason}",
            color=0x000000
        )
        embed.set_author(name=f"Successfully Unbanned {self.user.name}", icon_url=self.user.avatar.url if self.user.avatar else self.user.default_avatar.url)
        embed.add_field(name="<:moderator:1295601558985379852> Moderator:", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"Requested by {self.author}", icon_url=self.author.avatar.url if self.author.avatar else self.author.default_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        for item in self.view.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self.view)

class NotBannedView(ui.View):
    def __init__(self, user, author):
        super().__init__(timeout=120)
        self.user = user
        self.author = author
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("You are not allowed to interact with this!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

    @ui.button(label="Ban", style=discord.ButtonStyle.danger)
    async def ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = BanReasonModal(user=self.user, author=self.author, view=self)
        await interaction.response.send_modal(modal)

    @ui.button(style=discord.ButtonStyle.gray, emoji="<:x_mark:1294218790082711553>")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()

class BanReasonModal(ui.Modal):
    def __init__(self, user, author, view):
        super().__init__(title="Ban Reason")
        self.user = user
        self.author = author
        self.view = view
        self.reason_input = ui.TextInput(label="Reason for Banning", placeholder="Provide a reason for banning or leave it blank.", required=False, max_length=512, style=discord.TextStyle.paragraph)
        self.add_item(self.reason_input)

    async def on_submit(self, interaction: discord.Interaction):
        reason = self.reason_input.value or "No reason provided"
        try:
            await self.user.send(f"<:ban:1294218788689104957> You have been banned from **{self.author.guild.name}** by **{self.author}**. Reason: {reason}")
            dm_status = "Yes"
        except discord.Forbidden:
            dm_status = "No"
        except discord.HTTPException:
            dm_status = "No"

        await interaction.guild.ban(self.user, reason=f"Ban requested by {self.author} | Reason: {reason}")

        embed = discord.Embed(
            description=f"**<:user:1294654665895579721> Target User:** [{self.user}](https://discord.com/users/{self.user.id})\n"
                        f"<:mention:1294654604998475856> **User Mention:** {self.user.mention}\n"
                        f"**<:dm:1295595078122999915> DM Sent:** {dm_status}\n"
                        f"**<:reason:1295595129809141812> Reason:** {reason}",
            color=0x000000
        )
        embed.set_author(name=f"Successfully Banned {self.user.name}", icon_url=self.user.avatar.url if self.user.avatar else self.user.default_avatar.url)
        embed.add_field(name="<:moderator:1295601558985379852> Moderator:", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"Requested by {self.author}", icon_url=self.author.avatar.url if self.author.avatar else self.author.default_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        for item in self.view.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self.view)

class Unban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.from_rgb(0, 0, 0)

    @commands.hybrid_command(name="unban", help="Unbans a user from the Server", usage="unban <user>", aliases=["forgive", "pardon"])
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User, *, reason=None):
        try:
            await ctx.guild.fetch_ban(user)
            embed = discord.Embed(description=f"Are you sure you want to unban {user.mention}?", color=self.color)
            view = UnbanView(user=user, author=ctx.author)
            message = await ctx.send(embed=embed, view=view)
            view.message = message
        except discord.NotFound:
            embed = discord.Embed(description=f"**<:error:1294218790082711553> {user.mention} is not banned in this server.**", color=self.color)
            view = NotBannedView(user=user, author=ctx.author)
            message = await ctx.send(embed=embed, view=view)
            view.message = message

async def setup(bot):
    await bot.add_cog(Unban(bot))