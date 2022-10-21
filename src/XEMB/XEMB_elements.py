import xml.etree.ElementTree as et
from discord import Embed
from abc import ABCMeta, abstractmethod

class AbstractEmbedElement(metaclass=ABCMeta):
    """Абстрактный класс для элементов Embed сообщений"""
    @abstractmethod
    def __init__(self, *argv, **kwargs):
    	...
    	
    @abstractmethod
    def add_to_embed(self, emb: Embed):
        """Метод добавляет элемент к Embed сообщению"""
        ...

class Author(AbstractEmbedElement):
    def __init__(self, tag: et.Element):
        self.name = tag.text
        self.url = tag.get("link") or Embed.Empty
        self.icon_url = tag.get("url") or Embed.Empty

    def add_to_embed(self, emb: Embed):
        emb.set_author(name=self.name, url=self.url, icon_url=self.icon_url)

class Title(AbstractEmbedElement):
    def __init__(self, tag: et.Element):
        self.title = tag.text

    def add_to_embed(self, emb: Embed):
        emb.title = self.title

class Description(AbstractEmbedElement):
    def __init__(self, tag: et.Element):
        self.description = tag.text

    def add_to_embed(self, emb: Embed):
        emb.description = self.description

class Footer(AbstractEmbedElement):
    def __init__(self, tag: et.Element):
        self.footer = tag.text
        self.icon_url = tag.get("url") or Embed.Empty

    def add_to_embed(self, emb: Embed):
        emb.set_footer(text=self.footer, icon_url=self.icon_url)

class Image(AbstractEmbedElement):
    def __init__(self, tag: et.Element):
        self.img_url = tag.get("url") or Embed.Empty

    def add_to_embed(self, emb: Embed):
        emb.set_image(url=self.img_url)

class Thumbnail(AbstractEmbedElement):
    def __init__(self, tag: et.Element):
        self.url = tag.get("url") or Embed.Empty

    def add_to_embed(self, emb: Embed):
        emb.set_thumbnail(url=self.url)

class Field(AbstractEmbedElement):
    def __init__(self, tag: et.Element):
        self.title = tag.get("title") or " "
        self.inline = True if tag.get("inline") else False
        self.text = tag.text

    def add_to_embed(self, emb: Embed):
        emb.add_field(name=self.title, value=self.text, inline=self.inline)