import unittest
from backgammon.core.checker import Checker, CheckerColor
from backgammon.core.player import Player

class TestCheker(unittest.TestCase):
    
    def test_cheker_creation(self): #Chekea de que se creen correctamente las ficahas 
        ficha = Checker(CheckerColor.RED)
        self.assertEqual(str(ficha), "🔴")
    
    def test_cheker_equiality(self):#Chekea el color de las fichas, si son iguales o no
        ficha1 = Checker(CheckerColor.BLUE)
        ficha2 = Checker(CheckerColor.BLUE)
        ficha3 = Checker(CheckerColor.GREEN)

        self.assertEqual(ficha1, ficha2)
        self.assertNotEqual(ficha1, ficha3)
    
    def test_cheker_str_representation(self):
        colores_map = {
          CheckerColor.WHITE: "⚪",
          CheckerColor.BLACK: "⚫",
          CheckerColor.RED: "🔴",
          CheckerColor.BLUE: "🔵",
          CheckerColor.GREEN: "🟢"
        }

        for color, emoji in colores_map.items():
            with self.subTest(color=color):
                ficha = Checker(color)
                self.assertEqual(str(ficha), emoji)
    
class TestCheckerExtra(unittest.TestCase):
    def test_creation_with_player_defaults_color_from_palette(self):
        w = Checker(Player.WHITE)
        self.assertEqual(w.owner, Player.WHITE)
        self.assertEqual(w.color, CheckerColor.WHITE)

        w = Checker(Player.BLACK)
        self.assertEqual(w.owner, Player.BLACK)
        self.assertEqual(w.color, CheckerColor.BLACK)
    
    def test_creation_with_player_and_custom_color(self):
        f = Checker(Player.WHITE, CheckerColor.RED)
        self.assertEqual(f.owner, Player.WHITE)
        self.assertEqual(f.color, CheckerColor.RED)
        self.assertEqual(str(f), "🔴")

    def test_set_color_for_player_affects_future_checkers(self):
        Checker.set_color_for_player(Player.WHITE, CheckerColor.BLUE)
        f = Checker(Player.WHITE)
        self.assertEqual(f.owner, Player.WHITE)
        self.assertEqual(f.color, CheckerColor.BLUE)
        self.assertEqual(str(f), "🔵")
        # limpiar para no afectar otros tests
        Checker.set_color_for_player(Player.WHITE, CheckerColor.WHITE)
    def test_constructor_argument_raises(self):
        with self.assertRaises(ValueError):
            Checker("No es player ni checkercolor")


if __name__ == "__main__":
    unittest.main()