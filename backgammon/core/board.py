class Board:
    '''Tablero:
       24 puntos enumerados del 0 al 23
       Cada punto puede tener 0 o 5 fichas como maximo de un jugador
       Administacion de barra (sector donde van las piezas comidas) y borne (sector donde van las fichas retiradas del juego)'''
    
from backgammon.core.player import Player
from backgammon.core.checker import Checker

class Board:
    def __init__(self):#Inicializa un tabelro vacio con barra y borne por Player        
        self.__points__=[ [] for _ in range(24) ]
        self.__bar__ = {Player.WHITE: [], Player.BLACK: []}
        self.__borne__={Player.WHITE: [], Player.BLACK: []}
    
    def __setup__(self):#Posicion de las fichas al comienzo de la partida
        self.__points__[0] = [Checker(Player.BLACK) for _ in range(2)]
        self.__points__[5] = [Checker(Player.WHITE) for _ in range(5)]
        self.__points__[7] = [Checker(Player.WHITE) for _ in range(3)]
        self.__points__[11] = [Checker(Player.BLACK) for _ in range(5)]
        self.__points__[12] = [Checker(Player.WHITE) for _ in range(5)]
        self.__points__[16] = [Checker(Player.BLACK) for _ in range(3)]
        self.__points__[18] = [Checker(Player.BLACK) for _ in range(5)]
        self.__points__[23] = [Checker(Player.WHITE) for _ in range(2)]

    def __reset__(self):#Reinicia el tablero a la posicion inicial
        self.__points__=[[] for _ in range(24)]
        self.__bar__={Player.WHITE:[], Player.BLACK:[]}
        self.__borne__={Player.WHITE:[], Player.BLACK:[]}

        self.__points__[0] = [Checker(Player.BLACK) for _ in range(2)]
        self.__points__[5] = [Checker(Player.WHITE) for _ in range(5)]
        self.__points__[7] = [Checker(Player.WHITE) for _ in range(3)]
        self.__points__[11] = [Checker(Player.BLACK) for _ in range(5)]
        self.__points__[12] = [Checker(Player.WHITE) for _ in range(5)]
        self.__points__[16] = [Checker(Player.BLACK) for _ in range(3)]
        self.__points__[18] = [Checker(Player.BLACK) for _ in range(5)]
        self.__points__[23] = [Checker(Player.WHITE) for _ in range(2)]
    
    def owner_at(self, idx: int):#Nos sirve para ver que fiicha hay en un punto.
        pile = self.__points__[idx]
        return pile[-1].owner if pile else None
    
    def count_at(self, idx: int) -> int:#Nos dice cuantas fichas hay en un punto.
        return len(self.__points__[idx])
    
    def is_blocked_for(self, player: Player, idx: int) -> bool:#Nos sirve para saber si un punto esta bloqueado por el otro jugador o no.
        if not (0 <= idx < 24):
            return False
        opp = Player.BLACK if player is Player.WHITE else Player.WHITE
        return self.owner_at(idx) is opp and self.count_at(idx) >= 2
    
    def entry_index_from_bar(self, player: Player, die:int) -> int:#Nos sive para que un jugador pueda volver al juego si le comieron una ficha.
        return (die -1) if player is Player.WHITE else (24 - die)
    
    def dest_index(self, player:Player, src: int, die:int) -> int:#Nos sirve para calcular el punto donde va a terminar la ficha, las blancas+1 negras-1.
        direction = 1 if player is Player.WHITE else -1
        return src +direction * die


    def __count_checkers__(self, player: Player) -> int:#Cuenta las fichas de cada jugador en el tablero, barra y brone
        total=0
        for point in self.__points__:
            total += sum(1 for c in point if getattr(c, "owner", None) == player)
        total += len(self.__bar__[player])
        total += len(self.__borne__[player])
        return total
    
    def __str__(self):#Nos da en texto como esta el tablero
        output = []

        for i, point in enumerate(self.__points__):
            if point:
                owner = point[0].owner.name
                color = point[0].color.name
                cantidad = len(point)
                output.append(f"{i:2d}: {cantidad} ficha(s) de {owner} ({color})")
            else:
                output.append(f"{i:2d}: vacio")
        
        return "\n".join(output)