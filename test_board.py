import unittest

from backgammon.core.board import Board
from backgammon.core.player import Player
from backgammon.core.checker import Checker
from backgammon.core.exceptions import (
    PointBlocked, NoCheckerAtPoint, MustEnterFromBar, EntryBlocked, BearOffNotAllowed
)

def owner_at(board, idx):#Nos devuelce la lista de Players en un punto
    return [c.owner for c in board.__points__[idx]]

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.b = Board()
        self.b.__reset__()

    def test_normal_move_white_to_empty(self):
        self.b.move(Player.WHITE, 5, 1)
        self.assertEqual(self.b.owner_at(6), Player.WHITE)
        self.assertEqual(self.b.count_at(5), 4)
        self.assertEqual(self.b.count_at(6), 1)

    def test_point_blocked_raises(self):
        with self.assertRaises(PointBlocked):
            self.b.move(Player.WHITE, 12, 6)

    def test_hit_on_single_opponont(self):
        self.b.__points__[6] = [Checker(Player.BLACK)]
        before_bar_black = len(self.b.__bar__[Player.BLACK])

        self.b.move(Player.WHITE, 5, 1)

        self.assertEqual(len(self.b.__bar__[Player.BLACK]), before_bar_black + 1)
        self.assertEqual(self.b.owner_at(6), Player.WHITE)  # <- este era el assert correcto

    def test_must_enter_from_bar(self):
        self.b.__bar__[Player.WHITE].append(Checker(Player.WHITE))
        with self.assertRaises(MustEnterFromBar):
            self.b.move(Player.WHITE, 5, 1)

    def test_entry_blocked_from_bar(self):
        self.b.__bar__[Player.WHITE].append(Checker(Player.WHITE))
        self.b.__points__[0] = [Checker(Player.BLACK), Checker(Player.BLACK)]
        with self.assertRaises(EntryBlocked):
            self.b.move(Player.WHITE, None, 1)

    def test_entry_from_bar_with_hit(self):
        self.b.__bar__[Player.WHITE].append(Checker(Player.WHITE))
        self.b.__points__[0] = [Checker(Player.BLACK)]
        before_bar_black = len(self.b.__bar__[Player.BLACK])

        self.b.move(Player.WHITE, None, 1)

        self.assertEqual(self.b.owner_at(0), Player.WHITE)
        self.assertEqual(len(self.b.__bar__[Player.BLACK]), before_bar_black + 1)

    def test_bear_off_not_allowed_if_not_all_in_home(self):
        self.b.__points__ = [[] for _ in range(24)]
        self.b.__bar__ = {Player.WHITE: [], Player.BLACK: []}
        self.b.__borne__ = {Player.WHITE: [], Player.BLACK: []}
        self.b.__points__[10] = [Checker(Player.WHITE)]  # fuera del home
        self.b.__points__[23] = [Checker(Player.WHITE)]  # intenta salir con 1
        with self.assertRaises(BearOffNotAllowed):
            self.b.move(Player.WHITE, 23, 1)

    def test_bear_off_exact_allowed(self):
        self.b.__points__ = [[] for _ in range(24)]
        self.b.__bar__ = {Player.WHITE: [], Player.BLACK: []}
        self.b.__borne__ = {Player.WHITE: [], Player.BLACK: []}

        self.b.__points__[18] = [Checker(Player.WHITE) for _ in range(14)]
        self.b.__points__[23] = [Checker(Player.WHITE)]

        before_borne = len(self.b.__borne__[Player.WHITE])
        self.b.move(Player.WHITE, 23, 1)
        self.assertEqual(len(self.b.__borne__[Player.WHITE]), before_borne + 1)
        self.assertEqual(self.b.count_at(23), 0)

    def test_no_checker_at_point_raises(self):
        empty_idx = 6
        self.b.__points__[empty_idx] = []
        with self.assertRaises(NoCheckerAtPoint):
            self.b.move(Player.WHITE, empty_idx, 1)

    def test_invalid_src_raises(self):
        with self.assertRaises(NoCheckerAtPoint):
            self.b.move(Player.WHITE, -1, 1)
        with self.assertRaises(NoCheckerAtPoint):
            self.b.move(Player.WHITE, 24, 1)

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
    
    def test_is_blocked_for_boundaries_and_rules(self):
        b = Board()
        b.__reset__()
        # fuera de rango → False
        self.assertIs(b.is_blocked_for(Player.WHITE, -1), False)
        self.assertIs(b.is_blocked_for(Player.WHITE, 24), False)
        # bloquear: ponemos 2 negras en un punto
        b.__points__[8] = [Checker(Player.BLACK), Checker(Player.BLACK)]
        self.assertIs(b.is_blocked_for(Player.WHITE, 8), True)
        # 1 sola del rival no bloquea
        b.__points__[9] = [Checker(Player.BLACK)]
        self.assertIs(b.is_blocked_for(Player.WHITE, 9), False)

    def test_entry_index_from_bar(self):
        b = Board()
        self.assertEqual(b.entry_index_from_bar(Player.WHITE, 1), 0)
        self.assertEqual(b.entry_index_from_bar(Player.WHITE, 6), 5)
        self.assertEqual(b.entry_index_from_bar(Player.BLACK, 1), 23)
        self.assertEqual(b.entry_index_from_bar(Player.BLACK, 6), 18)

    def test_dest_index_direction(self):
        b = Board()
        self.assertEqual(b.dest_index(Player.WHITE, 6, 3), 9)   # suma
        self.assertEqual(b.dest_index(Player.BLACK, 20, 4), 16) # resta
if __name__ == "__main__":
    unittest.main()