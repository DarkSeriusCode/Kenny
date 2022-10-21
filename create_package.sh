#! /bin/bash

printf "Enter a name of project: "
read NAME

mkdir -p packages
cd packages

if [[ -d "./$NAME" ]]; then
    echo "The package with name \"$NAME\" is already exists!"
    exit 1;
fi

mkdir -p $NAME; cd $NAME

echo "{
    \"name\": \"$NAME\",
    \"desсription\": \"None\",
    \"version\": 0.1,
    \"run_file\": \"main.py\",
    \"docs\": \"${NAME}_docs.xml\"
}
" > config.json

echo "import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, command


class $NAME(commands.Cog):
    ${NAME}_g = SlashCommandGroup(\"$NAME\", \"descr\")

    def __init__(self, bot):
        self.bot = bot

    # ================================================================= #

    @${NAME}_g.command()
    async def hello_from_$NAME(self, ctx):
        await ctx.respond(\"Hello world from $NAME\")


def setup(bot):
    bot.add_cog($NAME(bot))
" > main.py