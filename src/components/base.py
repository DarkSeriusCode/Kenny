import discord.ui
from typing import Awaitable, List, Dict, Any

class Button(discord.ui.Button):
    """Представляет простую кнопку в Discord Ui"""
    
    def __init__(self, callback: Awaitable=None, **kwargs):
        super().__init__(**kwargs)
        self.__callback = callback

    async def callback(self, interaction):
        if self.__callback:
            await self.__callback(interaction)
        await interaction.response.defer()

class Select(discord.ui.Select):
    """Представляет список выбора"""
    
    def __init__(self, options: List[Dict[str, Any]], callback=None, **kwargs):
        super().__init__(**kwargs)
        self.__callback = callback
        for option in options:
            self.add_option(**option)

    async def callback(self, interaction):
        if self.__callback:
            await self.__callback(interaction)
        await interaction.response.defer()
