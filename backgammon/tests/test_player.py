import unittest 
from backgammon.core.player import Player

class TestPlayer(unittest.TestCase):

    def test_value_white_and_black(self): #Chequea que el valor puesto en __value__ es el correcto.
        self.assertEqual(Player.WHITE.__value__, -1)
        self.assertEqual(Player.BLACK.__value__, 1)

    def test_direcction_white_and_black(self):#Chequea que devuelva el correcto sentido de movimiento de cada Player.
        self.assertEqual(Player.WHITE.__direction__(), -1)
        self.assertEqual(Player.BLACK.__direction__(), 1)

    def test_home_range(self):#Chquea que devuelva el valor del rango correcto de cada Player y nos va a servir para mas adelante para comparar directamente si el jugador puede o no sacar sus fichas del tablero.
        self.assertEqual(list(Player.WHITE.__home_range__()), [0, 1, 2, 3, 4, 5])
        self.assertEqual(list(Player.BLACK.__home_range__()), [18, 19, 20, 21, 22, 23])

if __name__ == "__main__":
    unittest.main()