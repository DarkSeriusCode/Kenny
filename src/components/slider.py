import discord.ui
from discord import Embed
from typing import Callable
from . import abc


class Slider(abc.AbstractComponent):
	"""Класс для представления страничного виджета"""
	def __init__(self, page_gen: Callable[[int], Embed], max_pages: int):
		super().__init__()
		self.page_generator = page_gen
		self.page_index = 0
		self.max_pages = max_pages
		self.page = self.page_generator(0)

	async def send(self, ctx):
		await ctx.respond(embed=self.page, view=self)

	# ================================================================= #

	@discord.ui.button(emoji="◀️")
	async def backward(self, btn, interaction):
		self.page_index -= 1
		if self.page_index < 0:
			self.page_index = self.max_pages
		self.page = self.page_generator(self.page_index)

		await interaction.message.edit(embed=self.page)
		await interaction.response.defer()

	@discord.ui.button(emoji="⏹️")
	async def close(self, btn, interaction):
		await interaction.message.delete()
		await interaction.response.defer()

	@discord.ui.button(emoji="▶️")
	async def forward(self, btn, interaction):
		self.page_index += 1
		if self.page_index > self.max_pages:
			self.page_index = 0
		self.page = self.page_generator(self.page_index)

		await interaction.message.edit(embed=self.page)
		await interaction.response.defer()
