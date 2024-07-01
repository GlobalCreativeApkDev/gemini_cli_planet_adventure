"""
This file contains code for the game "Gemini CLI Planet Adventure".
Author: GlobalCreativeApkDev
"""


# Game version: 1


# Importing necessary libraries


import sys
import time
import uuid
import pickle
import copy
import google.generativeai as gemini
import random
from datetime import datetime
import os
from dotenv import load_dotenv
from functools import reduce

from mpmath import mp, mpf
from tabulate import tabulate

mp.pretty = True


# Creating static variables to be used throughout the game.


LETTERS: str = "abcdefghijklmnopqrstuvwxyz"
ELEMENT_CHART: list = [
    ["ATTACKING\nELEMENT", "TERRA", "FLAME", "SEA", "NATURE", "ELECTRIC", "ICE", "METAL", "DARK", "LIGHT", "WAR",
     "PURE",
     "LEGEND", "PRIMAL", "WIND"],
    ["DOUBLE\nDAMAGE", "ELECTRIC\nDARK", "NATURE\nICE", "FLAME\nWAR", "SEA\nLIGHT", "SEA\nMETAL", "NATURE\nWAR",
     "TERRA\nICE", "METAL\nLIGHT", "ELECTRIC\nDARK", "TERRA\nFLAME", "LEGEND", "PRIMAL", "PURE", "WIND"],
    ["HALF\nDAMAGE", "METAL\nWAR", "SEA\nWAR", "NATURE\nELECTRIC", "FLAME\nICE", "TERRA\nLIGHT", "FLAME\nMETAL",
     "ELECTRIC\nDARK", "TERRA", "NATURE", "SEA\nICE", "PRIMAL", "PURE", "LEGEND", "N/A"],
    ["NORMAL\nDAMAGE", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER", "OTHER",
     "OTHER",
     "OTHER", "OTHER", "OTHER"]
]


# Creating static functions to be used in this game.


def is_number(string: str) -> bool:
    try:
        mpf(string)
        return True
    except ValueError:
        return False


def list_to_string(a_list: list) -> str:
    res: str = "["  # initial value
    for i in range(len(a_list)):
        if i == len(a_list) - 1:
            res += str(a_list[i])
        else:
            res += str(a_list[i]) + ", "

    return res + "]"


def tabulate_element_chart() -> str:
    return str(tabulate(ELEMENT_CHART, headers='firstrow', tablefmt='fancy_grid'))


def generate_random_name() -> str:
    res: str = ""  # initial value
    name_length: int = random.randint(3, 25)
    for i in range(name_length):
        res += LETTERS[random.randint(0, len(LETTERS) - 1)]

    return res.capitalize()


def generate_random_legendary_creature(element):
    # type: (str) -> LegendaryCreature
    name: str = generate_random_name()
    max_hp: mpf = mpf(random.randint(45000, 55000))
    max_magic_points: mpf = mpf(random.randint(45000, 55000))
    attack_power: mpf = mpf(random.randint(8500, 9500))
    defense: mpf = mpf(random.randint(8500, 9500))
    attack_speed: mpf = mpf(random.randint(100, 125))
    skills: list = []  # initial value
    num_attack_skills: int = 0  # initial value
    num_heal_skills: int = 0  # initial value
    for i in range(4):
        if random.random() < 0.5:
            # Generating attack skill
            num_attack_skills += 1
            new_skill: Skill = Skill("ATTACK SKILL #" + str(num_attack_skills), "An attack skill.",
                                     "ATTACK", num_attack_skills * mpf("0.01") * random.randint(350, 450),
                                     mpf("0"), mpf("10") ** (num_attack_skills * random.randint(2, 4)))
            skills.append(new_skill)
        else:
            # Generating heal skill
            num_heal_skills += 1
            new_skill: Skill = Skill("HEAL SKILL #" + str(num_heal_skills), "A heal skill", "HEAL",
                                     mpf("0"), mpf("10") ** (num_attack_skills * random.randint(1, 3)),
                                     mpf("10") ** (num_attack_skills * random.randint(2, 4)))
            skills.append(new_skill)

    awaken_bonus: AwakenBonus = AwakenBonus(mpf(random.randint(115, 135)), mpf(random.randint(115, 135)),
                                            mpf(random.randint(115, 135)), mpf(random.randint(115, 135)),
                                            mpf(random.randint(0, 15)),
                                            mpf(0.01 * random.randint(0, 15)), mpf(0.01 * random.randint(0, 15)))
    new_legendary_creature: LegendaryCreature = LegendaryCreature(name, element, max_hp, max_magic_points,
                                                                  attack_power, defense, attack_speed, skills,
                                                                  awaken_bonus)
    return new_legendary_creature


def triangular(n: int) -> int:
    return int(n * (n - 1) / 2)


def mpf_sum_of_list(a_list: list) -> mpf:
    return mpf(str(sum(mpf(str(elem)) for elem in a_list if is_number(str(elem)))))


def mpf_product_of_list(a_list: list) -> mpf:
    return mpf(reduce(lambda x, y: mpf(x) * mpf(y) if is_number(x) and
                                                      is_number(y) else mpf(x) if is_number(x) and not is_number(
        y) else mpf(y) if is_number(y) and not is_number(x) else 1, a_list, 1))


def get_elemental_damage_multiplier(element1: str, element2: str) -> mpf:
    if element1 == "TERRA":
        return mpf("2") if element2 in ["ELECTRIC, DARK"] else mpf("0.5") if element2 in ["METAL", "WAR"] else mpf("1")
    elif element1 == "FLAME":
        return mpf("2") if element2 in ["NATURE", "ICE"] else mpf("0.5") if element2 in ["SEA", "WAR"] else mpf("1")
    elif element1 == "SEA":
        return mpf("2") if element2 in ["FLAME", "WAR"] else mpf("0.5") if element2 in ["NATURE", "ELECTRIC"] else \
            mpf("1")
    elif element1 == "NATURE":
        return mpf("2") if element2 in ["SEA", "LIGHT"] else mpf("0.5") if element2 in ["FLAME", "ICE"] else mpf("1")
    elif element1 == "ELECTRIC":
        return mpf("2") if element2 in ["SEA", "METAL"] else mpf("0.5") if element2 in ["TERRA", "LIGHT"] else mpf("1")
    elif element1 == "ICE":
        return mpf("2") if element2 in ["NATURE", "WAR"] else mpf("0.5") if element2 in ["FLAME", "METAL"] else mpf("1")
    elif element1 == "METAL":
        return mpf("2") if element2 in ["TERRA", "ICE"] else mpf("0.5") if element2 in ["ELECTRIC", "DARK"] else \
            mpf("1")
    elif element1 == "DARK":
        return mpf("2") if element2 in ["METAL", "LIGHT"] else mpf("0.5") if element2 == "TERRA" else mpf("1")
    elif element1 == "LIGHT":
        return mpf("2") if element2 in ["ELECTRIC", "DARK"] else mpf("0.5") if element2 == "NATURE" else mpf("1")
    elif element1 == "WAR":
        return mpf("2") if element2 in ["TERRA", "FLAME"] else mpf("0.5") if element2 in ["SEA", "ICE"] else mpf("1")
    elif element1 == "PURE":
        return mpf("2") if element2 == "LEGEND" else mpf("0.5") if element2 == "PRIMAL" else mpf("1")
    elif element1 == "LEGEND":
        return mpf("2") if element2 == "PRIMAL" else mpf("0.5") if element2 == "PURE" else mpf("1")
    elif element1 == "PRIMAL":
        return mpf("2") if element2 == "PURE" else mpf("0.5") if element2 == "LEGEND" else mpf("1")
    elif element1 == "WIND":
        return mpf("2") if element2 == "WIND" else mpf("1")
    else:
        return mpf("1")


def load_game_data(file_name):
    # type: (str) -> SavedGameData
    return pickle.load(open(file_name, "rb"))


def save_game_data(game_data, file_name):
    # type: (SavedGameData, str) -> None
    pickle.dump(game_data, open(file_name, "wb"))


def clear():
    # type: () -> None
    if sys.platform.startswith('win'):
        os.system('cls')  # For Windows System
    else:
        os.system('clear')  # For Linux System


# Creating necessary classes.


# TODO: implement more classes and __str__ method in the classes


###########################################
# ADVENTURE MODE
###########################################


class Action:
    """
    This class contains attributes of an action which can be carried out during battles.
    """

    POSSIBLE_NAMES: list = ["NORMAL ATTACK", "NORMAL HEAL", "USE SKILL"]

    def __init__(self, name):
        # type: (str) -> None
        self.name: str = name if name in self.POSSIBLE_NAMES else self.POSSIBLE_NAMES[0]

    def execute(self, user, target, skill_to_use=None):
        # type: (LegendaryCreature, LegendaryCreature, Skill or None) -> bool
        if self.name == "NORMAL ATTACK":
            if user == target:
                return False

            is_crit: bool = random.random() < user.crit_rate
            crit_factor: mpf = user.crit_damage if is_crit else mpf("1")
            raw_damage: mpf = user.attack_power * crit_factor - target.defense
            damage_multiplier_by_element: mpf = get_elemental_damage_multiplier(user.element, target.element)
            raw_damage *= damage_multiplier_by_element
            damage: mpf = raw_damage if raw_damage > mpf("0") else mpf("0")
            target.curr_hp -= damage
            print(str(user.name) + " dealt " + str(damage) + " damage on " + str(target.name) + "!")
            return True

        elif self.name == "NORMAL HEAL":
            if user != target:
                return False

            heal_amount: mpf = 0.05 * user.max_hp
            user.curr_hp += heal_amount
            if user.curr_hp >= user.max_hp:
                user.curr_hp = user.max_hp

            return True

        elif self.name == "USE SKILL":
            if isinstance(skill_to_use, Skill):
                if skill_to_use.skill_type == "HEAL":
                    user.curr_hp += skill_to_use.heal_amount
                    if user.curr_hp >= user.max_hp:
                        user.curr_hp = user.max_hp
                elif skill_to_use.skill_type == "ATTACK":
                    is_crit: bool = random.random() < user.crit_rate
                    crit_factor: mpf = user.crit_damage if is_crit else mpf("1")
                    raw_damage: mpf = user.attack_power * skill_to_use.damage_multiplier * crit_factor - target.defense
                    damage_multiplier_by_element: mpf = get_elemental_damage_multiplier(user.element, target.element)
                    raw_damage *= damage_multiplier_by_element
                    damage: mpf = raw_damage if raw_damage > mpf("0") else mpf("0")
                    target.curr_hp -= damage
                    print(str(user.name) + " dealt " + str(damage) + " damage on " + str(target.name) + "!")
                return True
            return False
        return False

    def clone(self):
        # type: () -> Action
        return copy.deepcopy(self)


class AwakenBonus:
    """
    This class contains attributes of the bonus gained for awakening a legendary creature.
    """

    def __init__(self, max_hp_percentage_up, max_magic_points_percentage_up, attack_power_percentage_up,
                 defense_percentage_up, attack_speed_up, crit_rate_up, crit_damage_up):
        # type: (mpf, mpf, mpf, mpf, mpf, mpf, mpf) -> None
        self.max_hp_percentage_up: mpf = max_hp_percentage_up
        self.max_magic_points_percentage_up: mpf = max_magic_points_percentage_up
        self.attack_power_percentage_up: mpf = attack_power_percentage_up
        self.defense_percentage_up: mpf = defense_percentage_up
        self.attack_speed_up: mpf = attack_speed_up
        self.crit_rate_up: mpf = crit_rate_up
        self.crit_damage_up: mpf = crit_damage_up

    def clone(self):
        # type: () -> AwakenBonus
        return copy.deepcopy(self)


class Battle:
    """
    This class contains attributes of a battle in this game.
    """

    def __init__(self, player1):
        # type: (Player) -> None
        self.player1: Player = player1
        self.reward: Reward = Reward()

    def clone(self):
        # type: () -> Battle
        return copy.deepcopy(self)


class PVPBattle(Battle):
    """
    This class contains attributes of a battle between players.
    """

    def __init__(self, player1, player2):
        # type: (Player, Player) -> None
        Battle.__init__(self, player1)
        self.whose_turn: Player or None = None
        self.winner: Player or None = None
        self.player2: Player = player2

    def get_someone_to_move(self):
        # type: () -> None
        """
        Getting a legendary creature to move and have its turn.
        :return: None
        """

        # Finding out which legendary creature moves
        full_attack_gauge_list: list = []  # initial value
        while len(full_attack_gauge_list) == 0:
            if self.player1.attack_gauge >= Player.FULL_ATTACK_GAUGE and self.player1 not \
                        in full_attack_gauge_list:
                full_attack_gauge_list.append(self.player1)

            if self.player2.attack_gauge >= Player.FULL_ATTACK_GAUGE and self.player2 not \
                        in full_attack_gauge_list:
                full_attack_gauge_list.append(self.player2)

            self.tick()

        max_attack_gauge: mpf = max(player.attack_gauge for player in full_attack_gauge_list)
        for player in full_attack_gauge_list:
            if player.attack_gauge == max_attack_gauge:
                self.whose_turn = player

    def tick(self):
        # type: () -> None
        """
        The clock ticks when battles are carried out.
        :return: None
        """

        self.player1.attack_gauge += self.player1.speed * 0.07
        self.player2.attack_gauge += self.player2.speed * 0.07


class WildBattle(Battle):
    """
    This class contains attributes of a battle against a wild legendary creature.
    """

    def __init__(self, player1, wild_legendary_creature):
        # type: (Player, LegendaryCreature) -> None
        Battle.__init__(self, player1)
        self.wild_legendary_creature: LegendaryCreature = wild_legendary_creature
        self.whose_turn: LegendaryCreature or None = None
        self.winner: BattleTeam or None = None
        self.reward = Reward(mpf("10") ** (5 * self.wild_legendary_creature.level),
                             mpf("10") ** (5 * self.wild_legendary_creature.level - 2),
                             mpf("10") ** (5 * self.wild_legendary_creature.level))
        self.wild_legendary_creature_caught: bool = False
        self.player_fled: bool = False

    def get_someone_to_move(self):
        # type: () -> None
        """
        Getting a legendary creature to move and have its turn.
        :return: None
        """

        # Finding out which legendary creature moves
        full_attack_gauge_list: list = []  # initial value
        while len(full_attack_gauge_list) == 0:
            for legendary_creature in self.player1.battle_team.get_legendary_creatures():
                if legendary_creature.attack_gauge >= legendary_creature.FULL_ATTACK_GAUGE and legendary_creature not \
                        in full_attack_gauge_list:
                    full_attack_gauge_list.append(legendary_creature)

            if (self.wild_legendary_creature.attack_gauge >= self.wild_legendary_creature.FULL_ATTACK_GAUGE and
                    self.wild_legendary_creature not in full_attack_gauge_list):
                full_attack_gauge_list.append(self.wild_legendary_creature)

            self.tick()

        max_attack_gauge: mpf = max(legendary_creature.attack_gauge for legendary_creature in full_attack_gauge_list)
        for legendary_creature in full_attack_gauge_list:
            if legendary_creature.attack_gauge == max_attack_gauge:
                self.whose_turn = legendary_creature

    def tick(self):
        # type: () -> None
        """
        The clock ticks when battles are carried out.
        :return: None
        """

        for legendary_creature in self.player1.battle_team.get_legendary_creatures():
            legendary_creature.attack_gauge += legendary_creature.attack_speed * 0.07

        self.wild_legendary_creature.attack_gauge += self.wild_legendary_creature.attack_speed * 0.07


class CreatureBattle(Battle):
    """
    This class contains attributes of a battle between teams of legendary creatures.
    """

    def __init__(self, player1, player2):
        # type: (Player, Player) -> None
        Battle.__init__(self, player1)
        self.player2: Player = player2
        self.whose_turn: LegendaryCreature or None = None
        self.winner: BattleTeam or None = None
        self.reward = Reward(mpf("10") ** sum(5 * legendary_creature.level for legendary_creature in
                                              self.player2.battle_team.get_legendary_creatures()),
                             mpf("10") ** sum(5 * legendary_creature.level - 2 for legendary_creature in
                                              self.player2.battle_team.get_legendary_creatures()),
                             mpf("10") ** sum(5 * legendary_creature.level for legendary_creature in
                                              self.player2.battle_team.get_legendary_creatures()))

    def get_someone_to_move(self):
        # type: () -> None
        """
        Getting a legendary creature to move and have its turn.
        :return: None
        """

        # Finding out which legendary creature moves
        full_attack_gauge_list: list = []  # initial value
        while len(full_attack_gauge_list) == 0:
            for legendary_creature in self.player1.battle_team.get_legendary_creatures():
                if legendary_creature.attack_gauge >= legendary_creature.FULL_ATTACK_GAUGE and legendary_creature not \
                        in full_attack_gauge_list:
                    full_attack_gauge_list.append(legendary_creature)

            for legendary_creature in self.player2.battle_team.get_legendary_creatures():
                if legendary_creature.attack_gauge >= legendary_creature.FULL_ATTACK_GAUGE and legendary_creature not \
                        in full_attack_gauge_list:
                    full_attack_gauge_list.append(legendary_creature)

            self.tick()

        max_attack_gauge: mpf = max(legendary_creature.attack_gauge for legendary_creature in full_attack_gauge_list)
        for legendary_creature in full_attack_gauge_list:
            if legendary_creature.attack_gauge == max_attack_gauge:
                self.whose_turn = legendary_creature

    def tick(self):
        # type: () -> None
        """
        The clock ticks when battles are carried out.
        :return: None
        """

        for legendary_creature in self.player1.battle_team.get_legendary_creatures():
            legendary_creature.attack_gauge += legendary_creature.attack_speed * 0.07

        for legendary_creature in self.player2.battle_team.get_legendary_creatures():
            legendary_creature.attack_gauge += legendary_creature.attack_speed * 0.07


class City:
    """
    This class contains attributes of a city in this game.
    """

    def __init__(self, name, tiles):
        # type: (str, list) -> None
        self.name: str = name
        self.__tiles: list = tiles

    def get_tile_at(self, x, y):
        # type: (int, int) -> CityTile or None
        if x < 0 or x >= len(self.__tiles[0]) or y < 0 or y >= len(self.__tiles):
            return None
        return self.__tiles[y][x]

    def get_tiles(self):
        # type: () -> list
        return self.__tiles

    def __str__(self):
        # type: () -> str
        res: str = str(self.name)
        all_tiles: list = []  # initial value
        for y in range(len(self.__tiles)):
            curr_tiles: list = []  # initial value
            for x in range(len(self.__tiles[y])):
                curr_tile: CityTile = self.get_tile_at(x, y)
                curr_tiles.append(str(curr_tile))

            all_tiles.append(curr_tiles)
        return res + "\n" + str(tabulate(all_tiles, headers='firstrow', tablefmt='fancy_grid'))

    def clone(self):
        # type: () -> City
        return copy.deepcopy(self)


class CityTile:
    """
    This class contains attributes of a tile in a city.
    """

    def __init__(self):
        # type: () -> None
        self.__game_characters: list = []  # initial value
        self.is_portal: bool = False

    def get_game_characters(self):
        # type: () -> list
        return self.__game_characters

    def add_game_character(self, game_character):
        # type: (GameCharacter) -> None
        self.__game_characters.append(game_character)

    def remove_game_character(self, game_character):
        # type: (GameCharacter) -> bool
        if game_character in self.__game_characters:
            self.__game_characters.remove(game_character)
            return True
        return False

    def __str__(self):
        # type: () -> str
        return "(" + str(type(self).__name__) + ")\nAND\n" + list_to_string(
            [game_character.name for game_character in self.__game_characters])

    def clone(self):
        # type: () -> CityTile
        return copy.deepcopy(self)


class PortalTile(CityTile):
    """
    This class contains attributes of a portal from one city to another.
    """

    def __init__(self):
        # type: () -> None
        CityTile.__init__(self)
        self.is_portal = True


class DowntownTile(CityTile):
    """
    This class contains attributes of downtown area in a city.
    """

    def __init__(self):
        # type: () -> None
        CityTile.__init__(self)


class SuburbTile(CityTile):
    """
    This class contains attributes of suburb area in a city.
    """

    def __init__(self):
        # type: () -> None
        CityTile.__init__(self)


class ParkTile(CityTile):
    """
    This class contains attributes of park area in a city.
    """

    def __init__(self):
        # type: () -> None
        CityTile.__init__(self)


class BeachTile(CityTile):
    """
    This class contains attributes of beach area in a city.
    """

    def __init__(self):
        # type: () -> None
        CityTile.__init__(self)


###########################################
# ADVENTURE MODE
###########################################


###########################################
# INVENTORY
###########################################


class LegendaryCreatureInventory:
    """
    This class contains attributes of an inventory containing legendary creatures.
    """

    def __init__(self):
        # type: () -> None
        self.__legendary_creatures: list = []  # initial value

    def add_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> None
        self.__legendary_creatures.append(legendary_creature)

    def remove_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if legendary_creature in self.__legendary_creatures:
            self.__legendary_creatures.remove(legendary_creature)
            return True
        return False

    def get_legendary_creatures(self):
        # type: () -> list
        return self.__legendary_creatures

    def clone(self):
        # type: () -> LegendaryCreatureInventory
        return copy.deepcopy(self)


class ItemInventory:
    """
    This class contains attributes of an inventory containing items.
    """

    def __init__(self):
        # type: () -> None
        self.__items: list = []  # initial value

    def add_item(self, item):
        # type: (Item) -> None
        self.__items.append(item)

    def remove_item(self, item):
        # type: (Item) -> bool
        if item in self.__items:
            self.__items.remove(item)
            return True
        return False

    def get_items(self):
        # type: () -> list
        return self.__items

    def clone(self):
        # type: () -> ItemInventory
        return copy.deepcopy(self)


###########################################
# INVENTORY
###########################################


###########################################
# LEGENDARY CREATURE
###########################################


class BattleTeam:
    """
    This class contains attributes of a team brought to battles.
    """

    MAX_LEGENDARY_CREATURES: int = 5

    def __init__(self, legendary_creatures=None):
        # type: (list) -> None
        if legendary_creatures is None:
            legendary_creatures = []
        self.__legendary_creatures: list = legendary_creatures if len(legendary_creatures) <= \
                                                                  self.MAX_LEGENDARY_CREATURES else []

    def add_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if len(self.__legendary_creatures) < self.MAX_LEGENDARY_CREATURES:
            self.__legendary_creatures.append(legendary_creature)
            return True
        return False

    def remove_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if legendary_creature in self.__legendary_creatures:
            self.__legendary_creatures.remove(legendary_creature)
            return True
        return False

    def get_legendary_creatures(self):
        # type: () -> list
        return self.__legendary_creatures

    def recover_all(self):
        # type: () -> None
        for legendary_creature in self.__legendary_creatures:
            legendary_creature.restore()

    def all_died(self):
        # type: () -> bool
        for legendary_creature in self.__legendary_creatures:
            if legendary_creature.get_is_alive():
                return False
        return True

    def clone(self):
        # type: () -> BattleTeam
        return copy.deepcopy(self)


class LegendaryCreature:
    """
    This class contains attributes of a legendary creature in this game.
    """

    MIN_CRIT_RATE: mpf = mpf("0.15")
    MAX_CRIT_RATE: mpf = mpf("1")
    MIN_CRIT_DAMAGE: mpf = mpf("1.5")
    MIN_ATTACK_GAUGE: mpf = mpf("0")
    FULL_ATTACK_GAUGE: mpf = mpf("1")
    POTENTIAL_ELEMENTS: list = ["TERRA", "FLAME", "SEA", "NATURE", "ELECTRIC", "ICE", "METAL", "DARK", "LIGHT", "WAR",
                                "PURE", "LEGEND", "PRIMAL", "WIND", "BEAUTY", "MAGIC", "CHAOS", "HAPPY", "DREAM",
                                "SOUL"]

    def __init__(self, name, element, max_hp, max_magic_points, attack_power, defense, attack_speed, skills,
                 awaken_bonus):
        # type: (str, mpf, str, mpf, mpf, mpf, mpf, list, AwakenBonus) -> None
        self.name: str = name
        self.element: str = element if element in self.POTENTIAL_ELEMENTS else self.POTENTIAL_ELEMENTS[0]
        self.level: int = 1
        self.exp: mpf = mpf("0")
        self.required_exp: mpf = mpf("1e6")
        self.curr_hp: mpf = max_hp
        self.max_hp: mpf = max_hp
        self.curr_magic_points: mpf = max_magic_points
        self.max_magic_points: mpf = max_magic_points
        self.attack_power: mpf = attack_power
        self.defense: mpf = defense
        self.attack_speed: mpf = attack_speed
        self.__skills: list = skills
        self.awaken_bonus: AwakenBonus = awaken_bonus
        self.crit_rate: mpf = self.MIN_CRIT_RATE
        self.crit_damage: mpf = self.MIN_CRIT_DAMAGE
        self.__runes: dict = {}  # initial value
        self.attack_gauge: mpf = self.MIN_ATTACK_GAUGE
        self.has_awakened: bool = False
        self.corresponding_team: BattleTeam or None = None  # initial value

    def awaken(self):
        # type: () -> bool
        if not self.has_awakened:
            self.name = "AWAKENED " + str(self.name)
            self.max_hp *= 1 + self.awaken_bonus.max_hp_percentage_up / 100
            self.max_magic_points *= 1 + self.awaken_bonus.max_magic_points_percentage_up / 100
            self.attack_power *= 1 + self.awaken_bonus.attack_power_percentage_up / 100
            self.defense *= 1 + self.awaken_bonus.defense_percentage_up / 100
            self.attack_speed += self.awaken_bonus.attack_speed_up
            self.crit_rate += self.awaken_bonus.crit_rate_up
            if self.crit_rate > self.MAX_CRIT_RATE:
                self.crit_rate = self.MAX_CRIT_RATE

            self.crit_damage += self.awaken_bonus.crit_damage_up
            self.restore()
            self.has_awakened = True
            return True
        return False

    def restore(self):
        # type: () -> None
        self.curr_magic_points = self.max_magic_points
        self.curr_hp = self.max_hp

    def get_skills(self):
        # type: () -> list
        return self.__skills

    def get_runes(self):
        # type: () -> dict
        return self.__runes

    def get_is_alive(self):
        # type: () -> bool
        return self.curr_hp > 0

    def recover_magic_points(self):
        # type: () -> None
        self.curr_magic_points += self.max_magic_points / 12
        if self.curr_magic_points >= self.max_magic_points:
            self.curr_magic_points = self.max_magic_points

    def place_rune(self, rune):
        # type: (Rune) -> bool
        if rune.already_placed:
            return False

        if rune.slot_number in self.__runes.keys():
            self.remove_rune(rune.slot_number)

        self.__runes[rune.slot_number] = rune
        self.max_hp *= 1 + (rune.max_hp_percentage_up / 100)
        self.max_magic_points *= 1 + (rune.max_magic_points_percentage_up / 100)
        self.attack_power *= 1 + (rune.attack_power_percentage_up / 100)
        self.defense *= 1 + (rune.stat_increase.defense_percentage_up / 100)
        self.attack_speed += rune.attack_speed_up
        self.crit_rate += rune.crit_rate_up
        if self.crit_rate > self.MAX_CRIT_RATE:
            self.crit_rate = self.MAX_CRIT_RATE

        self.crit_damage += rune.crit_damage_up
        self.restore()
        rune.already_placed = True
        return True

    def level_up(self):
        # type: () -> None
        while self.exp >= self.required_exp:
            self.level += 1
            self.required_exp *= mpf("10") ** self.level
            temp_runes: dict = self.__runes
            for slot_number in self.__runes.keys():
                self.remove_rune(slot_number)

            self.attack_power *= triangular(self.level)
            self.max_hp *= triangular(self.level)
            self.max_magic_points *= triangular(self.level)
            self.defense *= triangular(self.level)
            self.attack_speed += 2
            for rune in temp_runes.values():
                self.place_rune(rune)

            self.restore()

    def level_up_rune(self, slot_number):
        # type: (int) -> bool
        if slot_number not in self.__runes.keys():
            return False

        current_rune: Rune = self.__runes[slot_number]
        self.remove_rune(slot_number)
        success: bool = current_rune.level_up()
        self.place_rune(current_rune)
        return success

    def remove_rune(self, slot_number):
        # type: (int) -> bool
        if slot_number in self.__runes.keys():
            # Remove the rune at slot number 'slot_number'
            current_rune: Rune = self.__runes[slot_number]
            self.max_hp /= 1 + (current_rune.max_hp_percentage_up / 100)
            self.max_magic_points /= 1 + (current_rune.max_magic_points_percentage_up / 100)
            self.attack_power /= 1 + (current_rune.attack_power_percentage_up / 100)
            self.defense /= 1 + (current_rune.defense_percentage_up / 100)
            self.attack_speed -= current_rune.attack_speed_up
            self.crit_rate -= current_rune.crit_rate_up
            if self.crit_rate <= self.MIN_CRIT_RATE:
                self.crit_rate = self.MIN_CRIT_RATE

            self.crit_damage -= current_rune.crit_damage_up
            if self.crit_damage <= self.MIN_CRIT_DAMAGE:
                self.crit_damage = self.MIN_CRIT_DAMAGE

            self.restore()
            self.__runes.pop(current_rune.slot_number)
            current_rune.already_placed = False
            return True
        return False

    def have_turn(self, other, skill, action_name):
        # type: (LegendaryCreature, Skill or None, str) -> bool
        self.attack_gauge = self.MIN_ATTACK_GAUGE
        if action_name == "NORMAL ATTACK":
            self.normal_attack(other)
        elif action_name == "NORMAL HEAL":
            self.normal_heal(other)
        elif action_name == "USE SKILL" and isinstance(skill, Skill):
            self.use_skill(other, skill)
        else:
            return False

        return True

    def normal_attack(self, other):
        # type: (LegendaryCreature) -> None
        action: Action = Action("NORMAL ATTACK")
        action.execute(self, other)

    def normal_heal(self, other):
        # type: (LegendaryCreature) -> None
        action: Action = Action("NORMAL HEAL")
        action.execute(self, other)

    def use_skill(self, other, active_skill):
        # type: (LegendaryCreature, Skill) -> bool
        if active_skill not in self.__skills:
            return False

        if self.curr_magic_points < active_skill.magic_points_cost:
            print("Not enough magic points!")
            return False

        action: Action = Action("USE SKILL")
        action.execute(self, other, active_skill)
        self.curr_magic_points -= active_skill.magic_points_cost
        return True

    def clone(self):
        # type: () -> LegendaryCreature
        return copy.deepcopy(self)


class Skill:
    """
    This class contains attributes of a skill legendary creatures have.
    """

    POSSIBLE_SKILL_TYPES: list = ["ATTACK", "HEAL"]

    def __init__(self, name, description, skill_type, damage_multiplier, heal_amount, magic_points_cost):
        # type: (str, str, str, mpf, mpf, mpf) -> None
        self.name: str = name
        self.level: int = 1
        self.description: str = description
        self.skill_type: str = skill_type if skill_type in self.POSSIBLE_SKILL_TYPES else self.POSSIBLE_SKILL_TYPES[0]
        self.damage_multiplier: mpf = damage_multiplier if self.skill_type == "ATTACK" else mpf("0")
        self.heal_amount: mpf = heal_amount if self.skill_type == "HEAL" else mpf("0")
        self.magic_points_cost: mpf = magic_points_cost

    def level_up(self):
        # type: () -> None
        self.damage_multiplier *= mpf("1.25") * self.level
        self.heal_amount *= mpf("1.25") * self.level
        self.level += 1

    def clone(self):
        # type: () -> Skill
        return copy.deepcopy(self)


###########################################
# LEGENDARY CREATURE
###########################################


###########################################
# ITEM
###########################################


class Item:
    """
    This class contains attributes of an item in this game.
    """

    def __init__(self, name, description, dollars_cost):
        # type: (str, str, mpf) -> None
        self.name: str = name
        self.description: str = description
        self.dollars_cost: mpf = dollars_cost
        self.sell_dollars_gain: mpf = dollars_cost / 5

    def clone(self):
        # type: () -> Item
        return copy.deepcopy(self)


class Ball(Item):
    """
    This class contains attributes of a ball used to catch a legendary creature.
    """

    MIN_CATCH_SUCCESS_RATE: mpf = mpf("0.15")
    MAX_CATCH_SUCCESS_RATE: mpf = mpf("1")

    def __init__(self, name, description, dollars_cost, catch_success_rate):
        # type: (str, str, mpf, mpf) -> None
        Item.__init__(self, name, description, dollars_cost)
        self.catch_success_rate: mpf = catch_success_rate if (self.MIN_CATCH_SUCCESS_RATE <= catch_success_rate <=
                                                        self.MAX_CATCH_SUCCESS_RATE) else self.MIN_CATCH_SUCCESS_RATE


class Rune(Item):
    """
    This class contains attributes of a rune used to strengthen legendary creatures.
    """

    MIN_SLOT_NUMBER: int = 1
    MAX_SLOT_NUMBER: int = 6
    MIN_RATING: int = 1
    MAX_RATING: int = 6
    MAX_CRIT_RATE_UP: mpf = mpf("0.85")

    def __init__(self, name, description, dollars_cost, rating, slot_number, max_magic_points_percentage_up,
                 max_hp_percentage_up, attack_power_percentage_up, defense_percentage_up, attack_speed_up,
                 crit_rate_up, crit_damage_up):
        # type: (str, str, mpf, int, int, mpf, mpf, mpf, mpf, mpf, mpf, mpf) -> None
        Item.__init__(self, name, description, dollars_cost)
        self.rating: int = rating if self.MIN_RATING <= rating <= self.MAX_RATING else self.MIN_RATING
        self.slot_number: int = slot_number if self.MIN_SLOT_NUMBER <= slot_number <= self.MAX_SLOT_NUMBER \
            else self.MIN_SLOT_NUMBER
        self.max_magic_points_percentage_up: mpf = max_magic_points_percentage_up
        self.max_hp_percentage_up: mpf = max_hp_percentage_up
        self.attack_power_percentage_up: mpf = attack_power_percentage_up
        self.defense_percentage_up: mpf = defense_percentage_up
        self.attack_speed_up: mpf = attack_speed_up
        self.crit_rate_up: mpf = crit_rate_up if mpf("0") <= crit_rate_up <= self.MAX_CRIT_RATE_UP else mpf("0")
        self.crit_damage_up: mpf = crit_damage_up
        self.level: int = 1
        self.level_up_dollars_cost: mpf = dollars_cost
        self.level_up_success_rate: mpf = mpf("1")
        self.already_placed: bool = False  # initial value

    def level_up(self):
        # type: () -> bool
        # Check whether levelling up is successful or not
        if random.random() > self.level_up_success_rate:
            return False

        # Increase the level of the rune
        self.level += 1

        # Update the cost and success rate of levelling up the rune
        self.level_up_dollars_cost *= mpf("10") ** (self.level + self.rating)
        self.level_up_success_rate *= mpf("0.95")

        # Increase stats
        self.stat_increase.max_hp_percentage_up += self.rating
        self.stat_increase.max_magic_points_percentage_up += self.rating
        self.stat_increase.attack_percentage_up += self.rating
        self.stat_increase.defense_percentage_up += self.rating
        self.stat_increase.attack_speed_up += 2 * self.rating
        self.stat_increase.crit_rate_up += 0.01 * self.rating
        self.stat_increase.crit_damage_up += 0.05 * self.rating
        self.stat_increase.resistance_up += 0.01 * self.rating
        self.stat_increase.accuracy_up += 0.01 * self.rating
        return True


class AwakenShard(Item):
    """
    This class contains attributes of an awaken shard to immediately awaken a legendary creature.
    """

    def __init__(self, name, description, dollars_cost, legendary_creature_element):
        # type: (str, str, mpf, str) -> None
        Item.__init__(self, name, description, dollars_cost)
        self.legendary_creature_element: str = legendary_creature_element


class EXPShard(Item):
    """
    This class contains attributes of an EXP shard to increase the EXP of a legendary creature.
    """

    def __init__(self, name, description, dollars_cost, exp_granted):
        # type: (str, str, mpf, mpf) -> None
        Item.__init__(self, name, description, dollars_cost)
        self.exp_granted: mpf = exp_granted


class LevelUpShard(Item):
    """
    This class contains attributes of a shard used to immediately level up a legendary creature.
    """

    def __init__(self, name, description, dollars_cost):
        # type: (str, str, mpf) -> None
        Item.__init__(self, name, description, dollars_cost)


class SkillLevelUpShard(Item):
    """
    This class contains attributes of a skill level up shard to immediately increase the level of a
    skill possessed by a legendary creature.
    """

    def __init__(self, name, description, dollars_cost):
        # type: (str, str, mpf) -> None
        Item.__init__(self, name, description, dollars_cost)



###########################################
# ITEM
###########################################


###########################################
# EXERCISE
###########################################


class ExerciseGym:
    """
    This class contains attributes of a gym where the player can improve his/her attributes.
    """

    def __init__(self, name, training_options):
        # type: (str, list) -> None
        self.name: str = name
        self.level: int = 1
        self.level_up_dollars_cost: mpf = mpf("1e6")
        self.__training_options = training_options

    def level_up(self):
        # type: () -> None
        self.level += 1
        self.level_up_dollars_cost *= mpf("10") ** self.level
        for training_option in self.__training_options:
            training_option.player_attack_power_gain *= mpf("1.15") * self.level
            training_option.player_defense_gain *= mpf("1.15") * self.level
            training_option.player_speed_gain *= mpf("1.15") * self.level
            training_option.player_dexterity_gain *= mpf("1.15") * self.level

    def get_training_options(self):
        # type: () -> list
        return self.__training_options

    def clone(self):
        # type: () -> ExerciseGym
        return copy.deepcopy(self)


class TrainingOption:
    """
    This class contains attributes of a training option for fitness.
    """

    def __init__(self, name, stamina_cost, player_attack_power_gain, player_defense_gain, player_speed_gain, player_dexterity_gain):
        # type: (str, mpf, mpf, mpf, mpf, mpf) -> None
        self.name: str = name
        self.stamina_cost: mpf = stamina_cost
        self.player_attack_power_gain: mpf = player_attack_power_gain
        self.player_defense_gain: mpf = player_defense_gain
        self.player_speed_gain: mpf = player_speed_gain
        self.player_dexterity_gain: mpf = player_dexterity_gain

    def clone(self):
        # type: () -> TrainingOption
        return copy.deepcopy(self)


###########################################
# EXERCISE
###########################################


###########################################
# GENERAL
###########################################


class GameCharacter:
    """
    This class contains attributes of a game character.
    """

    def __init__(self, name):
        # type: (str) -> None
        self.character_id: str = str(uuid.uuid1())
        self.name: str = name

    def clone(self):
        # type: () -> GameCharacter
        return copy.deepcopy(self)


class NPC(GameCharacter):
    """
    This class contains attributes of a non-player character in this game.
    """

    def __init__(self, name):
        # type: (str) -> None
        GameCharacter.__init__(self, name)


class Player(GameCharacter):
    """
    This class contains attributes of the player in this game.
    """

    MIN_ATTACK_GAUGE: mpf = mpf("0")
    FULL_ATTACK_GAUGE: mpf = mpf("1")
    MAX_STAMINA: mpf = mpf("100")

    def __init__(self, name):
        # type: (str) -> None
        GameCharacter.__init__(self, name)
        self.level: int = 1
        self.max_hp: mpf = mpf(random.randint(100, 150))
        self.curr_hp: mpf = self.max_hp
        self.stamina: mpf = self.MAX_STAMINA
        self.attack_power: mpf = mpf(random.randint(20, 30))
        self.defense: mpf = mpf(random.randint(20, 30))
        self.speed: mpf = mpf(random.randint(20, 30))
        self.dexterity: mpf = mpf(random.randint(20, 30))
        self.exp: mpf = mpf("0")
        self.required_exp: mpf = mpf("1e6")
        self.dollars: mpf = mpf("5e6")
        self.attack_gauge: mpf = self.MIN_ATTACK_GAUGE
        self.battle_team: BattleTeam = BattleTeam()
        self.item_inventory: ItemInventory = ItemInventory()
        self.legendary_creature_inventory: LegendaryCreatureInventory = LegendaryCreatureInventory()
        self.city: City or None = None  # initial value
        self.location: AdventureModeLocation = AdventureModeLocation(0, 0)

    def recharge_stamina(self):
        # type: () -> None
        self.stamina += mpf("5")
        if self.stamina >= self.MAX_STAMINA:
            self.stamina = self.MAX_STAMINA

    def move_up(self):
        # type: () -> bool
        if isinstance(self.city, City):
            if self.location.tile_y > 0:
                self.city.get_tile_at(self.location.tile_x, self.location.tile_y).remove_game_character(self)
                self.location.tile_y -= 1
                self.city.get_tile_at(self.location.tile_x, self.location.tile_y).add_game_character(self)
                return True
            return False
        return False

    def move_down(self):
        # type: () -> bool
        if isinstance(self.city, City):
            if self.location.tile_y < len(self.city.get_tiles()) - 1:
                self.city.get_tile_at(self.location.tile_x, self.location.tile_y).remove_game_character(self)
                self.location.tile_y += 1
                self.city.get_tile_at(self.location.tile_x, self.location.tile_y).add_game_character(self)
                return True
            return False
        return False

    def move_left(self):
        # type: () -> bool
        if isinstance(self.city, City):
            if self.location.tile_x > 0:
                self.city.get_tile_at(self.location.tile_x, self.location.tile_y).remove_game_character(self)
                self.location.tile_x -= 1
                self.city.get_tile_at(self.location.tile_x, self.location.tile_y).add_game_character(self)
                return True
            return False
        return False

    def move_right(self):
        # type: () -> bool
        if isinstance(self.city, City):
            if self.location.tile_x < len(self.city.get_tiles()[0]) - 1:
                self.city.get_tile_at(self.location.tile_x, self.location.tile_y).remove_game_character(self)
                self.location.tile_x += 1
                self.city.get_tile_at(self.location.tile_x, self.location.tile_y).add_game_character(self)
                return True
            return False
        return False

    def claim_reward(self, reward):
        # type: (Reward) -> None
        self.exp += reward.player_reward_exp
        self.level_up()
        self.dollars += reward.player_reward_dollars
        for legendary_creature in self.battle_team.get_legendary_creatures():
            legendary_creature.exp += reward.legendary_creature_reward_exp
            legendary_creature.level_up()

        self.battle_team.recover_all()

    def get_city_tile(self):
        # type: () -> CityTile or None
        if isinstance(self.city, City):
            return self.city.get_tile_at(self.location.tile_x, self.location.tile_y)
        return None

    def place_rune_on_legendary_creature(self, legendary_creature, rune):
        # type: (LegendaryCreature, Rune) -> bool
        if legendary_creature in self.legendary_creature_inventory.get_legendary_creatures() and rune in \
                self.item_inventory.get_items():
            legendary_creature.place_rune(rune)
            return True
        return False

    def remove_rune_from_legendary_creature(self, legendary_creature, slot_number):
        # type: (LegendaryCreature, int) -> bool
        if legendary_creature in self.legendary_creature_inventory.get_legendary_creatures():
            if slot_number in legendary_creature.get_runes().keys():
                legendary_creature.remove_rune(slot_number)
                return True
            return False
        return False

    def level_up(self):
        # type: () -> None
        while self.exp >= self.required_exp:
            self.level += 1
            self.required_exp *= mpf("10") ** self.level

    def purchase_item(self, item):
        # type: (Item) -> bool
        if self.dollars >= item.dollars_cost:
            self.dollars -= item.dollars_cost
            self.add_item_to_inventory(item)
            return True
        else:
            print("Not enough dollars!")
            return False

    def sell_item(self, item):
        # type: (Item) -> bool
        if item in self.item_inventory.get_items():
            if isinstance(item, Rune):
                if item.already_placed:
                    return False

            self.remove_item_from_inventory(item)
            self.dollars += item.sell_dollars_gain
            return True
        return False

    def level_up_rune(self, rune):
        # type: (Rune) -> bool
        creature_has_rune: bool = False
        for legendary_creature in self.legendary_creature_inventory.get_legendary_creatures():
            if rune in legendary_creature.get_runes().values():
                creature_has_rune = True
                if self.dollars >= rune.level_up_dollars_cost:
                    self.dollars -= rune.level_up_dollars_cost
                    return legendary_creature.level_up_rune(rune.slot_number)
                else:
                    return False
        if not creature_has_rune:
            if rune in self.item_inventory.get_items():
                if self.dollars >= rune.level_up_dollars_cost:
                    self.dollars -= rune.level_up_dollars_cost
                    return rune.level_up()
                return False
            return False
        return False

    def add_item_to_inventory(self, item):
        # type: (Item) -> None
        self.item_inventory.add_item(item)

    def remove_item_from_inventory(self, item):
        # type: (Item) -> bool
        if isinstance(item, Rune):
            for legendary_creature in self.legendary_creature_inventory.get_legendary_creatures():
                if item in legendary_creature.get_runes().values():
                    return False

        return self.item_inventory.remove_item(item)

    def add_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> None
        self.legendary_creature_inventory.add_legendary_creature(legendary_creature)

    def remove_legendary_creature(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if legendary_creature in self.battle_team.get_legendary_creatures():
            return False
        return self.legendary_creature_inventory.remove_legendary_creature(legendary_creature)

    def add_legendary_creature_to_team(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if legendary_creature in self.legendary_creature_inventory.get_legendary_creatures():
            if self.battle_team.add_legendary_creature(legendary_creature):
                legendary_creature.corresponding_team = self.battle_team
                return True
            return False
        return False

    def remove_legendary_creature_from_team(self, legendary_creature):
        # type: (LegendaryCreature) -> bool
        if legendary_creature in self.legendary_creature_inventory.get_legendary_creatures():
            legendary_creature.corresponding_team = None
            return self.battle_team.remove_legendary_creature(legendary_creature)
        return False

    def level_up_gym(self, gym):
        # type: (ExerciseGym) -> bool
        if self.dollars >= gym.level_up_dollars_cost:
            self.dollars -= gym.level_up_dollars_cost
            gym.level_up()
            return True
        return False

    def train_in_gym(self, gym, option):
        # type: (ExerciseGym, TrainingOption) -> bool
        if option not in gym.get_training_options():
            return False

        if self.stamina < option.stamina_cost:
            return False

        self.stamina -= option.stamina_cost
        self.attack_power += option.player_attack_power_gain
        self.defense += option.player_defense_gain
        self.speed += option.player_speed_gain
        self.dexterity += option.player_dexterity_gain
        return True

    # TODO: implement more methods

    def interact_with_npc(self, npc):
        # type: (NPC) -> None
        pass  # TODO: implement this method

    def take_on_mission(self):
        # type: () -> None
        pass  # TODO: implement this method


class AIPlayer(Player):
    """
    This class contains attributes of an AI controlled player in this game.
    """

    def __init__(self, name):
        # type: (str) -> None
        Player.__init__(self, name)


class Mission:
    """
    This class contains attributes of a mission in this game.
    """

    def __init__(self, name, description, clear_reward):
        # type: (str, str, Reward) -> None
        self.name: str = name
        self.description: str = description
        self.clear_reward: Reward = clear_reward

    def clone(self):
        # type: () -> Mission
        return copy.deepcopy(self)


class ItemShop:
    """
    This class contains attributes of an item shop selling items.
    """

    def __init__(self, items_sold):
        # type: (list) -> None
        self.name: str = "ITEM SHOP"
        self.__items_sold: list = items_sold

    def get_items_sold(self):
        # type: () -> list
        return self.__items_sold

    def clone(self):
        # type: () -> ItemShop
        return copy.deepcopy(self)


class Reward:
    """
    This class contains attributes of a reward gained for accomplishing something in this game.
    """

    def __init__(self, player_reward_exp=mpf("0"), player_reward_dollars=mpf("0"),
                 legendary_creature_reward_exp=mpf("0")):
        # type: (mpf, mpf, mpf) -> None
        self.player_reward_exp: mpf = player_reward_exp
        self.player_reward_dollars: mpf = player_reward_dollars
        self.legendary_creature_reward_exp: mpf = legendary_creature_reward_exp

    def clone(self):
        # type: () -> Reward
        return copy.deepcopy(self)


class AdventureModeLocation:
    """
    This class contains attributes of the location of a player in adventure mode of this game.
    """

    def __init__(self, tile_x, tile_y):
        # type: (int, int) -> None
        self.tile_x: int = tile_x
        self.tile_y: int = tile_y

    def clone(self):
        # type: () -> AdventureModeLocation
        return copy.deepcopy(self)


class SavedGameData:
    """
    This class contains attributes of the saved game data in this game.
    """

    def __init__(self, player_name, temperature, top_p, top_k, max_output_tokens, player_data):
        # type: (str, float, float, float, int, Player) -> None
        self.player_name: str = player_name
        self.temperature: float = temperature
        self.top_p: float = top_p
        self.top_k: float = top_k
        self.max_output_tokens: int = max_output_tokens
        self.player_data: Player = player_data

    def __str__(self):
        # type: () -> str
        res: str = ""  # initial value
        res += str(self.player_name).upper() + "\n"
        res += "Temperature: " + str(self.temperature) + "\n"
        res += "Top P: " + str(self.top_p) + "\n"
        res += "Top K: " + str(self.top_k) + "\n"
        res += "Max output tokens: " + str(self.max_output_tokens) + "\n"
        return res

    def clone(self):
        # type: () -> SavedGameData
        return copy.deepcopy(self)


###########################################
# GENERAL
###########################################


# Creating main function used to run the game.


def main() -> int:
    """
    This main function is used to run the game.
    :return: an integer
    """

    load_dotenv()
    gemini.configure(api_key=os.environ['GEMINI_API_KEY'])

    # Gemini safety settings
    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]

    # Saved game data
    saved_game_data: SavedGameData = (SavedGameData("", 0, 0, 0,
                                                    0, Player("NONE")))  # initial value

    # The player's name
    player_name: str = ""  # initial value

    # Gemini Generative Model
    model = gemini.GenerativeModel(model_name="gemini-1.5-pro",
                                       generation_config={
                                           "temperature": 1,
                                           "top_p": 0.95,
                                           "top_k": 64,
                                           "max_output_tokens": 8192,
                                           "response_mime_type": "text/plain",
                                       },
                                       safety_settings=safety_settings)  # initial value

    print("Enter \"NEW GAME\" to create new saved game data.")
    print("Enter \"LOAD GAME\" to load existing saved game data.")
    action: str = input("What do you want to do? ")
    while action not in ["NEW GAME", "LOAD GAME"]:
        clear()
        print("Enter \"NEW GAME\" to create new saved game data.")
        print("Enter \"LOAD GAME\" to load existing saved game data.")
        action = input("Sorry, invalid input! What do you want to do? ")

    game_started: bool = False
    while not game_started:
        if action == "NEW GAME":
            clear()

            player_name = input("Please enter player name: ")
            saved_game_files: list = [f for f in os.listdir("../saved")]
            while player_name in saved_game_files:
                print("Below is a list of existing saved game files:\n")
                for i in range(len(saved_game_files)):
                    print(str(i + 1) + ". " + str(saved_game_files[i]))

                player_name = input("Sorry, player name " + str(player_name) + " already exists! "
                                                                               "Enter another player name: ")

            saved_game_data = SavedGameData(player_name, 1, 0.95, 64, 8192, Player(player_name))

            # Generate 5 random legendary creatures to be placed in player's battle team.
            for i in range(5):
                new_legendary_creature: LegendaryCreature = (generate_random_legendary_creature
                                                             (random.choice(LegendaryCreature.POTENTIAL_ELEMENTS)))
                saved_game_data.player_data.add_legendary_creature(new_legendary_creature)
                saved_game_data.player_data.add_legendary_creature_to_team(new_legendary_creature)

            # TODO: initialize the city map

        else:
            clear()

            saved_game_files: list = [f for f in os.listdir("../saved")]
            if len(saved_game_files) == 0:
                action = "NEW GAME"

            print("Below is a list of existing saved game files:\n")
            for i in range(len(saved_game_files)):
                print(str(i + 1) + ". " + str(saved_game_files[i]))

            player_name = input("Please enter player name associated with saved game data you want to load: ")
            while player_name not in saved_game_files:
                clear()
                print("Below is a list of existing saved game files:\n")
                for i in range(len(saved_game_files)):
                    print(str(i + 1) + ". " + str(saved_game_files[i]))

                player_name = input("Sorry, invalid input! Please enter player name associated with "
                                            "saved game data you want to load: ")

            saved_game_data = load_game_data(os.path.join("../saved", player_name))

            # Set up the model
            generation_config = {
                "temperature": saved_game_data.temperature,
                "top_p": saved_game_data.top_p,
                "top_k": saved_game_data.top_k,
                "max_output_tokens": saved_game_data.max_output_tokens,
            }

            model = gemini.GenerativeModel(model_name="gemini-1.5-pro",
                                           generation_config=generation_config,
                                           safety_settings=safety_settings)
            game_started = True

    # Start playing the game.
    while True:
        clear()
        print("Enter \"Y\" for yes.")
        print("Enter anything else for no.")
        continue_playing: str = input("Do you want to continue playing? ")
        if continue_playing != "Y":
            save_game_data(saved_game_data, os.path.join("../saved", player_name))
            return 0  # successfully saved the game

        clear()

    # TODO: implement in-game functionality

    # Start playing the game.
    while True:
        clear()


if __name__ == "__main__":
    main()
