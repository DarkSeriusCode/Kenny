import re
import json
import discord
import xml.etree.ElementTree as et
from discord import Embed
from typing import Dict, Union
from .XEMB_elements import *


# ------------------------------------------------------------------------------


class XEMBException(Exception):
	def __init__(self, text: str):
		self.text = text
		super().__init__(self.text)


def xemb_err(elem_name: str, text: str):
    print(f"[\033[35mXEMB\033[0m] {text} (in \033[33m\"{elem_name}\"\033[0m)")


# ------------------------------------------------------------------------------


class XEmbed(Embed):
    aviable_tags: Dict[str, AbstractEmbedElement] = {
            "author": Author,
            "title": Title,
            "description": Description,
            "footer": Footer,
            "image": Image,
            "thumbnail": Thumbnail,
            "field": Field
    }

    def __init__(self, tag: et.Element=None):
        super().__init__(title="Не указано!", description="Не указано!")
        if not tag: return 
        self.name = tag.get("name")
        colour_str = tag.get("colour")

        if colour_str != None:
            self.colour = self.convert_color(colour_str)

        # Перебор тегов
        for tag in tag.iter():
            if tag.tag not in self.aviable_tags: continue
            tag_class = self.aviable_tags[tag.tag]
            tag_class_instance = tag_class(tag)
            tag_class_instance.add_to_embed(self)

    def convert_color(self, content: str) -> discord.Colour:
        """Преобразует строку с цветом в discord.Colour. Если content это RGB, 
        то используется этот код, иначе цвет из стан. набора Discord"""
        if content in discord.Colour(0).__dir__():
            colour = discord.Colour(0).__getattribute__(content)()
        else:
            try:
                rbg = list(map(int, content.split()))
            except ValueError:
                xemb_err(self.name, f"Цвета \"{content}\" не существует!")
                colour = Embed.Empty
            else:
                colour = discord.Colour.from_rgb(*rbg)
        return colour
        

class XEMBParser:
    """Парсер для xml элементов и работе с Embed"""
    var_regexp = re.compile(r"\$\((.+)\)")


    def __init__(self, xemb_input, config: str="json/XEMB.json"):
        if isinstance(xemb_input, str):
            self.xml = et.ElementTree(file=xemb_input).getroot()
        else:
            self.xml = xemb_input.tag

        self.config = json.load(open(config))

        if self.xml.tag != "xembs": 
            raise XEMBException("Не найден тег xembs!")
        self.embeds: Dict[str, Embed] = {}

        # Общее кол-во XEMB сообщений
        self.embeds_count = len([x for x in self.xml.findall("embed")])

    def __len__(self):
        return self.embeds_count

    # ================================================================= #

    def get_by_name(self, name: str) -> XEmbed:
        return self.embeds[name]

    def get_by_index(self, ind: int) -> XEmbed:
        return tuple(self.embeds.values())[ind]

    # ================================================================= #

    def preprocessXEmbTagColor(self, tag: et.Element):
        """Препроцессинг цвета тега embed."""
        if (colour := tag.get("colour")):
            var = self.var_regexp.search(colour)
            if not var: return
            color_name = var.group()[2:-1]
            try:
                var_color = self.config["colors"][color_name]
            except KeyError:
                xemb_err(tag.get("name"), f"Цвет {color_name} не найден!")
                var_color = Embed.Empty
            tag.set("colour", var_color)

    # ================================================================= #

    def parse_all(self) -> Dict[str, Embed]:
        """Парсит все XEMB сообщения из xml файла"""
        for element in self.xml.findall("embed"):
            embed_name = element.get("name")
            if not embed_name: raise XEMBException("Не найден тег name!")
            self.preprocessXEmbTagColor(element)
            self.embeds[embed_name] = XEmbed(element)
        return self.embeds

    def parse_by_name(self, name: str) -> XEmbed:
        """Парсит XEMB cообщение по имени"""
        elem = self.xml.findall(f"embed[@name=\"{name}\"]")
        if not elem: raise XEMBException(f"Не найден XEMB по именем {name}")
        self.preprocessXEmbTagColor(elem)
        return XEmbed(elem[0])

    def parse_by_index(self, index: int) -> XEmbed:
        """Парсит XEMB по индексу"""
        elements = self.xml.findall("embed")
        self.preprocessXEmbTagColor(elements)
        if index <= len(elements): return XEmbed(elements[index])
        return XEmbed()