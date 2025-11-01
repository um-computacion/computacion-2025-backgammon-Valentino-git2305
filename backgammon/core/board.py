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
    
    def dest_index(self, player:Player, src: int, die:int) -> int:#Nos sirve para calcular el punto donde va a terminar la ficha, las blancas+1 negras-1.
        direction = 1 if player is Player.WHITE else -1
        return src +direction * die


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
        return range(18, 24) if player is Player.WHITE else range (0, 6)
    
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
    
    def move(self, player: Player, src: int | None, die: int):
        """
        Mueve una fihca del player usando el dado.
        """
        if self.has_in_bar(player):
            if src is not None:
                raise MustEnterFromBar()
            dst = self.entry_index_from_bar(player, die)
            if not (0 <= dst < 24):
                raise EntryBlocked()
            if self.is_blocked_for(player, dst):
                raise EntryBlocked()
        
            opp = Player.BLACK if player is Player.WHITE else Player.WHITE
            if self.owner_at(dst) is opp and self.count_at(dst) == 1:
               beaten = self.__points__[dst].pop()
               self.__bar__[opp].append(beaten)

            checker = self.__bar__[player].pop() if self.__bar__[player] else Checker(player)
            self.__points__[dst].append(checker)
            return
        
        if src is None or not (0 <= src < 24):
            raise NoCheckerAtPoint()
        if self.count_at(src) == 0 or self.owner_at(src) is not player:
            raise NoCheckerAtPoint()
        
        dst = self.dest_index(player, src, die)

        if dst < 0 or dst > 23:
            if not self.can_bear_off(player):
                raise BearOffNotAllowed()
            exact_src = (23 - (die - 1)) if player is Player.WHITE else (0 + (die-1))
            if src != exact_src:
                raise BearOffNotAllowed()
            checker = self.__points__[src].pop()
            self.__borne__[player].append(checker)
            return
        
        if self.is_blocked_for(player, dst):
            raise PointBlocked()
        
        opp = Player.BLACK if player is Player.WHITE else Player.WHITE

        if self.owner_at(dst) is opp and self.count_at(dst) == 1:
            beaten = self.__points__[dst].pop()
            self.__bar__[opp].append(beaten)
        
        checker = self.__points__[src].pop()
        self.__points__[dst].append(checker)

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
        
        #Mapas de columnas (12 arriba, 24 abajo)
        top_idxs = list(range(12, 24))
        bot_idxs = list(range(11, -1. -1))

        #Contruí columnas de 5 filas(con topes)
        max_rows = 5
        top_cols = [col_symbol(i) for i in top_idxs]
        top_cols = [col_symbol(i) for i in bot_idxs]

        # Encabezados de números de punto (como se ve en un tablero real)
        top_labels = [f"{i+1:>2}" for i in range(12, 24)]    
        bot_labels = [f"{i+1:>2}" for i in range(11, -1, -1)]

        # Función para apilar visualmente una fila dada
        def build_row(cols: list[list[str]], row_from_top: int, filler: str = ' ') -> str:
            # row_from_top: 0 es la "capa" más alta
            cells = []
            for col in cols:
                char = col[row_from_top] if row_from_top < len(col) else filler
                cells.append(f" {char} ")
            return "|" + "|".join(cells) + "|"

        # Top panel
        lines = []
        lines.append("         " + " ".join(top_labels))
        lines.append("        " + "-" * (len(top_labels) * 3 + (len(top_labels) - 1)))

        for r in range(max_rows):
            lines.append(build_row(top_cols, r))

        # Línea central: BAR y BORNE
        w_bar = len(self.__bar__[Player.WHITE])
        b_bar = len(self.__bar__[Player.BLACK])
        w_borne = len(self.__borne__[Player.WHITE])
        b_borne = len(self.__borne__[Player.BLACK])

        center = f"   BAR: W={w_bar} B={b_bar}   |   BORNE: W={w_borne} B={b_borne}"
        lines.append(center)

        # Bottom panel (se dibuja de abajo hacia arriba)
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