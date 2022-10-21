import discord
from discord.ext import commands
from discord.ext.commands import check_any, has_role, has_permissions
from discord.commands import SlashCommandGroup
from .package_manager import PackageManager
from src.utils import command_utils


class PackageManagerDiscord(commands.Cog, command_utils.ChecksMixin):
    pmd = SlashCommandGroup("pkg", "pkgman", guild_ids=[634453910236561419])
    def __init__(self, bot):
        self.bot = bot
        self.pm = PackageManager(bot)

    @check_any(has_role(703599297802797086), has_permissions(administrator=True))
    @pmd.command()
    async def status(self, ctx):
        """Отображает статус всех пакетов"""
        emb = discord.Embed(title=":package: Пакеты :package:")
        emb.description = f"_Найдено {len(self.pm.all_packages)}_ :package:"
        title_template = "{} **[**{}**]**"

        for pkg, stat in self.pm.statuses.items():
            emoji = ":green_square:" if stat else ":red_square:"
            title = title_template.format(pkg.name, emoji)
            emb.add_field(name=title, value=str(pkg))

        await ctx.respond(embed=emb)


def setup(bot):
    bot.add_cog(PackageManagerDiscord(bot))
