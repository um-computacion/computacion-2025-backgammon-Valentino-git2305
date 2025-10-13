import unittest

from backgammon.core.board import Board
from backgammon.core.player import Player
from backgammon.core.checker import Checker

def owner_at(board, idx):#Nos devuelce la lista de Players en un punto
    return [c.owner for c in board.__points__[idx]]

class TestBoard(unittest.TestCase):
    
    def test_init_board(self):
        tablero = Board()

        self.assertEqual(len(tablero.__points__), 24)#Cheque que el tablero tenga 24 puntos.

        for punto in tablero.__points__:
            self.assertIsInstance(punto, list)#Chequea que cada punto del tablero sea una lista vacia .
        
        self.assertEqual(tablero.__bar__[Player.WHITE], [])#Cheque que las barras empiecen vacias.
        self.assertEqual(tablero.__bar__[Player.BLACK], [])

        self.assertEqual(tablero.__borne__[Player.WHITE], [])#Cheque que el borne empiecen vacias.
        self.assertEqual(tablero.__borne__[Player.BLACK], [])
    
    def test_setup_board(self): #Cheque que el todas las fichas esten en los lugares correspondientes como lo indica el reglamento.
        tablero = Board()
        tablero.__setup__()

        self.assertEqual(owner_at(tablero, 0), [Player.BLACK] * 2)
        self.assertEqual(owner_at(tablero, 5), [Player.WHITE] * 5)
        self.assertEqual(owner_at(tablero, 7), [Player.WHITE] * 3)
        self.assertEqual(owner_at(tablero, 11), [Player.BLACK] * 5)
        self.assertEqual(owner_at(tablero, 12), [Player.WHITE] * 5)
        self.assertEqual(owner_at(tablero, 16), [Player.BLACK] * 3)
        self.assertEqual(owner_at(tablero, 18), [Player.BLACK] * 5)
        self.assertEqual(owner_at(tablero, 23), [Player.WHITE] * 2)

    def test_count_checkers(self):
        tablero = Board()
        tablero.__setup__()

        self.assertEqual(tablero.__count_checkers__(Player.WHITE), 15)
        self.assertEqual(tablero.__count_checkers__(Player.BLACK), 15)

    def test_reset_board(self):
        tablero = Board()
        tablero.__reset__()

        self.assertEqual(tablero.__count_checkers__(Player.WHITE), 15)
        self.assertEqual(tablero.__count_checkers__(Player.BLACK), 15)

        self.assertEqual(owner_at(tablero, 0), [Player.BLACK] * 2)
        self.assertEqual(owner_at(tablero, 5), [Player.WHITE] * 5)
        self.assertEqual(owner_at(tablero, 7), [Player.WHITE] * 3)
        self.assertEqual(owner_at(tablero, 11), [Player.BLACK] * 5)
        self.assertEqual(owner_at(tablero, 12), [Player.WHITE] * 5)
        self.assertEqual(owner_at(tablero, 16), [Player.BLACK] * 3)
        self.assertEqual(owner_at(tablero, 18), [Player.BLACK] * 5)
        self.assertEqual(owner_at(tablero, 23), [Player.WHITE] * 2)

    def test_str_board(self):
        tablero = Board()
        tablero.__reset__()
        output =str(tablero)

        self.assertIsInstance(output, str)
        lineas = output.strip().split("\n")
        self.assertEqual(len(lineas), 24)
        self.assertTrue(lineas[0].startswith("0:"))
        self.assertTrue(lineas[-1].startswith("23:"))
    
    def owners_at(board, idx):
        return [c.owner for c in board.__points__[idx]]
    
def test_is_blocked_for_boundaries_and_rules():
    b = Board()
    b.__reset__()
    #fuera de rango  False
    assert b.is_blocked_for(Player.WHITE, -1) is False
    assert b.is_blocked_for(Player.WHITE, 24) is False
    #bloquear ponemos 2 negras en un punto
    b.__points__[8] = [Checker(Player.BLACK), Checker(Player.BLACK)]
    assert b.is_blocked_for(Player.WHITE, 8) is True
    #1 sola del rival no bloquea
    b.__points__[9] = [Checker(Player.BLACK)]
    assert b.is_blocked_for(Player.WHITE, 9) is False

def test_entry_index_from_bar():
    b = Board()
    assert b.entry_index_from_bar(Player.WHITE, 1) == 0
    assert b.entry_index_from_bar(Player.WHITE, 6) == 5
    assert b.entry_index_from_bar(Player.BLACK, 1) == 23
    assert b.entry_index_from_bar(Player.BLACK, 6) == 18

def test_dest_index_direction():
    b = Board()
    assert b.dest_index(Player.WHITE, 6, 3) == 9   # suma
    assert b.dest_index(Player.BLACK, 20, 4) == 16 # resta
if __name__ == "__main__":
    unittest.main()