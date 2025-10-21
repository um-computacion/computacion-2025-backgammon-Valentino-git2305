## [Día 3] - 2025-08-28
### AI:
- ChatGPT
### PROMPT:
Chat, crees que debo agregarle algo mas a mi clase Player?
### Respuesta:
¡Excelente instinto, Valen! 🔎 Y sí: antes de cerrar el Pull Request es buen momento para revisar si falta algo importante en Player.

Vamos a hacerlo juntos.

✅ Lo que ya tiene tu clase Player:
    from enum import Enum

class Player(Enum):
    WHITE = -1
    BLACK = 1

    def __init__(self, value):
        self.__value__ = value
    
    def __direction__(self):
        if self is Player.WHITE:
            return -1
        else:
            return 1

    def __home_range__(self):
        if self is Player.WHITE:
            return range(0, 6)
        else:
            return range(18, 24)

⚠️ Opcional: Agregar __str__() para mostrar bonito

Si querés que cuando imprimas un Player aparezca "WHITE" o "BLACK" y no algo como <Player.WHITE: -1>, podés agregar esto:

    def __str__(self):
        return self.name

✍️ Commit sugerido
git add .
git commit -m "Agrega método __str__() en Player para mejor impresión"
git push origin 8-implementar-player-y-board-con-setup-inicial

### Que hice:
- Agregué __str__ ya que como me pareció conveniente tenerlo en esta clase también ya que tambien tengo __str__ en la clase Board porque no me gusta muestra Enum el mensaje y quiero que la salida del codigo sea mas limpia.

### AI:
- ChatGPT
### PROMPT:
mi clase game quedo asi dime si hay que cambiar, agregar o correguir algo 

from backgammon.core.board import Board
from backgammon.core.dice import Dice
from backgammon.core.player import Player

class Game :
    """
    Esta clase administrara: El estado global del (Tablero, Dados, Turnos), El ciclo de turnos,
    El inicio y reinicio de la partida, Consultas de estado.
    """

    def __init__(self):
        "Crea un partida nueva sin iniciar"
        self.__board__ = Board()
        self.__dice__ = Dice()
        self. __current_player__ = None
        self.started = False
        self.finished = False
        self.winner = None
        self.turn_count = 0
        self.__history__ = []
    
    def start(self):
        """
        Inicia la Partida
        """
        self.__board__.__reset__()
        self.__dice__.__reset__()
        self.__started__ = True
        self.__finished__ = False
        self.__winner__ = None
        self.__turn_count__ = 1

        while True:
            white_roll = self.__dice__.roll()[0]
            black_roll = self.__dice__.roll()[1]
            if white_roll != black_roll:
                break
        self.__current_player__ = (
            Player.WHITE if white_roll > black_roll else Player.BLACK
        )
        self.__history__.append(
            f"Game: Start = WHITE {white_roll} vs BLACK {black_roll} /"
            f"Comienza {self.__current_player__.name}"
        )

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
    def finiched(self) -> bool:
        return self.__finished__

    @property
    def winner(self):
        return self.__winner__
    
    @property
    def turn_count(self) -> int:
        return self.__turn_count__
    
    def roll(self):
        """
        Tira los dados del turno correspondiente y no devuelve los valores 
        """
        if not self.__started__:
            raise ValueError("La partida no fue iniciada, Comienza una partida para lanzar los dados.")
        vals = self.__dice__.roll()
        self.__history__.append(f"{self.__current_player__.name} roll: {vals[0]}-{vals[1]}")
        return vals
    
    def pass_turn(self):
        """
        Pasa el turno al siguiente player
        """
        if not self.__started__ or self.__finished__:
            return
        self.__current_player__ = Player.BLACK if self.__current_player__ is Player.WHITE else Player.WHITE
        self.__turn_count__ += 1
        self.__dice__.reset()
        self.__history__.append(f"Turno: Ahora juega {self.__current_player__.name}")

    def check_game_over(self):
        """
        Verifica si alguien ganó
        """
        white_out = len(self.__board__.__borne__[Player.WHITE] == 15)
        black_out = len(self.__board__.__borne__[Player.BLACK] == 15)
        if white_out or black_out:
            self.__finished__ = True
            self.__winner__ = Player.WHITE if white_out else Player.BLACK
            self.__history__.append(f"Game: Terminó, (Winner {self.__winner__.name})")
        
    def __str__(self):
        """
        Vista resumida del juego sobre quien juega, el estado de los dados, si alguien gano y quien
        """
        status = []
        status.append(f"Turno #{self.__turn_count__}" if self.__started__ else "Partida no iniciada")
        if self.__started__:
            status.append(f"Juega: {self.__current_player__.name}")
            status.append(f"Dados: {str(self.__dice__)}")
            if self.__finished__:
                status.append(f"Ganador: {self.__winner__.name}")
        return " | ".join(status)
    
    def history(self):
        """
        Nos devuelve una copia de los eventos registrados
        """
        return int(self.__history__)
      
### Respuesta:
¡Bien ahí, Valentino! Revisé tu Game y hay varias cositas para pulir. Te marco los problemas para que los puedas correguir.

🔍 Problemas detectados

Inconsistencia de nombres de atributos

En __init__ creás self.started, self.finished, self.winner, self.turn_count (sin __).

En el resto de la clase usás self.__started__, self.__finished__, etc.

Solución: usar SIEMPRE la convención del proyecto: __nombre__.

Espacio extraño

self. __current_player__ = None tiene un espacio entre self. y __current....

reset anidado dentro de start

Tu def reset(self): quedó indentado dentro de start. Así no se define como método de la clase.

Solución: dedéntalo (al mismo nivel que start).

Uso de métodos que no existen

self.__dice__.__reset__() no existe (tu Dice tiene reset()).

Solución: self.__dice__.reset().

Tirada inicial mal implementada

En start() hacés:

white_roll = self.__dice__.roll()[0]
black_roll = self.__dice__.roll()[1]


Eso llama a roll() dos veces, y toma el 1° valor de la 1ª tirada para WHITE y el 2° valor de la 2ª tirada para BLACK (no lo que querés).

Lo correcto: usar un dado por jugador con random.randint(1,6), o una sola tirada y comparar, pero sin mezclar.

Además, con tu elección de “reset preparatorio” (opción B) querés que start() haga la tirada inicial para decidir quién empieza pero sin dejar valores de dados “guardados” para ese primer turno. Por eso conviene usar random directo para decidir y luego resetear los dados.

Bug en check_game_over

len(self.__board__.__borne__[Player.WHITE] == 15) → las paréntesis están mal.

Debe ser: len(self.__board__.__borne__[Player.WHITE]) == 15 (y lo mismo para BLACK).

history() devuelve int(...)

return int(self.__history__) rompe (no se puede castear una lista a int).

Debe devolver una copia de la lista: return list(self.__history__).

Typo en propiedad

def finiched(self) → debería ser finished.

Mensajes y docstrings

Pequeños ajustes de texto para claridad.
### Que hice:
Corregi las cosas y tambien discuti algunas correcciones que me hizo ya que no las entendia como la siguiente correccion:

Tirada inicial mal implementada

En start() hacés:

white_roll = self.__dice__.roll()[0]
black_roll = self.__dice__.roll()[1]


Eso llama a roll() dos veces, y toma el 1° valor de la 1ª tirada para WHITE y el 2° valor de la 2ª tirada para BLACK (no lo que querés).

Lo correcto: usar un dado por jugador con random.randint(1,6), o una sola tirada y comparar, pero sin mezclar.

Además, con tu elección de “reset preparatorio” (opción B) querés que start() haga la tirada inicial para decidir quién empieza pero sin dejar valores de dados “guardados” para ese primer turno. Por eso conviene usar random directo para decidir y luego resetear los dados.

Y me pide que haga un random.randint pero ya lo entendi ya que la tirada esta no es la de la partida sino que es la tirada inicial para ver quien inicia.
