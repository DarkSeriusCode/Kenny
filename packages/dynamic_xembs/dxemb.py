import re
import discord
import discord.ui
import xml.etree.ElementTree as et
from discord.ext import commands
from src.XEMB.XEMB_parser import XEMBParser, XEMBException

from src.components.base import Select

class DynamicXEMB(commands.Cog):
    xemb_regexp = re.compile(r"```xml\s<!DOCTYPE XEMB>(\S*\s*)+```")

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        raw = msg.content
        if re.match(self.xemb_regexp, raw):
            raw = raw[6:-3]
            # Проверка на ошибки при парсинге
            try: 
                xml_tag = et.Element(et.fromstring(raw))
            except et.ParseError as exc:
                await msg.channel.send(f"```{exc.msg}```")
                return 
            # Ошибки XEMB парсера
            try:
                self.parser = XEMBParser(xml_tag)
                self.parser.parse_all()
            except XEMBException as exc:
                await msg.channel.send(f"```{exc.text}```")
                return

            if len(self.parser) > 1:
                opts = []
                for lbl in self.parser.embeds:
                    opts.append({"label": lbl, "value": lbl})
                
                s = Select(opts, self.select_callback)
                view = discord.ui.View(s, timeout=None)
                await msg.channel.send(content="**__{}__**".format(opts[0]["label"]),
                                       embed=self.parser.get_by_index(0), 
                                       view=view)
            elif len(self.parser) == 0:
                await msg.channel.send("```Не найдено ни одного Embed сообщения!```")
            else:
                emb = self.parser.get_by_index(0)
                await msg.channel.send(embed=emb)

    async def select_callback(self, interaction):
        xemb_name = interaction.data["values"][0]
        await interaction.message.edit(content=f"**__{xemb_name}__**",
                                       embed=self.parser.get_by_name(xemb_name))

def setup(bot):
    bot.add_cog(DynamicXEMB(bot))
