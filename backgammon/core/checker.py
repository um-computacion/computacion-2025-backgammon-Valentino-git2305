from backgammon.core.player import Player
from enum import Enum

class CheckerColor(Enum):
    WHITE = "white"
    BLACK = "black"
    RED = "red"
    BLUE = "blue"
    GREEN = "green"

class Checker:
    def __init__(self, color: CheckerColor):
        self.__color__ = color
    
    def __str__(self):
        color_map = {
            CheckerColor.WHITE: "⚪",
            CheckerColor.BLACK: "⚫",
            CheckerColor.RED: "🔴",
            CheckerColor.BLUE: "🔵",
            CheckerColor.GREEN: "🟢",
        }
        return color_map.get(self.__color__, "⬤")

    def __eq__(self, other):
        return isinstance(other, Checker) and self.__color__ == other.__color__
    
    