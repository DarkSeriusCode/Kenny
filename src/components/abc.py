import discord.ui
from discord import ApplicationContext
from abc import ABC, abstractmethod

class AbstractComponent(discord.ui.View, ABC):
    """Интерфейс любого компонента"""
    def __init__(self):
        discord.ui.View.__init__(self, timeout=None)

    @abstractmethod
    async def send(self, to: ApplicationContext):
        """Метод отправки компонента в канал"""
        pass
