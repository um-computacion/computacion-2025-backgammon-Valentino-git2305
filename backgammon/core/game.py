from backgammon.core.board import Board
from backgammon.core.dice import Dice
from backgammon.core.player import Player
from backgammon.core.exceptions import(
    GameNotStrated, GameAlredyStarted, GameFinished, DiceAlreadyRolled, DiceNotRolled
    ) 
import random

class Game :
    """
    Esta clase administrara: El estado global del (Tablero, Dados, Turnos), El ciclo de turnos,
    El inicio y reinicio de la partida, Consultas de estado.
    """

    def __init__(self):
        "Crea un partida nueva sin iniciar"
        self.__board__ = Board()
        self.__dice__ = Dice()
        self.__current_player__ = None
        self.__started__ = False
        self.__finished__ = False
        self.__winner__ = None
        self.__turn_count__ = 0
        self.__history__ = []
        self.__players_info__ = {}
    
    def start(self):
        """
        Inicia la Partida
        """
        """
        Inicia la partida, pero deja pendiente el sorteo inicial
        hasta que el usuario haga 'roll'.
        """
        if self.__started__ and not self.__finished__:
            raise GameAlredyStarted()

        self.__board__.__reset__()
        self.__dice__.reset()
        self.__started__ = True
        self.__finished__ = False
        self.__winner__ = None
        self.__turn_count__ = 1

        self.__current_player__ = None        # <<< clave: aún no hay jugador
        self.__needs_opening_roll__ = True    # <<< sorteo pendiente

        self.__history__.append("Game: Start (esperando sorteo con 'roll')")

    def reset(self):
        """
        Reinicia la partida
        """
        self.__board__.__reset__()
        self.__dice__.reset()
        self.__current_player__ = None
        self.__started__ = False
        self.__finished__ = False
        self.__winner__ = None
        self.__turn_count__ = 0
        self.__history__.append("Game:Reset")

    
    @property
    def board(self) -> Board:
        return self.__board__

    @property
    def dice(self) -> Dice:
        return self.__dice__         

    @property
    def current_player(self) -> Player:
        return self.__current_player__

    @property
    def started(self) -> bool:
        return self.__started__               

    @property
    def finished(self) -> bool:
        return self.__finished__

    @property
    def winner(self):
        return self.__winner__
    
    @property
    def turn_count(self) -> int:
        return self.__turn_count__
    
    def roll(self):
        """
        Si hay sorteo pendiente, tira WHITE/BLAK hasta desempatar,
        fija quién arranca y devuelve [white, black].
        Si ya hay current_player, es una tirada normal del turno.
        """
        if not self.__started__:
            raise GameNotStrated()
        if self.__finished__:
            raise GameFinished()

        if self.__current_player__ is None:
            w = random.randint(1, 6)
            b = random.randint(1, 6)
            while w == b:
                w = random.randint(1, 6)
                b = random.randint(1, 6)
            self.__current_player__ = Player.WHITE if w > b else Player.BLACK
            self.__history__.append(
                f"Draw: WHITE {w} vs BLACK {b} -> {self.__current_player__.name} starts"
            )
            self.__dice__.reset()
            return[w, b]
        if self.__dice__.values != (0, 0):
            raise DiceAlreadyRolled()
        vals = self.__dice__.roll()
        self.__history__.append(
            f"{self.__current_player__.name} roll: {vals[0]}-{vals[1]}"
        )
        return vals
    
    def pass_turn(self):
        """
        Pasa el turno al siguiente player
        """
        if not self.__started__:
            raise GameNotStrated()
        if self.__finished__:
            return 
        if self.__dice__.values == (0, 0):
            raise DiceNotRolled
        
        self.__current_player__ =(Player.BLACK if self.__current_player__ is Player.WHITE else Player.WHITE)
        self.__turn_count__ += 1
        self.__dice__.reset()
        self.__history__.append(f"Turno: Ahora juega {self.__current_player__.name}")

    def check_game_over(self):
        """
        Verifica si alguien ganó
        """
        white_out = len(self.__board__.__borne__[Player.WHITE]) == 15
        black_out = len(self.__board__.__borne__[Player.BLACK]) == 15
        if white_out or black_out:
            self.__finished__ = True
            self.__winner__ = Player.WHITE if white_out else Player.BLACK
            self.__history__.append(f"Game: Terminó, (Winner {self.__winner__.name})")
        else:
            self.__finished__ = False
            self.__winner__ = None
    
    def setup_players(self, who_is_white: str, who_is_black:str) -> None:
        """
        Define los nombres de los jugadoer segun el tablero (WHITE/BLACK)
        Debe llamarse antes de start() si queres nombres personalizados 
        """
        self.__players_info__ = {
            "WHITE": who_is_white.strip() or "Jugador Blanco",
            "BLACK": who_is_black.strip() or "Jugador Negro"
        }
        self.__history__.append(
            f"Jugadores: WHITE={self.__players_info__["WHITE"]} / BLACK={self.__players_info__["BLACK"]}"
        )
    
    def get_player_name(self, player: Player) -> str:
        """
        Devuelve el nombre del jugador segun su Player
        """
        return self.__players_info__.get(player.name, player.name)
        
    def __str__(self):
        """
        Vista resumida del juego
        """
        status = []
        status.append(f"Turno #{self.__turn_count__}" if self.__started__ else "Partida no iniciada")
        if self.__started__:
            if self.__current_player__ is None:
               status.append("Juega: — (falta sorteo)")
            else:
                status.append(f"Juega: {self.__current_player__.name}")
            status.append(f"Dados: {str(self.__dice__)}")
            if self.__finished__:
                status.append(f"Ganador: {self.__winner__.name}")
        return " | ".join(status)

        status.append(f"Juega: {self.get_player_name(self.__current_player__)}")

    def history(self):
        """
        Nos devuelve una copia de los eventos registrados
        """
        return list(self.__history__)
      