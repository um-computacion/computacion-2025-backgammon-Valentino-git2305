## [Día 1] - 2025-08-26
### Agregado
- Creé estructura inicial del proyecto con carpetas: core, cli, pygame_ui, tests, assets.
- Agregué archivos __init__.py en cada subcarpeta para tratarlas como paquetes.
- Agregué archivo requirements.txt con dependencias (pygame, pytest).
- Agregué archivo README.md con descripción inicial del proyecto.
- Intalé el entorno virtual pero no lo estoy usando ya que estoy trabajando en un entorno aisaldo con codesapces.
## [Día 2] - 2025-08-27
### Agregado
- Cree la clase Player con atributos 'WHITE', 'BLACK', metodo '__direction__()' y '__home_range__()'.
- Cree la calse Board con contructor y metodo 'setup()' para la posicion inicial de la fichas
- Cree los Test para 'Player' y 'Board' usando unittest.
## [Día 3] - 2025-08-28
### Agregado
- Implemené el método reset() en la clase Board para reiniciar el estado del tablero al comienzo de una partida..
- Cree el método count_checkers(player) para contar la cantidad total de fichas de un jugador (tablero, barra y borne).
- Definí el método __str__() en Board para visualizar en consola el estado actual del tablero.
- Agregué el test de __reset_board__ y el de __str_board__.
- Intalé coverage y lo agregué a la carpeta requierments.txt.