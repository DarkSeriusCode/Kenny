import discord
import os
import dotenv
from discord.ext import commands
from pkgman.package_manager import PackageManager
dotenv.load_dotenv()

# ------------------------------------------------------------------------------

bot = commands.Bot(command_prefix="!",
                   sync_commands=True,
                   activity=discord.Game("/help"),
                   case_insensitive=True,
                   help_command=None,
                   intents=discord.Intents.all(),
                   test_guilds=[634453910236561419])


@bot.event
async def on_ready():
    print("=====[Started]=====")

@bot.event
async def on_application_command_error(ctx, err):
    print(f"/{ctx.command.qualified_name}: {err}")
    await ctx.respond("Что-то пошло не так!", ephemeral=True)

# ------------------------------------------------------------------------------


def main():
    os.system("clear")
    pm = PackageManager(bot)
    pm.load_all()
    bot.run(os.getenv("TOKEN"))


if __name__ == '__main__':
    main()
