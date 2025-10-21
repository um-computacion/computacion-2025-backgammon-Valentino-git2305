import unittest

from backgammon.core.game import Game
from backgammon.core.player import Player
from backgammon.core.checker import Checker

class TasteGame(unittest.TestCase):
    def test_reset_pre_start_state(self):
        g = Game()
        g.reset()
        self.assertFalse(g.started)
        self.assertFalse(g.finished)
        self.assertIsNone(g.current_player)
        self.assertEqual(g.turn_count, 0)
        self.assertEqual(str(g.dice), "Falta tirar")

    def test_strart_sets_initial_state_and_current_player(self):
        g = Game()
        g.start()
        self.assertTrue(g.started)
        self.assertFalse(g.finished)
        self.assertIn(g.current_player, (Player.WHITE, Player.BLACK))
        self.assertEqual(g.turn_count, 1)
        self.assertEqual(str(g.dice), "Falta tirar")

    def test_roll_requires_started(self):
        g = Game()
        with self.assertRaises(ValueError):
            g.roll()
        g.start()
        vals = g.roll()
        self.assertIsInstance(vals, list)
        self.assertEqual(len(vals), 2)
        self.assertTrue(all(1 <= v  <= 6 for v in vals))

    def test_pass_turn_alternates_and_resets_dice(self):
        g = Game()
        g.start()
        first_player = g.current_player
        g.dice.__values__ = [3, 4]
        g.pass_turn()
        self.assertNotEqual(g.current_player, first_player)
        self.assertEqual(g.turn_count, 2)
        self.assertEqual(str(g.dice), "Falta tirar")

    def test_check_game_over_sets_winner_and_finished(self):
        g = Game()
        g.start()
        g.board.__borne__[Player.WHITE] = [Checker(Player.WHITE) for _ in range(15)]
        g.check_game_over()
        self.assertTrue(g.finished)
        self.assertEqual(g.winner, Player.WHITE)

    def test_str_representation(self):
        g = Game()
        self.assertIn("Partida no iniciada", str(g))
        g.start()
        s = str(g)
        self.assertIn("Turno #1" , s)
        self.assertIn("Juega:", s)
        self.assertIn("Dados", s)

    def test_history_return_copy(self):
        g = Game()
        g.start()
        h1 = g.history()
        h1.append("No deberia afectar")
        self.assertNotEqual(g.history()[-1], "No deberia afectar")

if __name__ == "__main__":
    unittest.main()
        