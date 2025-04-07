import random
import math
from copy import deepcopy

class Jugador:
    def __init__(self, jugador_id: int):
        self.jugador_id = jugador_id
        self.oponente_id = 2 if jugador_id == 1 else 1
        self.profundidad_maxima = 2

    def jugar(self, tablero: 'TableroHex') -> tuple:
        movimientos_disponibles = tablero.obtener_movimientos_posibles()
        mejor_puntaje = -math.inf
        mejor_movimiento = random.choice(movimientos_disponibles)

        for movimiento in movimientos_disponibles:
            tablero_simulado = deepcopy(tablero)
            tablero_simulado.colocar_ficha(movimiento[0], movimiento[1], self.jugador_id)
            puntaje = self.minimax(tablero_simulado, self.profundidad_maxima - 1, False, -math.inf, math.inf)
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_movimiento = movimiento

        return mejor_movimiento

    def minimax(self, tablero, profundidad, es_maximizador, alfa, beta):
        if (profundidad == 0 or
            tablero.hay_conexion(self.jugador_id) or
            tablero.hay_conexion(self.oponente_id)):
            return self.evaluar(tablero)

        movimientos_posibles = tablero.obtener_movimientos_posibles()

        if es_maximizador:
            maximo = -math.inf
            for movimiento in movimientos_posibles:
                nuevo_tablero = deepcopy(tablero)
                nuevo_tablero.colocar_ficha(movimiento[0], movimiento[1], self.jugador_id)
                evaluacion = self.minimax(nuevo_tablero, profundidad - 1, False, alfa, beta)
                maximo = max(maximo, evaluacion)
                alfa = max(alfa, evaluacion)
                if beta <= alfa:
                    break
            return maximo
        else:
            minimo = math.inf
            for movimiento in movimientos_posibles:
                nuevo_tablero = deepcopy(tablero)
                nuevo_tablero.colocar_ficha(movimiento[0], movimiento[1], self.oponente_id)
                evaluacion = self.minimax(nuevo_tablero, profundidad - 1, True, alfa, beta)
                minimo = min(minimo, evaluacion)
                beta = min(beta, evaluacion)
                if beta <= alfa:
                    break
            return minimo

    def evaluar(self, tablero):
        fichas_propias = sum(fila.count(self.jugador_id) for fila in tablero.tablero)
        fichas_oponente = sum(fila.count(self.oponente_id) for fila in tablero.tablero)
        return fichas_propias - fichas_oponente


class TableroHex:
    def __init__(self, tamano: int):
        self.tamano = tamano
        self.tablero = [[0] * tamano for _ in range(tamano)]
        self.fichas_por_jugador = {1: set(), 2: set()}

    def colocar_ficha(self, fila: int, columna: int, jugador_id: int) -> bool:
        if self.tablero[fila][columna] == 0:
            self.tablero[fila][columna] = jugador_id
            return True
        return False

    def obtener_movimientos_posibles(self) -> list:
        vacios = []
        for fila in range(self.tamano):
            for columna in range(self.tamano):
                if self.tablero[fila][columna] == 0:
                    vacios.append((fila, columna))
        return vacios

    def hay_conexion(self, jugador_id: int) -> bool:
        visitado = set()
        pila = []

        if jugador_id == 1:
            for columna in range(self.tamano):
                if self.tablero[0][columna] == jugador_id:
                    pila.append((0, columna))
        else:
            for fila in range(self.tamano):
                if self.tablero[fila][0] == jugador_id:
                    pila.append((fila, 0))

        while pila:
            fila, columna = pila.pop()
            if (fila, columna) in visitado:
                continue
            visitado.add((fila, columna))

            if jugador_id == 1 and fila == self.tamano - 1:
                return True
            if jugador_id == 2 and columna == self.tamano - 1:
                return True

            for df, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]:
                nueva_fila, nueva_columna = fila + df, columna + dc
                if 0 <= nueva_fila < self.tamano and 0 <= nueva_columna < self.tamano:
                    if self.tablero[nueva_fila][nueva_columna] == jugador_id and (nueva_fila, nueva_columna) not in visitado:
                        pila.append((nueva_fila, nueva_columna))

        return False

def mostrar_tablero(tablero):
    for fila in tablero.tablero:
        print(' '.join(str(celda) for celda in fila))
    print()

if __name__ == "__main__":
    # Inicializar el tablero y los jugadores
    tablero = TableroHex(3)  # puedes cambiar el tamaño del tablero
    jugador1 = Jugador(1)
    jugador2 = Jugador(2)
    
    turno = 1  # Jugador 1 comienza

    while True:
        mostrar_tablero(tablero)

        if turno == 1:
            print("Turno del Jugador 1")
            movimiento = jugador1.jugar(tablero)
            tablero.colocar_ficha(movimiento[0], movimiento[1], 1)
            if tablero.hay_conexion(1):
                mostrar_tablero(tablero)
                print("🏆 ¡Jugador 1 gana!")
                break
            turno = 2
        else:
            print("Turno del Jugador 2")
            movimiento = jugador2.jugar(tablero)
            tablero.colocar_ficha(movimiento[0], movimiento[1], 2)
            if tablero.hay_conexion(2):
                mostrar_tablero(tablero)
                print("🏆 ¡Jugador 2 gana!")
                break
            turno = 1

        # Si no hay más movimientos, es empate
        if not tablero.obtener_movimientos_posibles():
            mostrar_tablero(tablero)
            print("🤝 ¡Empate!")
            break


          