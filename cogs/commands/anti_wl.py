"""import discord
from discord.ext import commands
import aiosqlite
from utils.Tools import *

PERMISSIONS = {
    "bypass_ban": "Bypass Ban",
    "bypass_kick": "Bypass Kick",
    "bypass_channel": "Bypass Channel Create/Delete/Update",
    "bypass_role": "Bypass Role Create/Delete/Update",
    "bypass_webhook": "Bypass Webhook Create/Delete",
    "bypass_everyone": "Bypass Everyone/Here Pings",
    "bypass_prune": "Bypass Prune",
    "bypass_bot_add": "Bypass Bot Additions",
    "bypass_guild_update": "Bypass Guild Updates",
    "bypass_member_update": "Bypass Member Updates",
    "bypass_integration_create": "Bypass Integration Creation",
}

class WhitelistView(discord.ui.View):
    def __init__(self, ctx, member):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.member = member
        self.bot = ctx.bot
        self.db = self.bot.db
        self.create_buttons()

    async def get_user_permissions(self):
        async with self.db.execute("SELECT permission FROM whitelisted_permissions WHERE guild_id = ? AND user_id = ?", (self.ctx.guild.id, self.member.id)) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    def create_buttons(self):
        self.clear_items()
        loop = asyncio.get_event_loop()
        user_perms = loop.run_until_complete(self.get_user_permissions())

        for perm, desc in PERMISSIONS.items():
            granted = perm in user_perms
            button = discord.ui.Button(
                label=desc,
                style=discord.ButtonStyle.success if granted else discord.ButtonStyle.danger,
                custom_id=f"wl_{perm}_{self.member.id}"
            )
            button.callback = self.button_callback
            self.add_item(button)

    async def button_callback(self, interaction: discord.Interaction):
        if not (interaction.user.guild_permissions.administrator or await is_bot_owner(interaction.user.id)):
            return await interaction.response.send_message("You do not have permission to use this.", ephemeral=True)

        custom_id = interaction.data["custom_id"]
        _, perm, member_id = custom_id.split("_")

        if int(member_id) != self.member.id:
            return

        async with self.db.execute("SELECT permission FROM whitelisted_permissions WHERE guild_id = ? AND user_id = ? AND permission = ?", (self.ctx.guild.id, self.member.id, perm)) as cursor:
            data = await cursor.fetchone()

        if data:
            await self.db.execute("DELETE FROM whitelisted_permissions WHERE guild_id = ? AND user_id = ? AND permission = ?", (self.ctx.guild.id, self.member.id, perm))
        else:
            await self.db.execute("INSERT INTO whitelisted_permissions (guild_id, user_id, permission) VALUES (?, ?, ?)", (self.ctx.guild.id, self.member.id, perm))
        
        await self.db.commit()
        self.create_buttons()
        await interaction.response.edit_message(view=self)


class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.initialize_db())

    async def initialize_db(self):
        self.bot.db = await aiosqlite.connect('db/anti.db')
        await self.bot.db.execute('DROP TABLE IF EXISTS whitelisted_users')
        await self.bot.db.execute('''
            CREATE TABLE IF NOT EXISTS whitelisted_permissions (
                guild_id INTEGER,
                user_id INTEGER,
                permission TEXT,
                PRIMARY KEY (guild_id, user_id, permission)
            )
        ''')
        await self.bot.db.commit()

    @commands.hybrid_command(name='whitelist', aliases=['wl'], help="Whitelists a user from antinuke with granular permissions.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def whitelist(self, ctx, member: discord.Member = None):
        if not member:
            embed = discord.Embed(color=0x000000, title="Whitelist Commands", description="Whitelist a user to bypass antinuke.")
            embed.add_field(name="Usage", value=f"{ctx.prefix}whitelist <user>")
            await ctx.send(embed=embed)
            return

        view = WhitelistView(ctx, member)
        embed = discord.Embed(color=0x000000, description=f"Configure permissions for {member.mention}")
        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name='unwhitelist', aliases=['unwl'], help="Removes all whitelist permissions from a user.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def unwhitelist(self, ctx, member: discord.Member = None):
        if not member:
            embed = discord.Embed(color=0x000000, title="Unwhitelist Commands", description="Unwhitelist a user to re-enable antinuke for them.")
            embed.add_field(name="Usage", value=f"{ctx.prefix}unwhitelist <user>")
            await ctx.send(embed=embed)
            return

        async with self.bot.db.execute("SELECT * FROM whitelisted_permissions WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, member.id)) as cursor:
            data = await cursor.fetchone()

        if not data:
            embed = discord.Embed(color=0x000000, description=f"<:error:1294218790082711553> **{member.mention} is not whitelisted.**")
            await ctx.send(embed=embed)
        else:
            await self.bot.db.execute("DELETE FROM whitelisted_permissions WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, member.id))
            await self.bot.db.commit()
            embed = discord.Embed(color=0x000000, description=f"<:success:1294218788689104957> **Successfully unwhitelisted {member.mention}.**")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Whitelist(bot))
""