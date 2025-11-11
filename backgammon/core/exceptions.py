class BackgammonError(Exception):
    """Base de todas las exceptions del proyecto"""


#Estado del juego

class GameNotStrated(BackgammonError):
    """La partida todavia no ha comenzado"""

class GameAlredyStarted(BackgammonError):
    """La partida ya fue iniciada"""

class GameFinished(BackgammonError):
    """La partida ya terminó"""

#Turnos / dados

class NotYourTurn(BackgammonError):
    """No es turo del jugador"""

class DiceNotRolled(BackgammonError):
    """Falta tirar los dados"""

class DiceAlreadyRolled(BackgammonError):
    """Se intento volver a tirar en el mismo turno"""

#Movimiento en tablero

class IllegalMoves(BackgammonError):
    """Movimiento invalido"""

class PointBlocked(BackgammonError):
    """El punto de destino esta bloqueado"""

class NoCheckerAtPoint(BackgammonError):
    """No hay ficha del jugador en punto de origen"""

class MustEnterFromBar(BackgammonError):
    """El jugador tiene fichas en la barra, debe reingresarlas para jugar"""

class EntryBlocked(BackgammonError):
    """La entrada de la barra esta bloqueda para el dado obtenido"""

class BearOffNotAllowed(BackgammonError):
    """No puede retirar la fichas aún"""

#CLI

class InvalidCommand(BackgammonError):
    """Comando invalido"""