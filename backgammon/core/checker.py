from backgammon.core.player import Player
from enum import Enum

class CheckerColor(Enum):
    WHITE = "white"
    BLACK = "black"
    RED = "red"
    BLUE = "blue"
    GREEN = "green"

class Checker:
    __palette__ = {
        Player.WHITE: CheckerColor.WHITE,
        Player.BLACK: CheckerColor.BLACK,
    }

    def __init__(self, owner_or_color, color: CheckerColor = None):
        if isinstance(owner_or_color, Player):
            self.__owner__ = owner_or_color
            self.__color__ = color if color is not None else self.__palette__[owner_or_color]
        elif isinstance(owner_or_color, CheckerColor):
            self.__color__ = owner_or_color
            if owner_or_color == CheckerColor.WHITE:
                self.__owner__ = Player.WHITE
            elif owner_or_color == CheckerColor.BLACK:
                self.__owner__ = Player.BLACK
            else:
                self.__owner__ = None
        
        else:
            raise ValueError("Chcker debe inicializarse con Player o ChckerColor")
    
    @property
    def owner(self) -> Player:
        return self.__owner__
    
    @property
    def color(self) -> CheckerColor:
        return self.__color__
    
    def __str__(self):
        icons = {
            CheckerColor.WHITE: "⚪",
            CheckerColor.BLACK: "⚫",
            CheckerColor.RED:   "🔴",
            CheckerColor.BLUE:  "🔵",
            CheckerColor.GREEN: "🟢",
        }
        return icons.get(self.__color__,"⬤")
    
    def __eq__(self, other):
        return isinstance (other, Checker) and self.__owner__ == other.__owner__ and self.__color__== other.__color__
    
    @classmethod
    def set_color_for_player(cls, player: Player, color: CheckerColor) -> None:
        cls.__palette__[player] = color
        
    