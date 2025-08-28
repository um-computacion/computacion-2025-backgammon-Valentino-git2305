import unittest

from backgammon.core.board import Board
from backgammon.core.player import Player

class TestBoard(unittest.TestCase):
    
    def test_init_board(self):
        tablero = Board()

        self.assertEqual(len(tablero.__points__), 24)#Cheque que el tablero tenga 24 puntos.

        for punto in tablero.__points__:
            self.assertIsInstance(punto, list)#Cheque que cada punto del tablero sea una lista vacia .
        
        self.assertEqual(tablero.__bar__[Player.WHITE], [])#Cheque que las barras empiecen vacias.
        self.assertEqual(tablero.__bar__[Player.BLACK], [])

        self.assertEqual(tablero.__brone__[Player.WHITE], [])#Cheque que el brone empiecen vacias.
        self.assertEqual(tablero.__brone__[Player.BLACK], [])
    
    def test_setup_board(self): #Cheque que el todas las fichas esten en los lugares correspondientes como lo indica el reglamento.
        tablero = Board()
        tablero.setup()

        self.assertEqual(tablero.__points__[0], [Player.BLACK] * 2)
        self.assertEqual(tablero.__points__[5], [Player.WHITE] * 5)
        self.assertEqual(tablero.__points__[7], [Player.WHITE] * 3)
        self.assertEqual(tablero.__points__[11], [Player.BLACK] * 5)
        self.assertEqual(tablero.__points__[12], [Player.WHITE] * 5)
        self.assertEqual(tablero.__points__[16], [Player.BLACK] * 3)
        self.assertEqual(tablero.__points__[18], [Player.BLACK] * 5)
        self.assertEqual(tablero.__points__[23], [Player.WHITE] * 2)

if __name__ == "__main__":
    unittest.main()