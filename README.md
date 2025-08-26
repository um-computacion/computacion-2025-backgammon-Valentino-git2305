# Backgammon – Computación 2025

## Objetivo
Separar la **lógica** del juego (`backgammon/core`) de las **interfaces**:
- CLI: `backgammon/cli`
- UI Pygame: `backgammon/pygame_ui`

## Estructura
backgammon/
  core/       # Reglas, tablero, dados, estado del juego
  cli/        # Interfaz de consola
  pygame_ui/  # Interfaz gráfica (Pygame)
  tests/      # Pruebas (pytest)
  assets/     # Recursos

## Cómo correr
Instalar dependencias:
  pip install -r requirements.txt

CLI (cuando esté implementada):
  python -m backgammon.cli.main

Tests (cuando existan):
  pytest -q
