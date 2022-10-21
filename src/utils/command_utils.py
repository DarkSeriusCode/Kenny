import discord
from discord.ext import commands


class ChecksMixin:
    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, err):
        if issubclass(err.__class__, commands.CheckFailure):
            await ctx.respond("У вас нет прав на использование этой команды!",
                              ephemeral=True)
