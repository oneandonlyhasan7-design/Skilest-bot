import discord
from discord.ext import commands
import aiosqlite
from utils.Tools import *

class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.initialize_db())

    async def initialize_db(self):
        self.db = await aiosqlite.connect('db/anti.db')
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS whitelisted_users (
                guild_id INTEGER,
                user_id INTEGER,
                PRIMARY KEY (guild_id, user_id)
            )
        ''')
        await self.db.commit()

    @commands.hybrid_command(name='whitelist', aliases=['wl'], help="Whitelists a user from antinuke.")
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

        async with self.db.execute("SELECT * FROM whitelisted_users WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, member.id)) as cursor:
            data = await cursor.fetchone()

        if data:
            embed = discord.Embed(color=0x000000, description=f"<:error:1294218790082711553> **{member.mention} is already whitelisted.**")
            await ctx.send(embed=embed)
        else:
            await self.db.execute("INSERT INTO whitelisted_users (guild_id, user_id) VALUES (?, ?)", (ctx.guild.id, member.id))
            await self.db.commit()
            embed = discord.Embed(color=0x000000, description=f"<:success:1294218788689104957> **Successfully whitelisted {member.mention}.**")
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='unwhitelist', aliases=['unwl'], help="Unwhitelists a user from antinuke.")
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

        async with self.db.execute("SELECT * FROM whitelisted_users WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, member.id)) as cursor:
            data = await cursor.fetchone()

        if not data:
            embed = discord.Embed(color=0x000000, description=f"<:error:1294218790082711553> **{member.mention} is not whitelisted.**")
            await ctx.send(embed=embed)
        else:
            await self.db.execute("DELETE FROM whitelisted_users WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, member.id))
            await self.db.commit()
            embed = discord.Embed(color=0x000000, description=f"<:success:1294218788689104957> **Successfully unwhitelisted {member.mention}.**")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Whitelist(bot))