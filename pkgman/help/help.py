import discord
from typing import List, Dict
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup, SlashCommand, command
from ..package_manager import PackageManager
from src.XEMB.XEMB_parser import XEmbed, XEMBParser


# ------------------------------------------------------------------------------


def get_all_components(prefix: str) -> Dict[str, XEmbed]:
    pm = PackageManager(None)
    cmds = {}
    for pkg in filter(lambda p: p.docs, pm.all_packages):
        xembeds = pkg.docs_parser.parse_all()
        xembeds = {n.replace(prefix, ""): e for n, e in xembeds.items()
                   if n.startswith(prefix)}
        for ename, xembed in xembeds.items():
            cmds[f"{ename}"] = xembed
    return cmds


def get_all_manuals(other_path: str) -> Dict[str, XEmbed]:
    """Возвращает все пакетные мануалы, а также мануалы из other_path"""
    mans = get_all_components("man-")
    mans.update(XEMBParser(other_path).parse_all())
    return mans


def get_cmd_opt() -> Option:
    cmds = get_all_components("cmd-")
    opt = Option(str, "О какой команде вывести справку.", required=True,
                  choices=cmds.keys())
    if not cmds:
        opt.description = "Команд нет или у пакетов, содержащих их, отсутствует\
 документация"
    return opt


def get_man_opt() -> Option:
    mans = get_all_manuals("xml/help.xml")
    opt = Option(str, "Выберете мануал для прочтния", required=True,
                  choices=mans.keys())
    if not mans:
        opt.description = "Мануалов нет или у пакетов, содержащих их, \
отсутствует документация"
    return opt


# ------------------------------------------------------------------------------


class Help(commands.Cog):
    helps = SlashCommandGroup("help", "desc", guild_ids=[634453910236561419])

    def __init__(self, bot):
        self.bot = bot
        self.pm = PackageManager(bot)
        self._cmd_cache = get_all_components("cmd-")
        self._man_cache = get_all_manuals("xml/help.xml")
    
    @command()
    async def help(self, ctx, man: get_man_opt()="Про Кенни"):
        """Выводит справку о чём-либо"""
        if man not in self._man_cache: 
            await ctx.delete()
            return
        await ctx.respond(embed=self._man_cache[man])

    @helps.command()
    async def command(self, ctx, cmd: get_cmd_opt()):
        """Выводит справку по команде"""
        if cmd not in self._cmd_cache: 
            await ctx.delete()
            return
        await ctx.respond(embed=self._cmd_cache[cmd])

def setup(bot):
    bot.add_cog(Help(bot))
