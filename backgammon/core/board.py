class Board:
    '''Tablero:
       24 puntos enumerados del 0 al 23
       Cada punto puede tener 0 o 5 fichas como maximo de un jugador
       Administacion de barra (sector donde van las piezas comidas) y borne (sector donde van las fichas retiradas del juego)'''
    
from backgammon.core.player import Player

class Board:
    def __init__(self):
        """Inicializa un tabelro vacio con barra y borne por Player"""
         
        self.__points__=[ [] for _ in range(24) ]
        self.__bar__ = {Player.WHITE: [], Player.BLACK: []}
        self.__brone__={Player.WHITE: [], Player.BLACK: []}
    
    def __setup__(self):
        """Posicion de las fichas al comienzo de la partida"""
        self.__points__[0] = [Player.BLACK] * 2
        self.__points__[5] = [Player.WHITE] * 5
        self.__points__[7] = [Player.WHITE] * 3
        self.__points__[11] = [Player.BLACK] * 5
        self.__points__[12] = [Player.WHITE] * 5
        self.__points__[16] = [Player.BLACK] * 3
        self.__points__[18] = [Player.BLACK] * 5
        self.__points__[23] = [Player.WHITE] * 2

    def __reset__(self):
        """Reinicia el tablero a la posicion inicial"""
        self.__points__=[[] for _ in range(24)]
        self.__bar__={Player.WHITE:[], Player.BLACK:[]}
        self.__brone__={Player.WHITE:[], Player.BLACK:[]}

        self.__points__[0] = [Player.BLACK] * 2
        self.__points__[5] = [Player.WHITE] * 5
        self.__points__[7] = [Player.WHITE] * 3
        self.__points__[11] = [Player.BLACK] * 5
        self.__points__[12] = [Player.WHITE] * 5
        self.__points__[16] = [Player.BLACK] * 3
        self.__points__[18] = [Player.BLACK] * 5
        self.__points__[23] = [Player.WHITE] * 2

    def __count_checkers__(self, player):
        """Cuenta las fichas de cada jugador en el tablero, barra y brone"""
        total=0

        for point in self.__points__:
            total += point.count(player)

        total += len(self.__bar__[player])
        total += len(self.__brone__[player])

        return total
    
    def __str__(self):
        """Nos da en texto como esta el tablero"""
        output = []

        for i, point in enumerate(self.__points__):
            if point:
                owner = point[0].name
                cantidad = len(point)
                output.append(f"{i:2d}: {cantidad} ficha(s) de {owner}")
            else:
                output.append(f"{i:2d}: vacio")
        
        return "\n".join(output)