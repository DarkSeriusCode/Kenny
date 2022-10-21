import discord
import discord.utils
from discord.ext import commands, tasks

class Greetings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def get_start_role(self):
		guild = discord.utils.get(self.bot.guilds, id=634453910236561419)
		return discord.utils.get(guild.roles, id=702835482840531014)

	@commands.Cog.listener()
	async def on_ready(self):
		self.give_role.start()

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		await member.add_roles(self.get_start_role())

	@tasks.loop(seconds=60)
	async def give_role(self):
		guild = discord.utils.get(self.bot.guilds, id=634453910236561419)
		for member in guild.members:
			await member.add_roles(self.get_start_role())

def setup(bot):
	bot.add_cog(Greetings(bot))