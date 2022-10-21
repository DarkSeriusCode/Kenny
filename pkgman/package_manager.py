import os
import sys
import json
import discord
import logging
from discord.ext.commands import Bot, Cog
from discord.commands import SlashCommand
from typing import List, Union
from functools import reduce
from itertools import chain
from src.XEMB.XEMB_parser import XEMBParser, XEMBException

# ------------------------------------------------------------------------------


def ok(text: str) -> str:
    return f"[\033[32mOk\033[0m] {text}"


def fail(text: str) -> str:
    return f"[\033[31mFail\033[0m]: {text}"


# ------------------------------------------------------------------------------


class PackageError(Exception):
    def __init__(self, pkg, text: str):
        self.text = fail(f"{text} [{pkg.path}]")
        super().__init__(self.text)


# ------------------------------------------------------------------------------


class Package:
    """
    Класс представляющий собой пакет. Он читает config.json и
    формирует информацию о пакете.
    """

    def __init__(self, pkg_dir: str):
        self.path = os.path.normpath(pkg_dir)
        try:
            config = json.load(open(f"{pkg_dir}/config.json"))
        except:
            raise PackageError(self, "Не удалось прочитать config.json!")

        self.name = config.get("name") or "Название не указано!"
        self.descr = config.get("description") or "Описание не указано!"
        self.version = config.get("version") or "Версия не указана!"
        self.author = config.get("author") or "Автор не указан!"
        self.docsp = config.get("docs") or None
        self.run_file = config.get("run_file") or None
        self.blocked = config.get("blocked") or False

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.WARNING)
        fh = logging.FileHandler(f"log/{self.name}.log")
        fmt = logging.Formatter("%(levelname)s (%(asctime)s): %(message)s \
[at %(lineno)d line in %(filename)s]")
        fh.setFormatter(fmt)
        self.logger.addHandler(fh)

        self.docs = self.docsp and os.path.exists(f"{pkg_dir}/{self.docsp}")

        # Читаем файл документации, если тот указан
        if self.docs:
            try:
                self.docs_parser = XEMBParser(f"{pkg_dir}/{self.docsp}")
            except Exception as exc:
                print(fail(f"Ошибка чтения документации пакета {self.name}"))
                self.logger.error(f"{exc.__class__.__name__}: {str(exc)}")
                self.docs = False

        if self.run_file:
            self.run_file = f"{self.path}/{self.run_file}"
        # Если не указан run_file, то по умолчанию это название каталога
        if self.run_file == None:
            self.run_file = "{}/{}.py".format(self.path,
                                              self.path.split("/")[-1])

        # Проверка на существование файла пакета
        if not os.path.exists(self.run_file):
            raise PackageError(self, f"Файл {self.run_file} не найден!")

        # Формируем путь до self.run_file, пригодный для использования Bot()
        fname = os.path.basename(self.run_file).split(".")[0]
        self.formatted_run_file = "{}.{}".format(self.path.replace("/", "."),
                                                 fname)

    def __str__(self):
        return "**Имя**: {}\n**Описание**: {}\n\
**Версия**: {}\n**Автор**: {}\n**Документация**: {}".format(
            self.name, self.descr, self.version, self.author,
            "**[**:green_circle:**]**" if self.docs else "**[**:red_circle:**]**")

    def __hash__(self) -> int:
        return int(reduce(lambda x, y: x + y, (str(ord(x)) for x in self.path)))

    def __eq__(self, other) -> bool:
        return self.path == other.path
        

# ------------------------------------------------------------------------------


class PackageManager:
    """
    Класс для управления пакетами. Использует файл к конфигами пакетов для
    управления ими. Всего существует только один экземпляр этого класса на всё
    приложение.
    """
    THIS_INSTANCE = None


    def __init__(self, bot: Bot, config_path: str="json/package_config.json"):
        if PackageManager.THIS_INSTANCE != None:
            self.__dict__ = PackageManager.THIS_INSTANCE.__dict__
            return

        print(f"\033[33mЗапуск пакетного менеджера [{config_path}] \033[0m\n")

        self.bot = bot
        self.config_path = config_path

        if not os.path.exists(config_path):
            print(fail(f"Файл {config_path} не найден"))
            sys.exit(1)
        self.config = json.load(open(config_path, encoding="utf-8"))

        # Обновление и получение пакетов
        print("\033[4mОбновление списка пакетов...\033[0m")
        self.all_packages = self.update_package_list()
        self.unblocked_pckgs = [p for p in self.all_packages if not p.blocked]

        # Содержит информацию о состоянии пакетов
        self.statuses = {n: False for n in self.all_packages}

        print("-" * 45)
        PackageManager.THIS_INSTANCE = self

    # ================================================================= #

    def update_package_list(self) -> List[Package]:
        """Обновляет список пакетов в package_config.json и возвращает список
        доступных пакетов"""

        # Поиск пакетов
        found_pkgs = self.find_packages(self.config["find-dirs"])
        # Запись в файл
        self.config["packages"] = list(map(lambda x: x.path, found_pkgs))
        file = open(self.config_path, "w", encoding="utf-8")
        json.dump(self.config, file, indent=4)

        return found_pkgs

    def find_packages(self, search_dirs: List[str]) -> List[Package]:
        """Ищет пакеты в директории. Пакетом 
        считается папка, содержащая файл config.json"""
        pkgs = []
        for entry in chain.from_iterable(os.walk(sdir) for sdir in search_dirs):
            if "config.json" in entry[2]:
                try:
                    pkg = Package(entry[0])
                except PackageError as PE:
                    print(PE.text)
                else:
                    print(ok(f"Найден пакет \033[33m{pkg.name}\033[0m."))
                    pkgs.append(pkg)
        return pkgs

    # ================================================================= #

    def get_package(self, name: str) -> Union[Package, None]:
        """Возвращает пакет по имени или None"""
        for pkg in self.all_packages:
            if pkg.name == name: return pkg
        return None

    # ================================================================= #

    def load_package(self, package: Package):
        """Подключает package к боту"""
        if self.statuses[package] or package.blocked:
            return  # Если пакет уже подключён или заблокирован

        try:
            self.bot.load_extension(package.formatted_run_file)
        except Exception as exc:
            print(fail(f"Файл пакета {package.name} возбудил исключение!"))
            package.logger.critical(f"{exc.__class__.__name__}: {str(exc)}")
            self.unload_package(package)
        else:
            self.statuses[package] = True
            print(ok(f"Пакет {package.name} \033[32mподключён\033[0m!"))

    def unload_package(self, package: Package):
        """Отключает пакет от бота"""
        if not self.statuses[package]:
            return  # Если пакет уже отключён

        self.bot.unload_extension(package.formatted_run_file)
        self.statuses[package] = False
        print(ok(f"Пакет {package.name} \033[31mотключён!\033[0m"))

    def load_all(self):
        """Подключает все пакеты к боту"""
        for pkg in self.unblocked_pckgs:
            self.load_package(pkg)

    def unload_all(self):
        """Отключает все пакеты от бота"""
        for pkg in self.unblocked_pckgs:
            self.unload_package(pkg)
