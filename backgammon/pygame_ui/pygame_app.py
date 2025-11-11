# backgammon/pygame_ui/pygame_app.py
import sys
from typing import Optional, Tuple, List

import pygame

from backgammon.core.game import Game
from backgammon.core.player import Player
from backgammon.core.exceptions import (
    GameNotStrated,
    GameFinished,
    GameAlredyStarted,
    DiceAlreadyRolled,
    DiceNotRolled,
    PointBlocked,
    NoCheckerAtPoint,
    MustEnterFromBar,
    EntryBlocked,
    BearOffNotAllowed,
)

# ====== Paleta ======
BG = (18, 18, 22)
FELT = (24, 86, 64)
WOOD = (145, 104, 63)
WOOD_DARK = (115, 80, 48)
IVORY = (235, 235, 235)
INK = (24, 24, 28)
GOLD = (235, 200, 120)
RED = (210, 70, 70)
GREEN = (70, 180, 110)

WHITE_CHK = (240, 240, 240)
BLACK_CHK = (28, 28, 30)

# ====== Dimensiones ======
W, H = 1280, 720
BOARD_MARGIN = 30
PANEL_W = 300
BOARD_W = W - PANEL_W - 2 * BOARD_MARGIN
BOARD_H = H - 2 * BOARD_MARGIN

POINTS_PER_SIDE = 12
POINT_W = BOARD_W // POINTS_PER_SIDE
POINT_H = BOARD_H // 2
CHECKER_R = int(min(POINT_W, POINT_H) * 0.35)

FONT_NAME = None  # default system font


def _triangle(surface, color, p1, p2, p3):
    pygame.draw.polygon(surface, color, (p1, p2, p3))


class Toast:
    """Mensajes flotantes en esquina inferior izquierda."""

    def __init__(self, font):
        self._font = font
        self._msgs: List[Tuple[str, Tuple[int, int, int], int]] = []  # (txt, color, frames)

    def push(self, text: str, color: Tuple[int, int, int] = GOLD, frames: int = 180):
        self._msgs.append((text, color, frames))

    def draw(self, screen):
        if not self._msgs:
            return
        txt, col, frames = self._msgs[0]
        surf = self._font.render(txt, True, col)
        screen.blit(surf, (BOARD_MARGIN, H - BOARD_MARGIN - surf.get_height() - 4))
        self._msgs[0] = (txt, col, frames - 1)
        if frames - 1 <= 0:
            self._msgs.pop(0)


class PygameUI:
    """
    Pygame UI del Backgammon

    Teclas:
      S → start
      R → roll (sorteo inicial o turno)
      P → pass (si ya tiraste)
      ESC → salir

    Mouse:
      Click izq en un punto propio o BAR para origen.
      Luego 1 / 2 / 3 para usar dado A / dado B / A+B.
    """

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Backgammon — Pygame UI")
        self.__screen__ = pygame.display.set_mode((W, H))
        self.__clock__ = pygame.time.Clock()
        self.__font__ = pygame.font.Font(FONT_NAME, 20)
        self.__font_small__ = pygame.font.Font(FONT_NAME, 16)
        self.__font_big__ = pygame.font.Font(FONT_NAME, 28)

        # Core
        self.__game__ = Game()

        # Pantalla de setup
        self.setup_done = False
        self.player1_name = ""
        self.player2_name = ""
        self.player1_color: Optional[Player] = None  # WHITE / BLACK
        self.active_input = 0                       # 0 = nombre1, 1 = nombre2
        self.color_selected = False

        # Estado UI (IMPORTANTE: inicializado aquí, no en handlers)
        self.__selected_src__: Optional[int] = None   # -1 => BAR
        self.__pending_dist__: Optional[int] = None
        self.__toast__ = Toast(self.__font__)
        self.__top_rects__: List[pygame.Rect] = []
        self.__bot_rects__: List[pygame.Rect] = []
        self.__bar_rect__: pygame.Rect
        self.__borne_rect__: pygame.Rect
        self._compute_layout()

        # Debug: pinta índices de puntos
        self.debug_mode = False

    # ---------- Layout ----------
    def _compute_layout(self):
        board_rect = pygame.Rect(BOARD_MARGIN, BOARD_MARGIN, BOARD_W, BOARD_H)
        self.__top_rects__.clear()
        for i in range(POINTS_PER_SIDE):
            r = pygame.Rect(board_rect.x + i * POINT_W, board_rect.y, POINT_W, POINT_H)
            self.__top_rects__.append(r)
        self.__bot_rects__.clear()
        for i in range(POINTS_PER_SIDE):
            r = pygame.Rect(board_rect.x + i * POINT_W, board_rect.y + POINT_H, POINT_W, POINT_H)
            self.__bot_rects__.append(r)

        # Panel derecho
        self.__bar_rect__ = pygame.Rect(W - PANEL_W + 20, BOARD_MARGIN + 160, PANEL_W - 40, 50)
        self.__borne_rect__ = pygame.Rect(W - PANEL_W + 20, BOARD_MARGIN + 220, PANEL_W - 40, 50)

    def _point_from_pos(self, pos: Tuple[int, int]) -> Optional[int]:
        x, y = pos
        # Arriba: 12..23 (izq→der)
        for i, r in enumerate(self.__top_rects__):
            if r.collidepoint(x, y):
                return 12 + i
        # Abajo: 11..0 (izq→der)
        for i, r in enumerate(self.__bot_rects__):
            if r.collidepoint(x, y):
                return 11 - i
        return None

    # ---------- Setup (pantalla inicial) ----------
    def _draw_setup_screen(self):
        self.__screen__.fill(INK)

        title = self.__font_big__.render("CONFIGURACIÓN DE JUGADORES", True, GOLD)
        self.__screen__.blit(title, title.get_rect(centerx=W // 2, y=50))

        input_w, input_h = 300, 40
        input1_rect = pygame.Rect((W - input_w) // 2, 150, input_w, input_h)
        input2_rect = pygame.Rect((W - input_w) // 2, 250, input_w, input_h)

        pygame.draw.rect(self.__screen__, WOOD_DARK, input1_rect, border_radius=6)
        pygame.draw.rect(self.__screen__, WOOD_DARK, input2_rect, border_radius=6)

        pygame.draw.rect(self.__screen__, GOLD if self.active_input == 0 else FELT, input1_rect, 2, border_radius=6)
        pygame.draw.rect(self.__screen__, GOLD if self.active_input == 1 else FELT, input2_rect, 2, border_radius=6)

        name1 = self.player1_name + ('|' if self.active_input == 0 else '')
        name2 = self.player2_name + ('|' if self.active_input == 1 else '')
        self.__screen__.blit(self.__font__.render(name1, True, IVORY), self.__font__.render(name1, True, IVORY).get_rect(center=input1_rect.center))
        self.__screen__.blit(self.__font__.render(name2, True, IVORY), self.__font__.render(name2, True, IVORY).get_rect(center=input2_rect.center))

        self.__screen__.blit(self.__font__.render("Nombre Jugador 1:", True, IVORY), (input1_rect.x, input1_rect.y - 30))
        self.__screen__.blit(self.__font__.render("Nombre Jugador 2:", True, IVORY), (input2_rect.x, input2_rect.y - 30))

        if self.player1_name and self.player2_name and not self.color_selected:
            q = self.__font__.render(f"¿{self.player1_name} juega con blancas o negras?", True, GOLD)
            self.__screen__.blit(q, q.get_rect(centerx=W // 2, y=350))

            button_w, button_h = 120, 40
            self.white_button = pygame.Rect((W - 2 * button_w - 20) // 2, 400, button_w, button_h)
            self.black_button = pygame.Rect(self.white_button.right + 20, 400, button_w, button_h)

            pygame.draw.rect(self.__screen__, WHITE_CHK, self.white_button, border_radius=6)
            pygame.draw.rect(self.__screen__, BLACK_CHK, self.black_button, border_radius=6)
            self.__screen__.blit(self.__font_small__.render("BLANCAS", True, INK),
                                 self.__font_small__.render("BLANCAS", True, INK).get_rect(center=self.white_button.center))
            self.__screen__.blit(self.__font_small__.render("NEGRAS", True, IVORY),
                                 self.__font_small__.render("NEGRAS", True, IVORY).get_rect(center=self.black_button.center))

        if self.color_selected:
            c1 = "blancas" if self.player1_color == Player.WHITE else "negras"
            c2 = "negras" if self.player1_color == Player.WHITE else "blancas"
            lines = [
                f"{self.player1_name} jugará con fichas {c1}",
                f"{self.player2_name} jugará con fichas {c2}",
                "",
                "ENTER para comenzar"
            ]
            y = 350
            for t in lines:
                surf = self.__font__.render(t, True, GOLD)
                self.__screen__.blit(surf, surf.get_rect(centerx=W // 2, y=y))
                y += 30

    def _handle_setup_events(self, event: pygame.event.Event):
        input_w, input_h = 300, 40
        input1_rect = pygame.Rect((W - input_w) // 2, 150, input_w, input_h)
        input2_rect = pygame.Rect((W - input_w) // 2, 250, input_w, input_h)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if input1_rect.collidepoint(event.pos):
                self.active_input = 0
            elif input2_rect.collidepoint(event.pos):
                self.active_input = 1

            if hasattr(self, "white_button") and hasattr(self, "black_button"):
                if self.white_button.collidepoint(event.pos):
                    self.player1_color = Player.WHITE
                    self.color_selected = True
                elif self.black_button.collidepoint(event.pos):
                    self.player1_color = Player.BLACK
                    self.color_selected = True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.active_input = (self.active_input + 1) % 2
            elif event.key == pygame.K_RETURN:
                if self.color_selected:
                    # Configurar players en Game con el color elegido para p1
                    if self.player1_color == Player.WHITE:
                        self.__game__.setup_players(self.player1_name or "Jugador 1",
                                                    self.player2_name or "Jugador 2")
                    else:
                        self.__game__.setup_players(self.player2_name or "Jugador 2",
                                                    self.player1_name or "Jugador 1")
                    self.setup_done = True
            elif event.key == pygame.K_BACKSPACE:
                if self.active_input == 0:
                    self.player1_name = self.player1_name[:-1]
                else:
                    self.player2_name = self.player2_name[:-1]
            else:
                if event.unicode and event.unicode.isprintable():
                    if self.active_input == 0:
                        self.player1_name += event.unicode
                    else:
                        self.player2_name += event.unicode

    # ---------- Dibujo del tablero ----------
    def _draw_board(self):
        self.__screen__.fill(BG)

        board_rect = pygame.Rect(BOARD_MARGIN, BOARD_MARGIN, BOARD_W, BOARD_H)
        pygame.draw.rect(self.__screen__, FELT, board_rect, border_radius=8)

        alt1, alt2 = WOOD, WOOD_DARK
        for i, r in enumerate(self.__top_rects__):
            c = alt1 if i % 2 == 0 else alt2
            _triangle(self.__screen__, c, (r.x, r.bottom), (r.centerx, r.top + 10), (r.right, r.bottom))
        for i, r in enumerate(self.__bot_rects__):
            c = alt2 if i % 2 == 0 else alt1
            _triangle(self.__screen__, c, (r.x, r.top), (r.centerx, r.bottom - 10), (r.right, r.top))

        # Panel lateral
        panel = pygame.Rect(W - PANEL_W, 0, PANEL_W, H)
        pygame.draw.rect(self.__screen__, INK, panel)

        # Cabecera panel
        title_rect = pygame.Rect(W - PANEL_W + 10, 10, PANEL_W - 20, 40)
        pygame.draw.rect(self.__screen__, WOOD_DARK, title_rect, border_radius=8)
        title = self.__font_big__.render("BACKGAMMON", True, GOLD)
        self.__screen__.blit(title, title.get_rect(center=title_rect.center))

        # Controles
        y = 70
        controls = [("S", "Iniciar juego"), ("R", "Tirar dados"), ("P", "Pasar turno"), ("ESC", "Salir")]
        for key, desc in controls:
            key_rect = pygame.Rect(W - PANEL_W + 20, y, 30, 24)
            pygame.draw.rect(self.__screen__, WOOD, key_rect, border_radius=4)
            self.__screen__.blit(self.__font_small__.render(key, True, IVORY),
                                 self.__font_small__.render(key, True, IVORY).get_rect(center=key_rect.center))
            self.__screen__.blit(self.__font_small__.render(desc, True, IVORY), (W - PANEL_W + 60, y + 4))
            y += 30

        # Instrucciones
        inst_rect = pygame.Rect(W - PANEL_W + 20, y + 10, PANEL_W - 40, 50)
        pygame.draw.rect(self.__screen__, WOOD_DARK, inst_rect, border_radius=6)
        self.__screen__.blit(self.__font_small__.render("Click: seleccionar ficha / BAR", True, IVORY), (inst_rect.x + 10, inst_rect.y + 8))
        self.__screen__.blit(self.__font_small__.render("1 / 2 / 3: usar dado A / B / A+B", True, IVORY), (inst_rect.x + 10, inst_rect.y + 28))

        # BAR & BORNE
        pygame.draw.rect(self.__screen__, WOOD, self.__bar_rect__, border_radius=8)
        pygame.draw.rect(self.__screen__, WOOD, self.__borne_rect__, border_radius=8)

        bar_w = len(self.__game__.board.__bar__[Player.WHITE])
        bar_b = len(self.__game__.board.__bar__[Player.BLACK])
        self.__screen__.blit(self.__font_small__.render("BAR", True, GOLD),
                             self.__font_small__.render("BAR", True, GOLD).get_rect(centerx=self.__bar_rect__.centerx, top=self.__bar_rect__.y + 5))
        self.__screen__.blit(self.__font_small__.render(f"Blancas: {bar_w}  Negras: {bar_b}", True, IVORY),
                             self.__font_small__.render(f"Blancas: {bar_w}  Negras: {bar_b}", True, IVORY).get_rect(centerx=self.__bar_rect__.centerx, top=self.__bar_rect__.y + 25))

        borne_w = len(self.__game__.board.__borne__[Player.WHITE])
        borne_b = len(self.__game__.board.__borne__[Player.BLACK])
        self.__screen__.blit(self.__font_small__.render("BORNE", True, GOLD),
                             self.__font_small__.render("BORNE", True, GOLD).get_rect(centerx=self.__borne_rect__.centerx, top=self.__borne_rect__.y + 5))
        self.__screen__.blit(self.__font_small__.render(f"Blancas: {borne_w}  Negras: {borne_b}", True, IVORY),
                             self.__font_small__.render(f"Blancas: {borne_w}  Negras: {borne_b}", True, IVORY).get_rect(centerx=self.__borne_rect__.centerx, top=self.__borne_rect__.y + 25))

        # Bandas índices
        top_idx = " ".join(f"{i:>2}" for i in range(12, 24))
        bot_idx = " ".join(f"{i:>2}" for i in range(11, -1, -1))

        label_h = 26
        top_band = pygame.Rect(BOARD_MARGIN - 2, BOARD_MARGIN - label_h - 8, BOARD_W + 4, label_h)
        bot_band = pygame.Rect(BOARD_MARGIN - 2, BOARD_MARGIN + BOARD_H + 8, BOARD_W + 4, label_h)
        pygame.draw.rect(self.__screen__, (20, 20, 20), top_band, border_radius=6)
        pygame.draw.rect(self.__screen__, (20, 20, 20), bot_band, border_radius=6)

        self.__screen__.blit(self.__font_small__.render("PUNTOS 12 → 23", True, GOLD), (top_band.x + 8, top_band.y + 4))
        self.__screen__.blit(self.__font_small__.render(top_idx, True, IVORY), (top_band.x + 140, top_band.y + 4))

        self.__screen__.blit(self.__font_small__.render("PUNTOS 11 → 0", True, GOLD), (bot_band.x + 8, bot_band.y + 4))
        self.__screen__.blit(self.__font_small__.render(bot_idx, True, IVORY), (bot_band.x + 140, bot_band.y + 4))

    def _draw_checkers(self):
        b = self.__game__.board

        def draw_stack(rect: pygame.Rect, idx: int, top: bool):
            owner = b.owner_at(idx)
            if owner is None:
                return
            n = b.count_at(idx)
            visible = min(n, 5)

            cx = rect.centerx
            if top:
                base_y = rect.bottom - CHECKER_R - 6
                dy = -(CHECKER_R * 2 + 4)
            else:
                base_y = rect.top + CHECKER_R + 6
                dy = (CHECKER_R * 2 + 4)

            color = WHITE_CHK if owner is Player.WHITE else BLACK_CHK
            last_cy = base_y
            for i in range(visible):
                cy = base_y + i * dy
                last_cy = cy
                pygame.draw.circle(self.__screen__, color, (cx, cy), CHECKER_R)
                pygame.draw.circle(self.__screen__, GOLD, (cx, cy), CHECKER_R, 2)

            # badge si hay más de 5
            if n > 5:
                badge_r = 11
                bx = cx + CHECKER_R - badge_r
                by = last_cy - (CHECKER_R - badge_r) if top else last_cy + (CHECKER_R - badge_r)
                pygame.draw.circle(self.__screen__, GOLD, (bx, by), badge_r)
                num_surf = self.__font_small__.render(str(n), True, INK)
                self.__screen__.blit(num_surf, num_surf.get_rect(center=(bx, by)))

        # Arriba (12..23) y abajo (11..0)
        for i, r in enumerate(self.__top_rects__):
            idx = 12 + i
            draw_stack(r, idx, top=True)
        for i, r in enumerate(self.__bot_rects__):
            idx = 11 - i
            draw_stack(r, idx, top=False)

        # Highlight origen
        if self.__selected_src__ is not None:
            if self.__selected_src__ == -1:  # BAR
                pygame.draw.rect(self.__screen__, GREEN, self.__bar_rect__, 3, border_radius=6)
            else:
                idx = self.__selected_src__
                r = self.__top_rects__[idx - 12] if 12 <= idx <= 23 else self.__bot_rects__[11 - idx]
                pygame.draw.rect(self.__screen__, GREEN, r, 3)

        # Estado
        a, bvals = self.__game__.dice.values
        dice_text = f"Dados: {a} - {bvals}" if (a, bvals) != (0, 0) else "Dados: Falta tirar"
        turn_text = "Juega: — (falta sorteo)" if self.__game__.current_player is None else f"Juega: {self.__game__.current_player.name}"
        self.__screen__.blit(self.__font_big__.render(f"Turno #{self.__game__.turn_count}", True, GOLD), (W - PANEL_W + 16, H - 170))
        self.__screen__.blit(self.__font__.render(turn_text, True, IVORY), (W - PANEL_W + 16, H - 140))
        self.__screen__.blit(self.__font__.render(dice_text, True, IVORY), (W - PANEL_W + 16, H - 116))

        # Índices en tablero (debug)
        if self.debug_mode:
            for i, r in enumerate(self.__top_rects__):
                idx = 12 + i
                self.__screen__.blit(self.__font_small__.render(str(idx), True, IVORY), (r.x + 4, r.y + 4))
            for i, r in enumerate(self.__bot_rects__):
                idx = 11 - i
                self.__screen__.blit(self.__font_small__.render(str(idx), True, IVORY), (r.x + 4, r.y + 4))

    # ---------- Interacción ----------
    def _blit_text(self, text: str, pos: Tuple[int, int], font=None, color=IVORY):
        if font is None:
            font = self.__font__
        surf = font.render(text, True, color)
        self.__screen__.blit(surf, pos)

    def _apply_move_distance(self, dist: int) -> bool:
        """Aplica movimiento usando {a, b, a+b}. Protege contra borne ilegal y no descuenta dados en errores."""
        if self.__game__.dice.values == (0, 0):
            self.__toast__.push("Primero tirá con R (roll)", RED)
            return False
        if self.__selected_src__ is None:
            self.__toast__.push("Elegí un origen (punto o BAR)", RED)
            return False

        src = None if self.__selected_src__ == -1 else self.__selected_src__
        a, b = self.__game__.dice.values
        valid_opts = [x for x in (a, b, a + b) if x > 0]
        if dist not in valid_opts:
            self.__toast__.push(f"Distancia inválida. Opciones: {valid_opts}", RED)
            return False

        try:
            # El core maneja dirección (WHITE decrementa, BLACK incrementa) y borne
            self.__game__.board.move(self.__game__.current_player, src, dist)
        except (PointBlocked, NoCheckerAtPoint, MustEnterFromBar, EntryBlocked, BearOffNotAllowed,
                GameNotStrated, GameFinished) as exc:
            # No tocamos dados ni selección: nada “desaparece”
            self.__toast__.push(self._friendly_error(exc), RED)
            return False
        except Exception as exc:
            self.__toast__.push(f"{exc.__class__.__name__}: {exc}", RED)
            return False

        # Descuento de dados sólo si el movimiento fue exitoso
        if dist == a + b and a and b:
            self.__game__.dice.__values__ = [0, 0]
        elif dist == a:
            self.__game__.dice.__values__[0] = 0
        elif dist == b:
            self.__game__.dice.__values__[1] = 0

        self.__selected_src__ = None
        self.__pending_dist__ = None

        self.__game__.check_game_over()
        if self.__game__.finished:
            self._show_win_and_exit()
        return True

    def _friendly_error(self, exc: Exception) -> str:
        mapping = {
            GameNotStrated: "La partida no está iniciada (S para start)",
            GameFinished: "La partida ya terminó",
            GameAlredyStarted: "La partida ya está iniciada",
            DiceAlreadyRolled: "Ya tiraste en este turno",
            DiceNotRolled: "Tenés que tirar con R antes de pasar",
            PointBlocked: "Punto destino bloqueado",
            NoCheckerAtPoint: "No hay ficha tuya en ese origen",
            MustEnterFromBar: "Debés entrar desde la BAR primero",
            EntryBlocked: "Entrada desde BAR bloqueada",
            BearOffNotAllowed: "Aún no podés retirar fichas",
        }
        for etype, msg in mapping.items():
            if isinstance(exc, etype):
                return msg
        return f"{exc.__class__.__name__}: {exc}"

    def _handle_key(self, key: int):
        if key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit(0)
        elif key == pygame.K_s:
            try:
                self.__game__.start()
                self.__toast__.push("Partida iniciada. R para sorteo inicial", GREEN)
            except Exception as exc:
                self.__toast__.push(self._friendly_error(exc), RED)
        elif key == pygame.K_r:
            try:
                was_draw = (self.__game__.current_player is None)
                vals = self.__game__.roll()
                if was_draw:
                    self.__toast__.push(f"Sorteo: WHITE {vals[0]} - BLACK {vals[1]}", GREEN)
                else:
                    self.__toast__.push(f"Dados: {vals[0]} - {vals[1]}  (1/2/3 para mover)", GREEN)
            except Exception as exc:
                self.__toast__.push(self._friendly_error(exc), RED)
        elif key == pygame.K_p:
            try:
                self.__game__.pass_turn()
                self.__toast__.push("Turno pasado", GOLD)
                self.__game__.check_game_over()
                if self.__game__.finished:
                    self._show_win_and_exit()
            except Exception as exc:
                self.__toast__.push(self._friendly_error(exc), RED)
        elif key in (pygame.K_1, pygame.K_KP1):
            self._apply_move_distance(self.__game__.dice.values[0])
        elif key in (pygame.K_2, pygame.K_KP2):
            self._apply_move_distance(self.__game__.dice.values[1])
        elif key in (pygame.K_3, pygame.K_KP3):
            a, b = self.__game__.dice.values
            self._apply_move_distance(a + b)

    def _handle_mouse(self, pos: Tuple[int, int]):
        # Click fuera de cualquier punto/bar → deseleccionar
        if not self.__bar_rect__.collidepoint(pos):
            idx = self._point_from_pos(pos)
            if idx is None:
                self.__selected_src__ = None
                return

        # BAR
        if self.__bar_rect__.collidepoint(pos):
            if len(self.__game__.board.__bar__[self.__game__.current_player]) > 0:
                self.__selected_src__ = -1
                self.__toast__.push("Origen: BAR (ahora 1/2/3)", GOLD)
            else:
                self.__toast__.push("No hay fichas en la BAR", RED)
                self.__selected_src__ = None
            return

        # Punto del tablero
        idx = self._point_from_pos(pos)
        owner = self.__game__.board.owner_at(idx)
        count = self.__game__.board.count_at(idx)

        if owner != self.__game__.current_player or count == 0:
            self.__toast__.push("No hay fichas tuyas en ese punto", RED)
            self.__selected_src__ = None
            return

        # Si hay fichas en BAR propias, hay que entrar primero
        if len(self.__game__.board.__bar__[self.__game__.current_player]) > 0:
            self.__toast__.push("Debés mover desde la BAR primero", RED)
            self.__selected_src__ = None
            return

        self.__selected_src__ = idx
        self.__toast__.push(f"Origen seleccionado: {idx}. Elegí 1/2/3", GOLD)

    def _show_win_and_exit(self):
        overlay = pygame.Surface((W, H))
        overlay.fill(INK)
        overlay.set_alpha(200)
        self.__screen__.blit(overlay, (0, 0))

        box_width, box_height = 500, 200
        box_rect = pygame.Rect((W - box_width) // 2, (H - box_height) // 2, box_width, box_height)
        pygame.draw.rect(self.__screen__, WOOD_DARK, box_rect, border_radius=15)
        pygame.draw.rect(self.__screen__, GOLD, box_rect, width=3, border_radius=15)

        winner_text = "¡VICTORIA!"
        winner_surf = self.__font_big__.render(winner_text, True, GOLD)
        self.__screen__.blit(winner_surf, winner_surf.get_rect(centerx=W // 2, centery=H // 2 - 30))

        player_text = f"{self.__game__.winner.name}"
        player_surf = self.__font_big__.render(player_text, True, IVORY)
        self.__screen__.blit(player_surf, player_surf.get_rect(centerx=W // 2, centery=H // 2 + 30))

        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit(0)

    # ---------- Loop ----------
    def run(self):
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

                if not self.setup_done:
                    self._handle_setup_events(ev)
                else:
                    if ev.type == pygame.KEYDOWN:
                        self._handle_key(ev.key)
                    elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        self._handle_mouse(ev.pos)

            if not self.setup_done:
                self._draw_setup_screen()
            else:
                self._draw_board()
                self._draw_checkers()
                self.__toast__.draw(self.__screen__)

            pygame.display.flip()
            self.__clock__.tick(60)


def run() -> None:
    PygameUI().run()


if __name__ == "__main__":
    run()
