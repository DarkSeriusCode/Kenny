import discord
import json
import asyncio
import re
from discord import utils
from typing import List, Any, Callable
from discord.ext import commands, tasks

# ------------------------------------------------------------------------------

def predicate_fabric(compare: Any) -> Callable[[Any], bool]:
	return lambda x: x.name == compare

# ------------------------------------------------------------------------------

class DynamicChannes(commands.Cog):
	"""Класс для динамичных каналов (каналы, которые создаются и удаляются 
	динамически)."""
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		config = json.load(open("json/dynamic_channels_config.json"))

		self.category_name = config["category_name"]
		self.limit = config["limit"]
		self.fabric_channel_name = config["fabric_channel_name"]
		self.channels_name = config["channels_name"]
		self.chname_tmpl = config["channels_name_tmpl"]

		# Создаём предикаты для более удобного поиска
		# Динамичная категория
		self.has_pcat = predicate_fabric(self.category_name) 
		# Динамичный канал
		self.has_pch = predicate_fabric(self.fabric_channel_name) 

	# =========================================================== #

	@tasks.loop(seconds=10)
	async def create_loop(self):
		for guild in self.bot.guilds:
			await self.create_dynamic_category(guild)
			await self.create_fabric_channel(guild)

	@commands.Cog.listener()
	async def on_ready(self):
		for guild in self.bot.guilds:
			await self.clean_pcat(guild)
		self.create_loop.start()

	def cog_unload(self):
		self.create_loop.close()

	@commands.Cog.listener()
	async def on_voice_state_update(self, user, before, after):
		guild = user.guild

		# Ползователь подключается к фабричному каналу
		if after.channel and after.channel.name == self.fabric_channel_name:
				await self.create_dynamic_channel(guild, user)

		# Пользователь отключается от личного канала
		# Если после ухода канал пуст, то удалить онный
		if before.channel and len(before.channel.members) <= 0:
			if before.channel.name == self.channels_name.format(user=user.name):
				await before.channel.delete()

	# =========================================================== #

	def get_pcat(self, guild):
		"""Возвращает динамичную категорию на сервере"""
		return utils.get(guild.categories, name=self.category_name)

	# =========================================================== #

	async def create_dynamic_category(self, guild):
		"""Создаёт категорию (self.category_name) для динамичных каналов"""
		if not utils.find(self.has_pcat, guild.categories):
			await guild.create_category(position=1, name=self.category_name)

	async def create_fabric_channel(self, guild):
		"""Создаёт фабричный динамичный канал"""
		pcat = self.get_pcat(guild)
		if not utils.find(self.has_pch, pcat.voice_channels):
			await pcat.create_voice_channel(name=self.fabric_channel_name, 
											user_limit=1)

	async def create_dynamic_channel(self, guild, user: discord.Member):
		"""Если пользователь создаёт канал и его у него нет, то создать
		Иначе перекинуть в ранее созданый"""
		# TODO: Разбить на более мелкие функции
		pcat = self.get_pcat(guild)
		channel_name = self.channels_name.format(user=user.name)

		if not utils.get(pcat.voice_channels, name=channel_name):
			await pcat.create_voice_channel(name=channel_name, user_limit=self.limit)
		await user.move_to(utils.get(pcat.voice_channels, name=channel_name))

	# =========================================================== #

	async def clean_pcat(self, guild):
		"""Удаляет лишние и пустые каналы в приватной категории"""
		pcat = self.get_pcat(guild)
		if not pcat: return

		for channel in pcat.voice_channels:
			if len(channel.members) <= 0 and re.match(self.chname_tmpl, channel.name): 
				await channel.delete()
			if (not re.match(self.chname_tmpl, channel.name) and 
					channel.name != self.fabric_channel_name):
				await channel.delete()

def setup(bot):
	bot.add_cog(DynamicChannes(bot))