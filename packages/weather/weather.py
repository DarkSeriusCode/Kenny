import requests
import discord
from discord.ext import commands
from discord.commands import command
from src.XEMB.XEMB_parser import XEMBParser, XEmbed


class Weather(commands.Cog):
    WEATHER_API_KEY = "f46b024ca288355c7b41f2c439d2d9b9"
    WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}&lang=ru"
    WEATHER_ICON_URL = "http://openweathermap.org/img/wn/{}@4x.png"

    def __init__(self, bot):
        self.bot = bot
        self.templates = XEMBParser("xml/weather_template.xml").parse_all()

    # ================================================================= #

    def create_weather_embed(self, city: str, resp) -> XEmbed:
        """Создаёт XEmbed на основе данных openweathermap"""
        try:
            temp = round(resp["main"]["temp"])
            state = resp["weather"][0]["description"]
            icon_url = self.WEATHER_ICON_URL.format(resp["weather"][0]["icon"])
            feels_like = round(resp["main"]["feels_like"])
        except KeyError:
            emb = self.templates["weather-city-fail"].copy()
            emb.title = emb.title.format(city)
        else:
            emb = self.templates["weather-city-ok"].copy()
            emb.title = emb.title.format(city)
            emb.description = emb.description.format(temp, feels_like, state)
            emb.set_thumbnail(url=icon_url)
        return emb

    # ================================================================= #

    @command()
    async def weather(self, ctx, city: str):
        """Выводит погоду в указанном городе"""
        resp = requests.get(self.WEATHER_API_URL.format(city, 
                                                        self.WEATHER_API_KEY)).json()
        emb = self.create_weather_embed(city, resp)
        await ctx.respond(embed=emb)


def setup(bot):
    bot.add_cog(Weather(bot))
