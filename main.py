import os
import traceback
import discord
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
    tb_file = open("log/traceback.txt", "a")
    traceback.print_exception(type(err), err, err.__traceback__, file=tb_file)
    print("\n\n>", "=" * 77, "<\n", file=tb_file)

    print(f"/{ctx.command.qualified_name}: {err} (for more info see log/traceback.txt)")
    await ctx.respond("Что-то пошло не так!", ephemeral=True)

# ------------------------------------------------------------------------------


def main():
    tb_file_path = "log/traceback.txt"
    # Just create file
    os.makedirs(os.path.dirname(tb_file_path), exist_ok=True)
    open("log/traceback.txt", "w").close()

    pm = PackageManager(bot)
    pm.load_all()
    bot.run(os.getenv("TOKEN"))


if __name__ == '__main__':
    main()
