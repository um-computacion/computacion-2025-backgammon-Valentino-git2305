import unittest
from backgammon.core.checker import Checker, CheckerColor

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

if __name__ == "__main__":
    unittest.main()