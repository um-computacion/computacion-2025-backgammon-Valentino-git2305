from backgammon.core.player import Player
from backgammon.core.checker import Checker
from backgammon.core.exceptions import ( PointBlocked, NoCheckerAtPoint, MustEnterFromBar, EntryBlocked, BearOffNotAllowed)

class Board:

    '''Tablero:
       24 puntos enumerados del 0 al 23
       Cada punto puede tener 0 o 5 fichas como maximo de un jugador
       Administacion de barra (sector donde van las piezas comidas) y borne (sector donde van las fichas retiradas del juego)'''
    
    def __init__(self):#Inicializa un tabelro vacio con barra y borne por Player        
        self.__points__=[ [] for _ in range(24) ]
        self.__bar__ = {Player.WHITE: [], Player.BLACK: []}
        self.__borne__={Player.WHITE: [], Player.BLACK: []}
    
    def __setup__(self):#Posicion de las fichas al comienzo de la partida
        self.__points__[0] = [Checker(Player.BLACK) for _ in range(2)]
        self.__points__[5] = [Checker(Player.WHITE) for _ in range(5)]
        self.__points__[7] = [Checker(Player.WHITE) for _ in range(3)]
        self.__points__[11] = [Checker(Player.BLACK) for _ in range(5)]
        self.__points__[12] = [Checker(Player.WHITE) for _ in range(5)]
        self.__points__[16] = [Checker(Player.BLACK) for _ in range(3)]
        self.__points__[18] = [Checker(Player.BLACK) for _ in range(5)]
        self.__points__[23] = [Checker(Player.WHITE) for _ in range(2)]

    def __reset__(self):#Reinicia el tablero a la posicion inicial
        self.__points__=[[] for _ in range(24)]
        self.__bar__={Player.WHITE:[], Player.BLACK:[]}
        self.__borne__={Player.WHITE:[], Player.BLACK:[]}

        self.__points__[0] = [Checker(Player.BLACK) for _ in range(2)]
        self.__points__[5] = [Checker(Player.WHITE) for _ in range(5)]
        self.__points__[7] = [Checker(Player.WHITE) for _ in range(3)]
        self.__points__[11] = [Checker(Player.BLACK) for _ in range(5)]
        self.__points__[12] = [Checker(Player.WHITE) for _ in range(5)]
        self.__points__[16] = [Checker(Player.BLACK) for _ in range(3)]
        self.__points__[18] = [Checker(Player.BLACK) for _ in range(5)]
        self.__points__[23] = [Checker(Player.WHITE) for _ in range(2)]
    
    def owner_at(self, idx: int):#Nos sirve para ver que fiicha hay en un punto.
        pile = self.__points__[idx]
        return pile[-1].owner if pile else None
    
    def count_at(self, idx: int) -> int:#Nos dice cuantas fichas hay en un punto.
        return len(self.__points__[idx])
    
    def is_blocked_for(self, player: Player, idx: int) -> bool:#Nos sirve para saber si un punto esta bloqueado por el otro jugador o no.
        if not (0 <= idx < 24):
            return False
        opp = Player.BLACK if player is Player.WHITE else Player.WHITE
        return self.owner_at(idx) is opp and self.count_at(idx) >= 2
    
    def entry_index_from_bar(self, player: Player, die:int) -> int:#Nos sive para que un jugador pueda volver al juego si le comieron una ficha.
        return (die -1) if player is Player.WHITE else (24 - die)
    
    def dest_index(self, player:Player, src: int, die:int) -> int:
        direction = -1 if player is Player.WHITE else +1
        return src + direction * die

    def __count_checkers__(self, player: Player) -> int:#Cuenta las fichas de cada jugador en el tablero, barra y brone
        total=0
        for point in self.__points__:
            total += sum(1 for c in point if getattr(c, "owner", None) == player)
        total += len(self.__bar__[player])
        total += len(self.__borne__[player])
        return total

    def has_in_bar(self, player: Player) -> bool:#Nos dice si el player tiene fichas en la bar
        return len(self.__bar__[player]) > 0

    def home_range (self, player:Player) -> range:#Nos devuelve el home range de cada player
        return range(0, 6) if player is Player.WHITE else range (18, 24)
    
    def direction(self, player: Player) -> int:
        return -1 if player is Player.WHITE else +1
    
    def can_bear_off(self, player:Player) -> bool:
        """
        Se pueden retirar las fichas si:
        -No hay fichas en la barra
        -Todas las fichas del player estan dentro del home range
        """
        if self.has_in_bar(player):
            return False
        home = self.home_range(player)
        for i in range(24):
            if self.owner_at(i) is player and i not in home:
                return False
        return True
    
    def move(self, player: Player, src: int | None, die: int) -> None:
        MAX_STACK = 5
        if src is not None and self.has_in_bar(player):
            raise MustEnterFromBar()

        if src is None:
            if not self.__bar__[player]:
                raise MustEnterFromBar()
            checker = self.__bar__[player].pop()
            src_index = None
            dest = self.entry_index_from_bar(player, die)

        else:
            if src < 0 or src > 23:
                raise ValueError("Índice inválido")
            pile = self.__points__[src]
            if not pile or pile[-1].owner != player:
                raise NoCheckerAtPoint()
            checker = pile.pop()
            src_index = src
            if player is Player.WHITE:
                dest = src - die
            else:
                dest = src + die

        if dest < 0 and player is Player.WHITE:
            if not self.can_bear_off(player):
                raise BearOffNotAllowed()
            self.__borne__[player].append(checker)
            return
        if dest > 23 and player is Player.BLACK:
            if not self.can_bear_off(player):
                raise BearOffNotAllowed()
            self.__borne__[player].append(checker)
            return

        if dest < 0 or dest > 23:
            raise ValueError("Destino fuera del tablero")

        dest_pile = self.__points__[dest]

        if dest_pile and dest_pile[-1].owner is not player and len(dest_pile) == 1:
            beaten = dest_pile.pop()
            opponent = Player.BLACK if player is Player.WHITE else Player.WHITE
            self.__bar__[opponent].append(beaten)

        if dest_pile and dest_pile[-1].owner is not player and len(dest_pile) >= 2:
            if src_index is None:
                self.__bar__[player].append(checker)
                raise EntryBlocked()
            else:
                self.__points__[src_index].append(checker)
                raise PointBlocked()

        if dest_pile and dest_pile[-1].owner is player and len(dest_pile) >= MAX_STACK:
            if src_index is None:
                self.__bar__[player].append(checker)
            else:
                self.__points__[src_index].append(checker)
            from backgammon.core.exceptions import IllegalMoves
            raise IllegalMoves("No podés tener más de 5 fichas en un punto.")

        dest_pile.append(checker)


    def ascii(self):
        """
        Dibuja un tablero ASCII al estilo backgammon
        """
        def col_symbol(idx: int) -> list[str]:
            pile = self.__points__[idx]
            #Nos va a mostrar los simbolos x chekcer
            symbols = [("W" if c.owner.name == "WHITE" else "B") for c in pile]
            #Hasta 5 visibles
            visible = symbols[:5]
            return visible

        top_idxs = list(range(12, 24))
        bot_idxs = list(range(11, -1, -1))

        #Contruí columnas de 5 filas(con topes)
        max_rows = 5
        top_cols = [col_symbol(i) for i in top_idxs]
        bot_cols = [col_symbol(i) for i in bot_idxs]
        top_labels = [f"{i+1:>2}" for i in range(12, 24)]    
        bot_labels = [f"{i+1:>2}" for i in range(11, -1, -1)]
        bot_cols = []

        def build_row(cols: list[list[str]], row_from_top: int, filler: str = ' ') -> str:
            cells = []
            for col in cols:
                char = col[row_from_top] if row_from_top < len(col) else filler
                cells.append(f" {char} ")
            return "|" + "|".join(cells) + "|"
        lines = []
        lines.append("         " + " ".join(top_labels))
        lines.append("        " + "-" * (len(top_labels) * 3 + (len(top_labels) - 1)))

        for r in range(max_rows):
            lines.append(build_row(top_cols, r))

        w_bar = len(self.__bar__[Player.WHITE])
        b_bar = len(self.__bar__[Player.BLACK])
        w_borne = len(self.__borne__[Player.WHITE])
        b_borne = len(self.__borne__[Player.BLACK])

        center = f"   BAR: W={w_bar} B={b_bar}   |   BORNE: W={w_borne} B={b_borne}"
        lines.append(center)

        for r in range(max_rows - 1, -1, -1):
            lines.append(build_row(bot_cols, r))

        lines.append("        " + "-" * (len(bot_labels) * 3 + (len(bot_labels) - 1)))
        lines.append("         " + " ".join(bot_labels))

        return "\n".join(lines)

    def __str__(self):#Nos da en texto como esta el tablero
        output = []

        for i, point in enumerate(self.__points__):
            if point:
                owner = point[0].owner.name
                color = point[0].color.name
                cantidad = len(point)
                output.append(f"{i:2d}: {cantidad} ficha(s) de {owner} ({color})")
            else:
                output.append(f"{i:2d}: vacio")
        
        return "\n".join(output)