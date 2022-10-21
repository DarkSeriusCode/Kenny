import os
import random
import discord
from discord.ui import View
from typing import List
from discord.ext import commands
from discord.commands import SlashCommandGroup, command


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.images = [f"img/" + f for f in os.listdir("img")]

    async def send_image(self, ctx, img_path: str):
        await ctx.respond("Супер случайная фотка!", file=discord.File(img_path))

    # ================================================================= #

    @command()
    async def image(self, ctx):
        """Выводит случайную картинку из всех категорий"""
        img = random.choice(self.images)
        await self.send_image(ctx, img)

def setup(bot):
    bot.add_cog(Images(bot))