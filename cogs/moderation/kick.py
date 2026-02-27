import discord
from discord.ext import commands
from discord import ui
from utils.Tools import *

class KickView(ui.View):
    def __init__(self, member, author):
        super().__init__(timeout=120)
        self.member = member
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
        modal = ReasonModal(member=self.member, author=self.author, view=self)
        await interaction.response.send_modal(modal)

    @ui.button(style=discord.ButtonStyle.gray, emoji="<:x_mark:1294218790082711553>")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()

class ReasonModal(ui.Modal):
    def __init__(self, member, author, view):
        super().__init__(title="Kick Reason")
        self.member = member
        self.author = author
        self.view = view
        self.reason_input = ui.TextInput(label="Reason for Kicking", placeholder="Provide a reason to kick or leave it blank for no reason.", required = False, max_length=2000, style=discord.TextStyle.paragraph)
        self.add_item(self.reason_input)

    async def on_submit(self, interaction: discord.Interaction):
        reason = self.reason_input.value or "No reason provided"
        try:
            await self.member.send(f"<:kick:1294218788689104957> You have been kicked from **{self.author.guild.name}** by **{self.author}**. Reason: {reason or 'No reason provided'}")
            dm_status = "Yes"
        except discord.Forbidden:
            dm_status = "No"
        except discord.HTTPException:
            dm_status = "No"

        await self.member.kick(reason=f"Kicked by {self.author} | Reason: {reason}")
            
        embed = discord.Embed(description=f"**<:user:1294654665895579721> Target User:** [{self.member}](https://discord.com/users/{self.member.id})\n<:mention:1294654604998475856> **User Mention:** {self.member.mention}\n**<:dm:1295595078122999915> DM Sent:** {dm_status}\n**<:reason:1295595129809141812> Reason:** {reason}", color=0x000000)
        embed.set_author(name=f"Successfully Kicked {self.member.name}", icon_url=self.member.avatar.url if self.member.avatar else self.member.default_avatar.url)
        embed.add_field(name="<:moderator:1295601558985379852> Moderator:", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"Requested by {self.author}", icon_url=self.author.avatar.url if self.author.avatar else self.author.default_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.edit_message(embed=embed, view=None)

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.from_rgb(0, 0, 0)

    @commands.hybrid_command(name="kick", help="Kicks a member from the server.", usage="kick <member> [reason]", aliases=["kickmember"])
    @blacklist_check()
    @ignore_check()
    @top_check()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick_command(self, ctx, member: discord.Member, *, reason: str = None):
        if member == ctx.author:
            return await ctx.reply("You cannot kick yourself.")

        if member == ctx.bot.user:
            return await ctx.reply("You cannot kick me.")

        if not ctx.author == ctx.guild.owner:
            if member == ctx.guild.owner:
                return await ctx.reply("I cannot kick the server owner.")

            if ctx.author.top_role <= member.top_role:
                return await ctx.reply("You cannot kick a member with a higher or equal role.")

        if ctx.guild.me.top_role <= member.top_role:
            return await ctx.reply("I cannot kick a member with a higher or equal role.")

        embed = discord.Embed(description=f"Are you sure you want to kick {member.mention}?", color=self.color)
        view = KickView(member=member, author=ctx.author)
        message = await ctx.send(embed=embed, view=view)
        view.message = message