
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
    
    def setup(self):
        """Posicion de las fichas al comienzo de la partida"""
        self.__points__[0] = [Player.BLACK] * 2
        self.__points__[5] = [Player.WHITE] * 5
        self.__points__[7] = [Player.WHITE] * 3
        self.__points__[11] = [Player.BLACK] * 5
        self.__points__[12] = [Player.WHITE] * 5
        self.__points__[16] = [Player.BLACK] * 3
        self.__points__[18] = [Player.BLACK] * 5
        self.__points__[23] = [Player.WHITE] * 2