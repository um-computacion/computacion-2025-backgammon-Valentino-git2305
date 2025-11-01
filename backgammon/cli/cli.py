import shlex
from typing import List, Optional
from backgammon.core.game import Game
from backgammon.core.player import Player
from backgammon.core.checker import CheckerColor
from backgammon.core.checker import Checker
from backgammon.core.exceptions import (
    GameNotStrated, GameFinished, GameAlredyStarted, DiceAlreadyRolled, DiceNotRolled, PointBlocked,
      NoCheckerAtPoint, NotYourTurn, MustEnterFromBar, EntryBlocked, BearOffNotAllowed
)

class CLI:
    """
    CLI interactivo para jugar backgammon
    Los comandos:
    start   ---->Inicia una nueva partida
    roll    ---->Tira los dados
    move    ---->Mueve una ficha
    pass    ---->Pasa el turno
    board   ---->Muestra el tablero
    status  ---->Estado resumido
    help    ---->Ayuda
    exit    ---->Salir
    """
    PROMPT = "backgammon>"

    def __init__(self) -> None:
        self.game = Game()
        self.white_name = "WHITE"
        self.black_name = "BLACK"
        self._players_configured = False
        self.remaining_dice = []

    def cmd_setup(self, args: List[str]) -> None:
        """
        Configuracion incial de quien sera WHITE y BLACK con nombres
        """
        print("---Configuracion de jugadores---")
        name1 = input("Jugador 1 - nombre: ").strip() or "Jugador 1"
        name2 = input("Jugador 2 - nombre: ").strip() or "Jugador 2"

        choice = input(f"¿Quien juega con WHITE? (1 para {name1}, 2 para {name2}): ").strip()
        if choice == "1":
            white_name, black_name = name1, name2
        elif choice == "2":
            white_name, black_name = name2, name1
        else:
           print("Opción inválida. Usando por defecto: Jugador 1 = WHITE, Jugador 2 = BLACK")
           white_name, black_name = name1, name2
        
        self.game.setup_players(white_name, black_name)
        self.white_name, self.black_name = white_name, black_name
        self._players_configured = True

        self.game.setup_players(white_name, black_name)
        print(f"WHITE: {white_name} | BLACK: {black_name}")

    def _print_board(self) -> None:
        print(self._board_ascii())
    
    def _print_status(self) -> None:
        print(str(self.game))

    def _checker_cell(self, idx: int) -> str:
        """
        Devuelve un token corto para la casilla idx:
        - ".." vacío
        - "Wn" o "Bn" según dueño y cantidad (tope 9 para vista compacta)
        """
        owner = self.game.board.owner_at(idx)
        if owner is None:
            return ".."
        ch = "W" if owner is Player.WHITE else "B"
        n = self.game.board.count_at(idx)
        n = n if n <= 9 else 9
        return f"{ch}{n}"

    def _board_ascii(self) -> str:
       board = self.game.board

       def cell(i: int) -> str:
           owner = board.owner_at(i)   # debe existir en Board (abajo te muestro cómo si no lo tenés)
           if owner is None:
               return ".."
           ch = "W" if owner is Player.WHITE else "B"
           n = board.count_at(i)
           n = n if n <= 9 else 9
           return f"{ch}{n}"

       top_idx = list(range(12, 24))         # 12..23
       bot_idx = list(range(11, -1, -1))     # 11..0

       idx_top_line = " ".join(f"{i:>2}" for i in top_idx)
       idx_bot_line = " ".join(f"{i:>2}" for i in bot_idx)

       top_line = " ".join(f"{cell(i):>2}" for i in top_idx)
       bot_line = " ".join(f"{cell(i):>2}" for i in bot_idx)

       bar_w = len(board.__bar__[Player.WHITE])
       bar_b = len(board.__bar__[Player.BLACK])
       borne_w = len(board.__borne__[Player.WHITE])
       borne_b = len(board.__borne__[Player.BLACK])

       sep = "-" * max(len(top_line), 40)

       lines = []
       lines.append("      PUNTOS 12 → 23")
       lines.append("      " + idx_top_line)
       lines.append("      " + top_line)
       lines.append(sep)
       lines.append(f"BAR   | WHITE:{bar_w}  BLACK:{bar_b}")
       lines.append(f"BORNE | WHITE:{borne_w} BLACK:{borne_b}")
       lines.append(sep)
       lines.append("      PUNTOS 11 → 0")
       lines.append("      " + idx_bot_line)
       lines.append("      " + bot_line)

       return "\n".join(lines)


    
    def _handle_error(self, exc: Exception) -> None:
        msg_map = {
        GameNotStrated:    "La partida no está iniciada. Usá 'start'.",
        GameFinished:      "La partida ya terminó.",
        GameAlredyStarted: "La partida ya está iniciada.",
        DiceAlreadyRolled: "Ya tiraste los dados en este turno.",
        DiceNotRolled:     "Tenés que tirar los dados antes de pasar el turno.",
        PointBlocked:      "El punto destino está bloqueado.",
        NoCheckerAtPoint:  "No hay ficha tuya en el origen.",
        MustEnterFromBar:  "Debés ingresar desde la barra antes de mover otras fichas.",
        EntryBlocked:      "No podés entrar desde la barra con ese dado (bloqueado).",
        BearOffNotAllowed: "No podés retirar fichas todavía.",
        }
        for etype, msg in msg_map.items():
             if isinstance(exc, etype):
                 print(f"[ERROR] {msg}")
                 return
        print(f"[ERROR] {exc.__class__.__name__}: {exc}")

    #Comandos:
    
    def cmd_start(self, args: List[str]) -> None:
        if not self._players_configured:
            print("Primero hay que configurar los jugadores")
            self.cmd_setup([])
        self.game.start()
        self.remaining_dice = []
        print("Partida iniciada")
        print("Ahora usa roll para hacer el sorteo unicial")
        self._print_board()
        self._print_status()

    def cmd_roll(self, args: List[str]) -> None:
        if self.game.dice.values != (0, 0) and self.game.current_player is not None:
            print("Ya tiraste los dados en este turno. Usá 'move' o 'pass'.")
            return
        is_draw_roll = (self.game.current_player is None)
        try:
            vals = self.game.roll()
            if is_draw_roll:
                print(f"Sorteo de inicio: WHITE {vals[0]} - BLACK {vals[1]}")
            else:
                print(f"Tirada: {vals[0]} - {vals[1]}")
            self.remaining_dice = [vals[0], vals[1]] if vals[0] != vals[1] else [vals[0]] * 4
            self._print_status()
            self._print_board()
        except Exception as exc:
            self._handle_error(exc) 

    def cmd_move(self, args: List[str]) -> None:
        if not self.game.started:
            print("La partida no está iniciada. Usá 'start'.")
            return
        if self.game.current_player is None:
            print("Primero resolvé el sorteo inicial con 'roll'.")
            return
        if self.game.dice.values == (0, 0):
            print("Primero tirá los dados con 'roll'.")
            return
        if not self.remaining_dice:
            print("No te quedan dados este turno — usá 'pass'.")
            return
        if len(args) != 2:
            print("Uso: move <src|bar> <die>")
            print("Ejemplos: 'move 12 3'  |  'move bar 5'")
            return
        src_token, die_token = args
        if src_token.lower() == "bar":
            src = None
        else:
            try:
                src = int(src_token)
            except ValueError:
                print("El origen debe ser número (0..23) o 'bar'.")
                return
        try:
            die = int(die_token)
        except ValueError:
            print("El dado debe ser un número entero (1..6).")
            return
        if die not in self.remaining_dice:
            print(f"[ERROR] Ese valor ({die}) no coincide con los dados disponibles {self.remaining_dice}.")
            return
        try:
            self.game.board.move(self.game.current_player, src, die)
            print("Movimiento realizado")
            try:
                self.remaining_dice.remove(die)
            except ValueError:
                pass  
            self._print_board()
            self._print_status()
            self.game.check_game_over()
            if self.game.finished:
                print(f"¡¡¡Ganó {self.game.winner.name}!!!")
            elif not self.remaining_dice:
                print("No te quedan dados este turno — podés usar 'pass'.")
        except Exception as exc:
            self._handle_error(exc)

    def cmd_pass(self, args: List[str]) -> None:
        if self.game.dice.values == (0, 0):
            print("[ERROR] Tenés que tirar los dados antes de pasar el turno.")
            return
        if self.remaining_dice:
            print(f"[ERROR] Te faltan usar dados: {self.remaining_dice}.")
            return
        try:
            self.game.pass_turn()
            self.remaining_dice = []
            print("Turno pasado")
            self._print_board()
            self._print_status()
        except Exception as exc:
            self._handle_error(exc)

    def cmd_board(self, args: List[str]) -> None:
        self._print_board()

    def cmd_status(self, args: List[str]) -> None:
        self._print_status()
    
    def cmd_help(self, args: List[str]) -> None:
        print(self.__class__.__doc__)
    
    def cmd_exit(self, args: List[str]) -> None:
        raise SystemExit(0)
    
    def run(self) -> None:
        print("Backgammon — escribí 'help' para ver comandos")
        while True:
            try:
                line = input(self.PROMPT)
            except EOFError:
                print()
                break
            if not line.strip():
                continue
            try:
                tokens = shlex.split(line)
            except ValueError as e:
                print(f"ERROR|Entrada inválida: {e}")
                continue
            cmd, *args = tokens
            cmd = cmd.lower()

            try:
                if cmd == "start":
                    self.cmd_start(args)
                elif cmd == "roll":
                    self.cmd_roll(args)
                elif cmd == "move":
                    self.cmd_move(args)
                elif cmd == "pass":
                    self.cmd_pass(args)
                elif cmd == "board":
                    self.cmd_board(args)
                elif cmd == "status":
                    self.cmd_status(args)
                elif cmd == "help":
                    self.cmd_help(args)
                elif cmd == "exit":
                    self.cmd_exit(args)
                elif cmd == "setup":
                    self.cmd_setup(args)
                elif cmd == "colors":
                    self.cmd_colors(args)   
                else:
                    print(f"Comando desconocido: {cmd}. Escribí 'help' para ver los comandos.")
            except Exception as exc:
                self._handle_error(exc)

    def _parse_checker_color(self, s: str) -> CheckerColor | None:
        s = (s or "").strip().lower()
        mapping = {
            "white": CheckerColor.WHITE,
            "black": CheckerColor.BLACK,
            "red":   CheckerColor.RED,
            "blue":  CheckerColor.BLUE,
            "green": CheckerColor.GREEN,
        }
        return mapping.get(s)

    def cmd_colors(self, args: List[str]) -> None:
    
        print("=== Colores de fichas ===")
        print("Disponibles: white, black, red, blue, green")

        col_white = self._parse_checker_color(input("Color para WHITE: "))
        col_black = self._parse_checker_color(input("Color para BLACK: "))

        if not col_white or not col_black:
           print("Color inválido. Intenta de nuevo.")
           return
        if col_white == col_black:
           print("Los colores no pueden ser iguales. Intenta de nuevo.")
           return

        Checker.set_color_for_player(Player.WHITE, col_white)
        Checker.set_color_for_player(Player.BLACK, col_black)

        print(f"WHITE -> {col_white.name.lower()} | BLACK -> {col_black.name.lower()}")    

def run() -> None:
    CLI().run()