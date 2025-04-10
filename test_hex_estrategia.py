
import time
from base_estrategia_completa import Player, HexBoard

def mostrar_tablero(tablero):
    for fila in tablero.tablero:
        print(' '.join(str(celda) for celda in fila))
    print()

if __name__ == "__main__":
    tamano_tablero = 7  # Puedes ajustar a 5, 7, 9, etc.
    tablero = HexBoard(tamano_tablero)
    jugador1 = Player(1)
    jugador2 = Player(2)
    turno = 1
    movimientos_totales = 0
    tiempos_jugador1 = []
    tiempos_jugador2 = []

    while True:
        mostrar_tablero(tablero)

        if turno == 1:
            print("🔵 Turno del Jugador 1")
            inicio = time.time()
            movimiento = jugador1.play(tablero)
            duracion = time.time() - inicio
            tiempos_jugador1.append(duracion)
            tablero.colocar_ficha(movimiento[0], movimiento[1], 1)
            movimientos_totales += 1
            if tablero.check_connection(1):
                mostrar_tablero(tablero)
                print("🏆 ¡Jugador 1 gana!")
                break
            turno = 2
        else:
            print("🔴 Turno del Jugador 2")
            inicio = time.time()
            movimiento = jugador2.play(tablero)
            duracion = time.time() - inicio
            tiempos_jugador2.append(duracion)
            tablero.colocar_ficha(movimiento[0], movimiento[1], 2)
            movimientos_totales += 1
            if tablero.check_connection(2):
                mostrar_tablero(tablero)
                print("🏆 ¡Jugador 2 gana!")
                break
            turno = 1

        if not tablero.get_possible_moves():
            mostrar_tablero(tablero)
            print("🤝 ¡Empate!")
            break

    print("\n📊 Estadísticas de la partida:")
    print(f"Total de movimientos: {movimientos_totales}")
    print(f"Promedio Jugador 1: {sum(tiempos_jugador1)/len(tiempos_jugador1):.3f} s")
    print(f"Promedio Jugador 2: {sum(tiempos_jugador2)/len(tiempos_jugador2):.3f} s")
