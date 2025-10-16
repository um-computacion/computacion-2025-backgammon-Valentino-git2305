import unittest
import random
from backgammon.core.dice import Dice


class TestDice (unittest.TestCase):
    def test_intial_state(self):
        """Verifica el estado inicial de los dados"""
        d=Dice()
        self.assertEqual(d.values, (0, 0))
        self.assertEqual(str(d), "Falta tirar")
        self.assertFalse(d.is_double())

    def test_roll_generates_valid_values(self):
        """Comprueba que roll() genere valores entre el 1 y el 6"""
        d = Dice()
        vals = d.roll()
        #Nos devuelve lista de dos enteros entre el 1 y el 6
        self.assertIsInstance(vals, list)
        self.assertEqual(len(vals), 2)
        self.assertTrue(all(1 <= v <= 6 for v in vals))
        #property values expone la tupla y coincide con el estado
        self.assertEqual(d.values, tuple(vals))
        self.assertIsInstance(d.values, tuple)
    
    def test_is_double_detection(self):
        """Verfica que is_double detecte correctamente un doble"""
        d = Dice()
        d.__values__= [3, 3]
        self.assertTrue(d.is_double())
        d.__values__ = [2, 5]
        self.assertFalse(d.is_double())
        d.__values__ = [0, 0]
        self.assertFalse(d.is_double())
    
    def test_str_representation(self):
        """Comprueba la presentacion de los textos"""
        d = Dice()
        d.__values__ = [4, 2]
        self.assertEqual(str(d), "4 - 2")
        d.__values__ = [6, 6]
        self.assertEqual(str(d), "6 - 6 (doble)")
    
    def test_reset(self):
        """Verifica que el reset() resetee los valores correctamente """
        d=Dice()
        d.__values____ = [5, 2]
        d.reset()
        self.assertEqual(d.values, (0, 0))
        self.assertEqual(str(d), "Falta tirar")
        self.assertFalse(d. is_double())


if __name__ == "__main__":
    unittest.main()
                         