import discord
from discord.ext import commands
from discord.commands import command, Option


clear_opt = Option(int, "Сколько сообщений очистить", required=True)


class ChatUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(guild_ids=[634453910236561419])
    async def clear(self, ctx, number: clear_opt):
        """Очищает чат от number сообщений"""
        await ctx.delete()
        await ctx.channel.purge(limit=number)

def setup(bot):
    bot.add_cog(ChatUtils(bot))
