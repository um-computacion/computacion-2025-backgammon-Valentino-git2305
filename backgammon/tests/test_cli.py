# backgammon/tests/test_cli.py
import builtins
import re
import random 
import pytest
from unittest.mock import MagicMock, ANY

import backgammon.core.checker

from backgammon.cli.cli import CLI
from backgammon.core.player import Player
from backgammon.core.checker import Checker, CheckerColor
from backgammon.core.exceptions import (
    GameNotStrated, GameFinished, GameAlredyStarted, DiceAlreadyRolled, DiceNotRolled, PointBlocked,
    NoCheckerAtPoint, NotYourTurn, MustEnterFromBar, EntryBlocked, BearOffNotAllowed
)


# --------------------------
# Helpers
# --------------------------

def _seed_board_for_current(cli: CLI, setup: dict):
    """
    Configura el tablero para el jugador actual.
    """
    b = cli.game.board
    b.__points__ = [[] for _ in range(24)]
    b.__bar__ = {Player.WHITE: [], Player.BLACK: []}
    b.__borne__ = {Player.WHITE: [], Player.BLACK: []}
    
    cur = cli.game.current_player
    opp = Player.BLACK if cur is Player.WHITE else Player.WHITE 
    
    if "points" in setup:
        for idx, count in setup["points"].items():
            b.__points__[idx] = [Checker(cur) for _ in range(count)]
            
    if "opponent_points" in setup:
        for idx, count in setup["opponent_points"].items():
            b.__points__[idx] = [Checker(opp) for _ in range(count)]

    if "bar" in setup:
        b.__bar__[cur] = [Checker(cur) for _ in range(setup["bar"])]
        
    if "borne" in setup:
        b.__borne__[cur] = [Checker(cur) for _ in range(setup["borne"])]


def _setup_and_roll(cli: CLI, monkeypatch, capsys, dice_vals: tuple = (3, 1)):
    """
    Helper para iniciar, sortear y hacer la tirada de turno.
    Usa monkeypatch para controlar random.randint
    """
    # 1. Configurar jugadores
    inputs = iter(["Alice", "Bob", "1"])
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(inputs))
    cli.cmd_setup([])
    
    # 2. Iniciar
    cli.cmd_start([])
    
    # 3. Preparar el mock de random.randint
    # Devuelve 6 y 1 para el sorteo (gana WHITE)
    # Devuelve los dice_vals para la tirada de turno
    dice_sequence = iter([6, 1, dice_vals[0], dice_vals[1]])
    monkeypatch.setattr(random, "randint", lambda a, b: next(dice_sequence))

    # 4. Sorteo (ahora usa el mock de randint)
    cli.cmd_roll([])
    # El game.roll() real se ejecuta y setea el estado
    assert cli.game.current_player is Player.WHITE
    
    # 5. Tirada de turno (usa el mock de randint)
    cli.cmd_roll([])
    # El game.roll() real se ejecuta y setea el estado
    assert cli.game.dice.values == dice_vals

    # 6. Limpiar toda la salida de setup
    capsys.readouterr()
    
    # Sanity check
    assert cli.game.dice.values == dice_vals
    if dice_vals[0] == dice_vals[1]:
        assert cli.remaining_dice == [dice_vals[0]] * 4
    else:
        assert cli.remaining_dice == list(dice_vals)


# --------------------------
# start + setup
# --------------------------

def test_start_llama_setup_si_no_configurado(monkeypatch, capsys):
    cli = CLI()
    inputs = iter(["Alice", "Bob", "1"])
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(inputs))
    cli.cmd_start([])
    out = capsys.readouterr().out
    assert "Configuracion de jugadores" in out
    assert "WHITE: Alice | BLACK: Bob" in out
    assert "Partida iniciada" in out


def test_setup_choice_2_and_invalid(monkeypatch, capsys):
    cli = CLI()
    
    inputs = iter(["Alice", "Bob", "2"])
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(inputs))
    cli.cmd_setup([])
    out = capsys.readouterr().out
    assert "WHITE: Bob | BLACK: Alice" in out
    assert cli.white_name == "Bob"

    inputs = iter(["Charlie", "Dave", "99"])
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(inputs))
    cli.cmd_setup([])
    out = capsys.readouterr().out
    assert "Opción inválida." in out
    assert "WHITE: Charlie | BLACK: Dave" in out


def test_start_already_started(monkeypatch, capsys):
    cli = CLI()
    inputs = iter(["A", "B", "1"])
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(inputs))
    cli.cmd_start([])
    capsys.readouterr() 
    
    with pytest.raises(GameAlredyStarted):
        cli.cmd_start([])


# --------------------------
# roll
# --------------------------

def test_roll_not_started(capsys):
    cli = CLI()
    cli.cmd_roll([])
    out = capsys.readouterr().out
    assert "[ERROR] La partida no está iniciada." in out


def test_roll_sorteo_inicial_muestra_mensaje(monkeypatch, capsys):
    cli = CLI()
    cli._players_configured = True
    cli.game.start()

    dice_sequence = iter([5, 2])
    monkeypatch.setattr(random, "randint", lambda a, b: next(dice_sequence))
    
    cli.cmd_roll([])
    out = capsys.readouterr().out

    assert "Sorteo de inicio: WHITE 5 - BLACK 2" in out
    assert cli.game.current_player is Player.WHITE
    assert cli.remaining_dice == [5, 2] 


def test_roll_en_turno_normal_luego_del_sorteo(monkeypatch, capsys):
    cli = CLI()
    cli._players_configured = True
    cli.game.start()

    dice_sequence = iter([6, 1, 4, 2])
    monkeypatch.setattr(random, "randint", lambda a, b: next(dice_sequence))
    
    cli.cmd_roll([])      
    capsys.readouterr()   
    cli.cmd_roll([])      

    out = capsys.readouterr().out
    assert "Tirada: 4 - 2" in out
    assert cli.remaining_dice == [4, 2]
    assert cli.game.dice.values == (4, 2)


def test_roll_en_turno_normal_dobles(monkeypatch, capsys):
    cli = CLI()
    cli._players_configured = True
    cli.game.start()
    
    dice_sequence = iter([6, 1, 5, 5])
    monkeypatch.setattr(random, "randint", lambda a, b: next(dice_sequence))

    cli.cmd_roll([])      
    capsys.readouterr()
    cli.cmd_roll([])      
    out = capsys.readouterr().out
    
    assert "Tirada: 5 - 5" in out
    assert cli.remaining_dice == [5, 5, 5, 5]
    assert cli.game.dice.values == (5, 5)


def test_roll_repetido_en_el_mismo_turno_avisa(monkeypatch, capsys):
    cli = CLI()
    cli._players_configured = True
    cli.game.start()

    dice_sequence = iter([6, 1, 3, 1])
    monkeypatch.setattr(random, "randint", lambda a, b: next(dice_sequence))
    
    cli.cmd_roll([])  
    capsys.readouterr()
    cli.cmd_roll([])  
    out1 = capsys.readouterr().out

    cli.cmd_roll([])
    out2 = capsys.readouterr().out
    
    assert "Tirada: 3 - 1" in out1
    assert "Ya tiraste los dados en este turno" in out2


# --------------------------
# move
# --------------------------

def test_move_ok_descuenta_dado_y_actualiza_tablero(monkeypatch, capsys):
    cli = CLI()
    
    _setup_and_roll(cli, monkeypatch, capsys, (1, 4))

    cur = cli.game.current_player 
    _seed_board_for_current(cli, {"points": {5: 1}})
    
    cli.cmd_move(["5", "1"])
    out_move = capsys.readouterr().out
    
    assert "Movimiento realizado" in out_move
    assert cli.game.board.count_at(5) == 0
    assert cli.game.board.owner_at(4) is Player.WHITE
    assert cli.remaining_dice == [4]


def test_move_ok_ultimo_dado(monkeypatch, capsys):
    cli = CLI()
    _setup_and_roll(cli, monkeypatch, capsys, (3, 1)) 
    
    cur = cli.game.current_player
    _seed_board_for_current(cli, {"points": {10: 1, 8: 1}})
    
    cli.cmd_move(["10", "3"])
    capsys.readouterr()
    
    cli.cmd_move(["8", "1"])
    out = capsys.readouterr().out
    
    assert "Movimiento realizado" in out
    assert cli.remaining_dice == []
    assert "No te quedan dados este turno — podés usar 'pass'." in out


def test_move_rechazos_basicos(monkeypatch, capsys):
    cli = CLI()

    # 1) no iniciada
    cli.cmd_move(["5", "1"])
    out = capsys.readouterr().out
    assert "no está iniciada" in out

    # 2) iniciada pero sin sorteo
    cli._players_configured = True
    cli.game.start()
    cli.cmd_move(["5", "1"])
    out = capsys.readouterr().out
    assert "Primero resolvé el sorteo inicial" in out

    # 3) con jugador actual pero sin tirar:
    dice_sequence = iter([6, 1])
    monkeypatch.setattr(random, "randint", lambda a, b: next(dice_sequence))
    cli.cmd_roll([])      
    capsys.readouterr()   
    cli.cmd_move(["5", "1"])
    out = capsys.readouterr().out
    assert "Primero tirá los dados" in out

    # 4) sin remaining_dice
    dice_sequence_2 = iter([6, 1, 3, 2])
    monkeypatch.setattr(random, "randint", lambda a, b: next(dice_sequence_2))
    cli.cmd_roll([])      
    cli.cmd_roll([])      
    cli.remaining_dice = [] 
    cli.cmd_move(["5", "1"])
    out = capsys.readouterr().out
    assert "No te quedan dados" in out

    # 5) argumentos inválidos
    cli.remaining_dice = [3]
    cli.cmd_move(["solo_un_arg"])
    out = capsys.readouterr().out
    assert "Uso: move <src|bar> <die>" in out

    cli.cmd_move(["x", "3"]) 
    out = capsys.readouterr().out
    assert "El origen debe ser número" in out

    cli.cmd_move(["5", "n"]) 
    out = capsys.readouterr().out
    assert "El dado debe ser un número entero" in out

    cli.cmd_move(["5", "6"]) 
    out = capsys.readouterr().out
    assert "no coincide con los dados disponibles" in out


def test_move_error_de_logica_usa_handle_error(monkeypatch, capsys):
    cli = CLI()
    _setup_and_roll(cli, monkeypatch, capsys, (3, 1)) 
    
    _seed_board_for_current(cli, {})

    # 1. NoCheckerAtPoint
    cli.cmd_move(["5", "3"])
    out = capsys.readouterr().out
    assert "[ERROR] No hay ficha tuya en el origen" in out

    # 2. PointBlocked
    monkeypatch.setattr(cli.game.board, "move", MagicMock(side_effect=PointBlocked("Test")))
    cli.cmd_move(["5", "3"])
    out = capsys.readouterr().out
    assert "[ERROR] El punto destino está bloqueado." in out

    # 3. MustEnterFromBar
    monkeypatch.setattr(cli.game.board, "move", MagicMock(side_effect=MustEnterFromBar("Test")))
    cli.cmd_move(["5", "3"])
    out = capsys.readouterr().out
    assert "[ERROR] Debés ingresar desde la barra" in out

    # 4. EntryBlocked
    monkeypatch.setattr(cli.game.board, "move", MagicMock(side_effect=EntryBlocked("Test")))
    cli.cmd_move(["bar", "1"])
    out = capsys.readouterr().out
    assert "[ERROR] No podés entrar desde la barra con ese dado (bloqueado)." in out

    # 5. BearOffNotAllowed
    monkeypatch.setattr(cli.game.board, "move", MagicMock(side_effect=BearOffNotAllowed("Test")))
    # FIX: Usar un dado disponible (3 o 1)
    cli.cmd_move(["3", "1"])
    out = capsys.readouterr().out
    assert "[ERROR] No podés retirar fichas todavía." in out
    
    # 6. Excepción genérica
    monkeypatch.setattr(cli.game.board, "move", MagicMock(side_effect=ValueError("Error genérico")))
    cli.cmd_move(["5", "3"])
    out = capsys.readouterr().out
    assert "[ERROR] ValueError: Error genérico" in out


def test_move_from_bar_ok(monkeypatch, capsys):
    cli = CLI()
    _setup_and_roll(cli, monkeypatch, capsys, (3, 1))
    
    _seed_board_for_current(cli, {"bar": 1})
    
    cli.cmd_move(["bar", "3"])
    out = capsys.readouterr().out
    
    assert "Movimiento realizado" in out
    cur = cli.game.current_player 
    dest = 2 
    assert cli.game.board.count_at(dest) == 1
    assert cli.remaining_dice == [1]


def test_move_wins_game(monkeypatch, capsys):
    cli = CLI()
    _setup_and_roll(cli, monkeypatch, capsys, (3, 1)) 
    
    cur = cli.game.current_player 
    src_idx = 0 
    _seed_board_for_current(cli, {"borne": 14, "points": {src_idx: 1}})
    
    cli.cmd_move([str(src_idx), "1"])
    out = capsys.readouterr().out
    
    assert "Movimiento realizado" in out
    assert cli.game.finished is True
    
    winner_name = cli.game.current_player.name 
    assert f"¡¡¡Ganó {winner_name}!!!" in out


# --------------------------
# pass
# --------------------------

def test_pass_requisitos(monkeypatch, capsys):
    cli = CLI()
    _setup_and_roll(cli, monkeypatch, capsys, (3, 1)) 
    
    # 1. Con dados tirados pero aún quedan remaining_dice
    cli.cmd_pass([])
    out = capsys.readouterr().out
    assert "Te faltan usar dados: [3, 1]" in out

    # 2. Sin tirar dados
    cli_new = CLI()
    cli_new._players_configured = True
    cli_new.game.start()
    
    cli_new.cmd_pass([])
    out = capsys.readouterr().out
    assert "Tenés que tirar los dados" in out


def test_pass_ok(monkeypatch, capsys):
    cli = CLI()
    _setup_and_roll(cli, monkeypatch, capsys, (3, 1)) 

    cli.remaining_dice = []  
    cli.cmd_pass([])
    out = capsys.readouterr().out
    
    assert "Turno pasado" in out
    assert cli.game.dice.values == (0, 0)
    assert cli.remaining_dice == []


def test_pass_con_error_de_juego(monkeypatch, capsys):
    cli = CLI()
    _setup_and_roll(cli, monkeypatch, capsys, (3, 1)) 
    cli.remaining_dice = [] 

    monkeypatch.setattr(cli.game, "pass_turn", MagicMock(side_effect=GameFinished("Test")))
    
    cli.cmd_pass([])
    out = capsys.readouterr().out
    assert "[ERROR] La partida ya terminó." in out


# --------------------------
# board / status / help / exit
# --------------------------

def test_board_status_help_exit(monkeypatch, capsys):
    cli = CLI()

    cli.cmd_board([])
    out = capsys.readouterr().out
    assert "PUNTOS 12 → 23" in out

    cli.cmd_status([])
    out = capsys.readouterr().out
    assert "Partida no iniciada" in out

    inputs = iter(["A", "B", "1"])
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(inputs))
    cli.cmd_start([])
    capsys.readouterr() 
    
    cli.cmd_status([])
    out = capsys.readouterr().out
    assert "Partida no iniciada" not in out
    assert "Turno #1" in out 

    cli.cmd_help([])
    out = capsys.readouterr().out
    assert "CLI interactivo para jugar backgammon" in out

    with pytest.raises(SystemExit):
        cli.cmd_exit([])


def test_board_representa_mas_de_9_fichas(monkeypatch, capsys):
    cli = CLI()
    _setup_and_roll(cli, monkeypatch, capsys, (1,1))
    
    cur = cli.game.current_player
    char = "W" if cur is Player.WHITE else "B"
    _seed_board_for_current(cli, {"points": {10: 10}})
    
    cli.cmd_board([])
    out = capsys.readouterr().out
    
    assert f"{char}9" in out
    assert f"{char}10" not in out


# --------------------------
# colors
# --------------------------

def test_cmd_colors_ok(monkeypatch, capsys):
    cli = CLI()
    inputs = iter(["red", "blue"])
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(inputs))
    
    mock_setter = MagicMock()
    monkeypatch.setattr(backgammon.core.checker.Checker, "set_color_for_player", mock_setter)
    
    cli.cmd_colors([])
    out = capsys.readouterr().out
    
    assert "WHITE -> red | BLACK -> blue" in out
    mock_setter.assert_any_call(Player.WHITE, CheckerColor.RED)
    mock_setter.assert_any_call(Player.BLACK, CheckerColor.BLUE)


def test_cmd_colors_invalidos(monkeypatch, capsys):
    cli = CLI()
    
    inputs = iter(["purple", "blue"])
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(inputs))
    cli.cmd_colors([])
    out = capsys.readouterr().out
    assert "Color inválido. Intenta de nuevo." in out

    inputs = iter(["red", ""])
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(inputs))
    cli.cmd_colors([])
    out = capsys.readouterr().out
    assert "Color inválido. Intenta de nuevo." in out


def test_cmd_colors_iguales(monkeypatch, capsys):
    cli = CLI()
    inputs = iter(["green", "green"])
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(inputs))
    
    cli.cmd_colors([])
    out = capsys.readouterr().out
    
    assert "Los colores no pueden ser iguales. Intenta de nuevo." in out


# --------------------------
# run (main loop)
# --------------------------

def test_run_loop_comandos_basicos(monkeypatch, capsys):
    cli = CLI()
    
    inputs = iter([
        "setup", "Alice", "Bob", "1", 
        "status",                     
        "board",                      
        "help",                       
        "colors", "red", "red",     
        "comando_desconocido",        
        "exit"                        
    ])
    
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(inputs))

    with pytest.raises(SystemExit):
        cli.run()

    out = capsys.readouterr().out
    
    assert "Backgammon — escribí 'help' para ver comandos" in out
    assert "WHITE: Alice | BLACK: Bob" in out  # setup
    assert "Partida no iniciada" in out       # status
    assert "PUNTOS 12 → 23" in out            # board
    assert "CLI interactivo" in out           # help
    assert "Los colores no pueden ser iguales" in out # colors
    assert "Comando desconocido: comando_desconocido" in out # else


def test_run_loop_errores_de_entrada(monkeypatch, capsys):
    cli = CLI()
    
    # 1. EOFError
    inputs_eof = iter([])
    def mock_input_eof(prompt=""):
        try:
            return next(inputs_eof)
        except StopIteration:
            raise EOFError
            
    monkeypatch.setattr(builtins, "input", mock_input_eof)
    cli.run()
    out = capsys.readouterr().out
    assert "Backgammon" in out 

    # 2. Línea vacía
    cli = CLI()
    inputs_empty = iter(["", "exit"])
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(inputs_empty))
    with pytest.raises(SystemExit):
        cli.run()
    # No debe imprimir error

    # 3. Error de shlex
    cli = CLI()
    inputs_shlex = iter(['move "unclosed quote', "exit"])
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(inputs_shlex))
    with pytest.raises(SystemExit):
        cli.run()
    out = capsys.readouterr().out
    assert "ERROR|Entrada inválida:" in out