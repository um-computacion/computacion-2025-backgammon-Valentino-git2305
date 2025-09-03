from enum import Enum

class Player(Enum):
    WHITE = -1 #Jugador Blanco
    BLACK = 1 #Jugador Negro

    def __init__(self, value):
        #Atributo de intancia con el nombre de mi formato
        self.__value__ = value
    
    def __direction__(self):
        '''Sentido de movimiento en el tablero:
           WHITE devuelve -1 (23 -> 0)
           BLACK devuelve +1 (0 -> 23)'''
        if self is Player.WHITE:
            return -1
        else:
            return 1
    
    def __home_range__(self):
        '''Rango de casillas que forman la casa del jugador(Sector en el cual todaas las fichas de ese jugador deben estan para comenzar a sacarlas)
           WHITE: Desde la casilla 0 hasta la 5
           BLACK: Desde la casilla 18 hacia la 23'''
        
        if self is Player.WHITE:
            return range (0, 6) 
        else:
            return range (18, 24)
        
        '''El rango marcado en range es de 0 a 6 y de 18 a 24 porque en la funcion range (a, b) excluye b'''

    def  __str__(self):
        return self.name
    