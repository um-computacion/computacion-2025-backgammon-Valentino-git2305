import unittest

from backgammon.core.game import Game
from backgammon.core.player import Player
from backgammon.core.checker import Checker
from backgammon.core.exceptions import (GameNotStrated, GameAlredyStarted, GameFinished, DiceAlreadyRolled, DiceNotRolled)
from unittest.mock import patch

class TesteGame(unittest.TestCase):
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
        self.assertIsNone(g.current_player)
        self.assertEqual(g.turn_count, 1)
        self.assertEqual(str(g.dice), "Falta tirar")

    def test_roll_requires_started(self):
        g = Game()
        with self.assertRaises(GameNotStrated):
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
    
    def test_start_sets_current_player_and_prevents_restart(self):
        g = Game()
        with patch("backgammon.core.game.random.randint", side_effect=[6, 1]):
            g.start()
            g.roll() 
        assert g.started is True
        assert g.current_player in (Player.WHITE, Player.BLACK)
        with self.assertRaises(GameAlredyStarted):
            g.start()

    
    def test_roll_requires_started_and_prevents_double_roll(self):
        g = Game()
        with self.assertRaises(GameNotStrated):
            g.roll()
        with patch("backgammon.core.game.random.randint", side_effect=[6, 1]):
            g.start()
        with self.assertRaises(DiceNotRolled):
            g.pass_turn()

    def test_roll_raises_if_game_finished(self):
        g = Game()
        with patch("backgammon.core.game.random.randint", side_effect=[6, 1]):
            g.start()
        g.board.__borne__[Player.WHITE] = [object()] * 15
        g.check_game_over()
        self.assertTrue(g.finished)
        with self.assertRaises(GameFinished):
            g.roll()

    def test_pass_turn_requires_started_and_rolled_dice(self):
        g = Game()
        with self.assertRaises(GameNotStrated):
            g.pass_turn()
        with patch("backgammon.core.game.random.randint", side_effect=[6, 1]):
            g.start()
        with self.assertRaises(DiceNotRolled):
            g.pass_turn()

    def test_pass_turn_switches_player_and_resets_dice(self):
        g = Game()
        with patch("backgammon.core.game.random.randint", side_effect=[6, 1]):
            g.start()
        first = g.current_player
        g.dice.__values__ = [4, 3]
        g.pass_turn()
        self.assertNotEqual(g.current_player, first)
        self.assertEqual(g.turn_count, 2)
        self.assertEqual(g.dice.values, (0, 0))
    
    def test_pass_turn_requires_dice_rolled(self):
        g = Game()
        g.start()
        with self.assertRaises(DiceNotRolled):
            g.pass_turn()

    def test_str_shows_winner_when_game_over(self):
        g = Game()
        with patch("backgammon.core.game.random.randint", side_effect=[6, 1]):
            g.start()
        g.board.__borne__[Player.WHITE] = [object()] * 15
        g.check_game_over()
        s = str(g)
        self.assertIn("Ganador", s)
        self.assertIn("WHITE", s)

    def test_start_tie_then_black_starts(self):
        g = Game()
        with patch("backgammon.core.game.random.randint", side_effect=[3, 3, 1, 6]):
            g.start()
            g.roll()
        self.assertTrue(g.started)
        self.assertEqual(g.current_player, Player.BLACK)


    def test_strat_again_raises(self):
        g = Game()
        with patch("backgammon.core.game.random.randint", side_effect=[6, 1]):
            g.start()
        with self.assertRaises(GameAlredyStarted):
            g.start()
        
    def test_str_shows_winner_black(self):
        g = Game()
        with patch("backgammon.core.game.random.randint", side_effect=[6, 1]):
            g.start()  
        g.board.__borne__[Player.BLACK] = [Checker(Player.BLACK) for _ in range(15)]
        g.check_game_over()
        s = str(g)
        self.assertIn("Ganador", s)
        self.assertIn("BLACK", s)
    
    def test_history_has_start_and_roll(self):
        g = Game()
        with patch("backgammon.core.game.random.randint", side_effect=[6, 1, 4, 2]):
            g.start()
            g.roll() 
        self.assertTrue(any("Game: Start" in h for h in g.history()))
        g.roll() 
        self.assertTrue(any(" roll:" in h for h in g.history()))

        
    def test_roll_twice_raises_dice_already_rolled(self):
        g = Game()
        with patch("backgammon.core.game.random.randint", side_effect=[6, 1]):
            g.start()
        g.__finished__ = True
        g.__dice__.reset()
        current = g.current_player
        turns = g.turn_count
        try:
            g.pass_turn()
        except Exception as e:
            self.fail(f"pass_turn no debe lanzar si finished lanzo {e}")
        assert g.current_player == current
        assert g.turn_count == turns
        assert g.dice.values == (0, 0)

    def test_start_sets_white_when_white_is_higher(self):
        g = Game()
        with patch("backgammon.core.game.random.randint", side_effect=[6, 1]):
            g.start()
            g.roll()
        assert g.current_player == Player.WHITE


    def test_str_shows_winner_white(self):
        g = Game()
        with patch("backgammon.core.game.random.randint", side_effect=[6, 1]):
            g.start()
        g.board.__borne__[Player.WHITE] = [object()] * 15
        g.check_game_over()
        s = str(g)
        assert "Ganador" in s and "WHITE" in s  

    def test_roll_opening_draw_resolves_correctly(self):
        """El sorteo inicial debe repetirse si hay empate y resolver correctamente."""
        from unittest.mock import patch

        g = Game()
        with patch("backgammon.core.game.random.randint", side_effect=[3, 3, 5, 2]):
            g.start()
            vals = g.roll()
            self.assertEqual(vals, [5, 2])
            self.assertEqual(g.current_player, Player.WHITE)

    def test_pass_turn_switches_player_and_resets_dice(self):
        """Al pasar turno, el jugador debe alternar y los dados reiniciarse."""
        from unittest.mock import patch
        g = Game()
        with patch("backgammon.core.game.random.randint", side_effect=[6, 1]):
            g.start()
            g.roll()
        with patch("backgammon.core.game.random.randint", side_effect=[4, 2]):
            g.roll()
        first = g.current_player
        g.pass_turn()
        self.assertNotEqual(g.current_player, first)
        self.assertEqual(g.dice.values, (0, 0))

    def test_roll_twice_in_same_turn_raises(self):
        # Arranco y hago sorteo; luego tiro dados del turno y reintento tirar
        with patch("backgammon.core.game.random.randint", side_effect=[6, 1]):
            g = Game()
            g.start()
            g.roll()  # sorteo inicial resuelto

        with patch("backgammon.core.game.random.randint", side_effect=[4, 2]):
            vals = g.roll()
            self.assertEqual(len(vals), 2)

        # Reintentar tirar en el mismo turno debe fallar
        with self.assertRaises(DiceAlreadyRolled):
            g.roll()

    def test_pass_turn_when_finished_is_noop(self):
        # Termino el juego y luego pass_turn no debe cambiar nada
        with patch("backgammon.core.game.random.randint", side_effect=[6, 1]):
            g = Game()
            g.start()
            # simulamos fin de juego
            g.board.__borne__[Player.WHITE] = [Checker(Player.WHITE) for _ in range(15)]
            g.check_game_over()
            self.assertTrue(g.finished)
            current = g.current_player
            turn = g.turn_count
            dice = g.dice.values

            # no debe explotar ni cambiar estado relevante
            g.pass_turn()
            self.assertEqual(g.current_player, current)
            self.assertEqual(g.turn_count, turn)
            self.assertEqual(g.dice.values, dice)

    def test_setup_players_and_get_player_name(self):
        g = Game()
        g.setup_players("Val", "Non")
        # Antes de start() get_player_name ya debe mapear
        self.assertEqual(g.get_player_name(Player.WHITE), "Val")
        self.assertEqual(g.get_player_name(Player.BLACK), "Non")

        # Si pido un player no mapeado (improbable), devuelve el enum name
        # Simulamos borrando el dict para una clave
        g.__players_info__.pop("WHITE", None)
        self.assertEqual(g.get_player_name(Player.WHITE), "WHITE")

    def test_str_shows_waiting_draw(self):
        g = Game()
        g.start()
        s = str(g)
        self.assertIn("Turno #1", s)
        self.assertIn("falta sorteo", s)  # "Juega: — (falta sorteo)"


if __name__ == "__main__":
    unittest.main()
        