import discord
from discord.ext import commands
from discord import ui
from utils.Tools import *

class BanView(ui.View):
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
        modal = ReasonModal(user=self.user, author=self.author, view=self)
        await interaction.response.send_modal(modal)

    @ui.button(style=discord.ButtonStyle.gray, emoji="<:x_mark:1294218790082711553>")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()

class AlreadyBannedView(ui.View):
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
            await self.message.edit(view=self)

    @ui.button(label="Unban", style=discord.ButtonStyle.success)
    async def unban(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ReasonModal(user=self.user, author=self.author, view=self)
        await interaction.response.send_modal(modal)

    @ui.button(style=discord.ButtonStyle.gray, emoji="<:x_mark:1294218790082711553>")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()

class ReasonModal(ui.Modal):
    def __init__(self, user, author, view):
        super().__init__(title="Ban Reason")
        self.user = user
        self.author = author
        self.view = view
        self.reason_input = ui.TextInput(label="Reason for Banning", placeholder="Provide a reason to ban or leave it blank for no reason.", required = False, max_length=2000, style=discord.TextStyle.paragraph)
        self.add_item(self.reason_input)

    async def on_submit(self, interaction: discord.Interaction):
        reason = self.reason_input.value or "No reason provided"
        try:
            await self.user.send(f"<:ban:1294218788689104957> You have been banned from **{self.author.guild.name}** by **{self.author}**. Reason: {reason or 'No reason provided'}")
            dm_status = "Yes"
        except discord.Forbidden:
            dm_status = "No"
        except discord.HTTPException:
            dm_status = "No"

        await interaction.guild.ban(self.user, reason=f"Ban requested by {self.author} for reason: {reason or 'No reason provided'}")
            
        embed = discord.Embed(description=f"**<:user:1294654665895579721> Target User:** [{self.user}](https://discord.com/users/{self.user.id})\n<:mention:1294654604998475856> **User Mention:** {self.user.mention}\n**<:dm:1295595078122999915> DM Sent:** {dm_status}\n**<:reason:1295595129809141812> Reason:** {reason}", color=0x000000)
        embed.set_author(name=f"Successfully Banned {self.user.name}", icon_url=self.user.avatar.url if self.user.avatar else self.user.default_avatar.url)
        embed.add_field(name="<:moderator:1295601558985379852> Moderator:", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"Requested by {self.author}", icon_url=self.author.avatar.url if self.author.avatar else self.author.default_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.edit_message(embed=embed, view=None)

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.from_rgb(0, 0, 0)

    def get_user_avatar(self, user):
        return user.avatar.url if user.avatar else user.default_avatar.url

    @commands.hybrid_command(name="ban", help="Bans a user from the Server", usage="ban <member>", aliases=["fuckban", "hackban"])
    @blacklist_check()
    @ignore_check()
    @top_check()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason=None):
        member = ctx.guild.get_member(user.id)

        bans = [entry async for entry in ctx.guild.bans()]
        if any(ban_entry.user.id == user.id for ban_entry in bans):
            embed = discord.Embed(description=f"**<:error:1294218790082711553> {user.mention} is already banned in this server.**", color=self.color)
            view = AlreadyBannedView(user=user, author=ctx.author)
            message = await ctx.send(embed=embed, view=view)
            view.message = message 
            return

        if member == ctx.guild.owner:
            error = discord.Embed(color=self.color, description="<:error:1294218790082711553> I can't ban the Server Owner!")
            return await ctx.send(embed=error)

        if isinstance(member, discord.Member) and member.top_role >= ctx.guild.me.top_role:
            error = discord.Embed(color=self.color, description="<:error:1294218790082711553> I can't ban a user with a higher or equal role!")
            return await ctx.send(embed=error)

        if isinstance(member, discord.Member):
            if ctx.author != ctx.guild.owner:
                if member.top_role >= ctx.author.top_role:
                    error = discord.Embed(color=self.color, description="<:error:1294218790082711553> You can't ban a user with a higher or equal role!")
                    return await ctx.send(embed=error)

        embed = discord.Embed(description=f"Are you sure you want to ban {user.mention}?", color=self.color)
        view = BanView(user=user, author=ctx.author)
        message = await ctx.send(embed=embed, view=view)
        view.message = message