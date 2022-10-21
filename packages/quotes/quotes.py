import discord
import random
import xml.etree.ElementTree as et
from discord.ext import commands
from discord.commands import Option, command, SlashCommandGroup
from src.XEMB.XEMB_parser import XEMBParser, XEmbed

from src.components import base
from src.components.slider import Slider
from discord.ui import View


class Quotes(commands.Cog):
    q = SlashCommandGroup("quote", "Цитаты", guild_ids=[634453910236561419])

    def __init__(self, bot):
        self.bot = bot

        self.XML = et.ElementTree(file="xml/quotes/quotes.xml").getroot()
        raw_main_quotes = self.XML.find("quotes").text.split("\n")[1:-1]

        # Шаблоны Embed cообщений из XEMB файла
        self.templates = XEMBParser("xml/quotes/quotes_template.xml").parse_all()

        self.main_quotes = list(map(lambda x: x.strip(), raw_main_quotes))
        self.quotes_on_page = 16
        quotes_count = len(self.main_quotes)

        # Индекс поледней страницы
        pind = quotes_count / self.quotes_on_page 
        # Если целое цисло, то вычитаем единицу, если дробное, 
        # то отбрасываем дробную часть
        self.pages_count = int(pind - (not (pind > int(pind))))

    def get_random_quote(self) -> XEmbed:
        emb = self.templates["random-tmpl"].copy()
        emb.description = emb.description.format(random.choice(self.main_quotes))
        return emb

    def page_generator(self, ind: int) -> XEmbed:
        """Генерирует страницы с цитатами по номеру (страницы)"""
        emb = self.templates["quotes-list-tmpl"].copy()
        emb.title = emb.title.format(ind + 1, self.pages_count + 1)

        quote_beg = ind * self.quotes_on_page
        page_quotes = self.main_quotes[quote_beg:quote_beg + self.quotes_on_page]
        descr = ""
        for quote_num, quote in enumerate(page_quotes, quote_beg + 1):
            descr += f"> **{quote_num}.** {quote}\n"

        emb.description = descr
        return emb

    # ================================================================= #

    @command()
    async def quote(self, ctx):
        """Выводит случайную цитату"""
        quote = self.get_random_quote()
        view = View(base.Button(self.roll_btn_callback, emoji="🔄"), timeout=None)
        await ctx.respond(embed=quote, view=view)

    @q.command()
    async def list(self, ctx):
        """Выводит список цитат"""
        view = Slider(self.page_generator, self.pages_count)
        await view.send(ctx)

    # ================================================================= #

    async def roll_btn_callback(self, interaction):
        quote = self.get_random_quote()
        await interaction.message.edit(embed=quote)


def setup(bot):
    bot.add_cog(Quotes(bot))

