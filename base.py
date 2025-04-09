import random
import math
import heapq

class Jugador:
    def __init__(self, jugador_id: int):
        self.jugador_id = jugador_id
        self.oponente_id = 2 if jugador_id == 1 else 1

    def jugar(self, tablero: 'TableroHex') -> tuple:
        movimientos_disponibles = tablero.obtener_movimientos_posibles()
        total_libres = len(movimientos_disponibles)

        if total_libres > 15:
            profundidad = 1
        elif total_libres > 8:
            profundidad = 2
        else:
            profundidad = 3

        movimientos_ordenados = self.ordenar_movimientos(movimientos_disponibles, tablero.tamano)
        mejor_puntaje = -math.inf
        mejor_movimiento = random.choice(movimientos_disponibles)

        for movimiento in movimientos_ordenados:
            fila, col = movimiento
            tablero.simular_ficha(fila, col, self.jugador_id)
            puntaje = self.minimax(tablero, profundidad - 1, False, -math.inf, math.inf)
            tablero.deshacer_ficha(fila, col)

            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_movimiento = movimiento

        return mejor_movimiento

    def ordenar_movimientos(self, movimientos, tam):
        centro = tam // 2
        return sorted(movimientos, key=lambda m: abs(m[0] - centro) + abs(m[1] - centro))

    def minimax(self, tablero, profundidad, es_maximizador, alfa, beta):
        if (profundidad == 0 or
            tablero.hay_conexion(self.jugador_id) or
            tablero.hay_conexion(self.oponente_id)):
            return self.evaluar(tablero)

        movimientos = tablero.obtener_movimientos_posibles()
        movimientos = self.ordenar_movimientos(movimientos, tablero.tamano)

        if es_maximizador:
            maximo = -math.inf
            for fila, col in movimientos:
                tablero.simular_ficha(fila, col, self.jugador_id)
                evaluacion = self.minimax(tablero, profundidad - 1, False, alfa, beta)
                tablero.deshacer_ficha(fila, col)
                maximo = max(maximo, evaluacion)
                alfa = max(alfa, evaluacion)
                if beta <= alfa:
                    break
            return maximo
        else:
            minimo = math.inf
            for fila, col in movimientos:
                tablero.simular_ficha(fila, col, self.oponente_id)
                evaluacion = self.minimax(tablero, profundidad - 1, True, alfa, beta)
                tablero.deshacer_ficha(fila, col)
                minimo = min(minimo, evaluacion)
                beta = min(beta, evaluacion)
                if beta <= alfa:
                    break
            return minimo

    def evaluar(self, tablero):
        def distancia_conexion(jugador_id):
            tam = tablero.tamano
            dist = [[math.inf] * tam for _ in range(tam)]
            heap = []

            if jugador_id == 1:
                for col in range(tam):
                    if tablero.tablero[0][col] in [0, jugador_id]:
                        dist[0][col] = 0
                        heapq.heappush(heap, (0, 0, col))
            else:
                for fila in range(tam):
                    if tablero.tablero[fila][0] in [0, jugador_id]:
                        dist[fila][0] = 0
                        heapq.heappush(heap, (0, fila, 0))

            direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]

            while heap:
                costo, fila, col = heapq.heappop(heap)
                for df, dc in direcciones:
                    nf, nc = fila + df, col + dc
                    if 0 <= nf < tam and 0 <= nc < tam:
                        celda = tablero.tablero[nf][nc]
                        if celda == jugador_id:
                            nuevo_costo = costo
                        elif celda == 0:
                            # penalización si hay enemigos alrededor
                            enemigos = sum(
                                1 for ddf, ddc in direcciones
                                if 0 <= nf + ddf < tam and 0 <= nc + ddc < tam and
                                tablero.tablero[nf + ddf][nc + ddc] == self.oponente_id
                            )
                            nuevo_costo = costo + 1 + enemigos * 0.5
                        else:
                            continue
                        if nuevo_costo < dist[nf][nc]:
                            dist[nf][nc] = nuevo_costo
                            heapq.heappush(heap, (nuevo_costo, nf, nc))

            if jugador_id == 1:
                return min(dist[tam - 1][col] for col in range(tam))
            else:
                return min(dist[fila][tam - 1] for fila in range(tam))

        def bonus_puentes(jugador_id):
            tam = tablero.tamano
            bonus = 0
            direcciones = [(-1, 1), (1, -1), (-1, -1), (1, 1)]
            for fila in range(tam):
                for col in range(tam):
                    if tablero.tablero[fila][col] == jugador_id:
                        for df, dc in direcciones:
                            nf, nc = fila + df * 2, col + dc * 2
                            mf, mc = fila + df, col + dc
                            if (
                                0 <= nf < tam and 0 <= nc < tam and
                                0 <= mf < tam and 0 <= mc < tam and
                                tablero.tablero[nf][nc] == jugador_id and
                                tablero.tablero[mf][mc] == 0
                            ):
                                bonus += 1  
            return bonus

        def bonus_centro(jugador_id):
            tam = tablero.tamano
            centro = tam // 2
            score = 0
            for fila in range(tam):
                for col in range(tam):
                    if tablero.tablero[fila][col] == jugador_id:
                        dist_centro = abs(fila - centro) + abs(col - centro)
                        score += max(0, 5 - dist_centro)  
            return score

    
        d_propio = distancia_conexion(self.jugador_id)
        d_oponente = distancia_conexion(self.oponente_id)

        heuristica = (
            (d_oponente - d_propio) * 10 +  # mantener la parte principal
            bonus_puentes(self.jugador_id) * 3 -
            bonus_puentes(self.oponente_id) * 2 +
            bonus_centro(self.jugador_id) * 1 -
            bonus_centro(self.oponente_id) * 1
        )

        return heuristica


class TableroHex:
    def __init__(self, tamano: int):
        self.tamano = tamano
        self.tablero = [[0] * tamano for _ in range(tamano)]

    def colocar_ficha(self, fila: int, columna: int, jugador_id: int) -> bool:
        if self.tablero[fila][columna] == 0:
            self.tablero[fila][columna] = jugador_id
            return True
        return False

    def simular_ficha(self, fila: int, columna: int, jugador_id: int):
        self.tablero[fila][columna] = jugador_id

    def deshacer_ficha(self, fila: int, columna: int):
        self.tablero[fila][columna] = 0

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
                nf, nc = fila + df, columna + dc
                if 0 <= nf < self.tamano and 0 <= nc < self.tamano:
                    if self.tablero[nf][nc] == jugador_id and (nf, nc) not in visitado:
                        pila.append((nf, nc))

        return False


def mostrar_tablero(tablero):
    for fila in tablero.tablero:
        print(' '.join(str(celda) for celda in fila))
    print()


if __name__ == "__main__":
    tablero = TableroHex(5) 
    jugador1 = Jugador(1)
    jugador2 = Jugador(2)

    turno = 1

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

        if not tablero.obtener_movimientos_posibles():
            mostrar_tablero(tablero)
            print("🤝 ¡Empate!")
            break
