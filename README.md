# Backgammon – Computación 2025

## Objetivo
Implementar una versión completa del juego Backgammon en Python, separando la lógica del juego del sistema de interfaces.
El proyecto aplica conceptos de programación orientada a objetos, manejo de excepciones, modularización y pruebas unitarias.

## Estructura del Proyecto
backgammon/
  core/         # Núcleo lógico del juego (tablero, fichas, reglas, dados, jugadores)
  cli/          # Interfaz por consola (interacción textual)
  pygame_ui/    # Interfaz gráfica desarrollada con Pygame
  tests/        # Pruebas unitarias (unittest)
  assets/       # Recursos opcionales (gráficos, sonidos, etc.)

## Descripción de Módulos

core/           # Lógica principal del juego
  board.py      # Representación del tablero y movimientos
  checker.py    # Definición de fichas (Checkers)
  dice.py       # Lógica de los dados
  game.py       # Flujo de la partida y reglas
  player.py     # Enum de jugadores (WHITE / BLACK)
  exceptions.py # Excepciones personalizadas del juego

cli/            # Interfaz de consola
  cli.py        # Comandos interactivos del juego
  __main__.py   # Punto de entrada del modo consola

pygame_ui/      # Interfaz visual (Pygame)
  pygame_app.py # Tablero gráfico, fichas, animaciones, interacción con mouse/teclado
  __init__.py   # Inicialización del módulo

tests/          # Pruebas unitarias
  test_board.py # Test de movimientos del tablero
  test_game.py  # Test de reglas y condiciones de victoria
  ...           # Otros tests del núcleo lógico

## Instalación y Configuración

# 1. Clonar el repositorio
git clone https://github.com/Valentino-git2305/computacion-2025-backgammon-Valentino-git2305.git
cd computacion-2025-backgammon-Valentino-git2305

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno virtual
# Windows (PowerShell)
.\.venv\Scripts\activate
# Linux / Mac
source .venv/bin/activate

# 4. Instalar dependencias
pip install pygame==2.6.1

## Cómo jugar

# Modo Consola (CLI)
python -m backgammon.cli

# Comandos disponibles
start     -> Inicia una nueva partida
roll      -> Tira los dados
move X Y  -> Mueve una ficha (ejemplo: move 12 3)
pass      -> Pasa el turno
board     -> Muestra el tablero
status    -> Muestra el estado del juego
exit      -> Finaliza la partida

# Modo Gráfico (Pygame)
python -m backgammon.pygame_ui.pygame_app

# Controles Pygame
S        -> Iniciar partidaR        -> Tirar dados
P        -> Pasar turno
ESC      -> Salir del juego
Click izq -> Seleccionar una ficha o la BAR
1 / 2 / 3 -> Mover usando dado A / B / A+B

## Características de la Interfaz Pygame
- Pantalla de configuración de jugadores (nombres y colores)
- Movimiento visual de fichas y detección de golpes
- Mensajes emergentes (toast) de errores o acciones
- Bloqueo del borne ilegal sin pérdida de fichas
- Contador visible cuando hay más de 5 fichas en una casilla
- Mensaje de victoria con animación final

## Pruebas Unitarias
Ejecutar todos los tests:
python -m unittest -q

# Los tests validan:
- Movimientos válidos e inválidos en el tablero
- Tiradas de dados y alternancia de turnos
- Entrada desde la BAR y borne
- Manejo correcto de excepciones personalizadas

## Requisitos
- Python 3.12 o superior
- Pygame 2.6.1
- Compatible con Windows, Linux y macOS

## Créditos
#utor: Valentino Molinelli
Materia: Computación 2025
Carrera: Ingeniería en Informática – Universidad de Mendoza

## Licencia
Proyecto distribuido bajo licencia MIT.
Puede ser utilizado, modificado y redistribuido libremente citando al autor original.
