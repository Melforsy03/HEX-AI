
import random
import math
import heapq
import concurrent.futures
from hashlib import sha256

transposition_table = {}

def evaluar_movimiento_global(args):
    jugador_id, tablero_flat, tamano, movimiento, profundidad = args
    jugador = Player(jugador_id)
    tablero = HexBoard(tamano)
    tablero.tablero = [list(tablero_flat[i:i+tamano]) for i in range(0, len(tablero_flat), tamano)]
    fila, col = movimiento
    tablero.simular_ficha(fila, col, jugador_id)
    jugador._profundidad_actual = profundidad
    puntaje = jugador.minimax(tablero, profundidad - 1, False, -math.inf, math.inf)
    return puntaje, movimiento

class Player:
    def __init__(self, jugador_id: int):
        self.jugador_id = jugador_id
        self.oponente_id = 2 if jugador_id == 1 else 1

    def play(self, tablero: 'HexBoard') -> tuple:
        movimientos_disponibles = tablero.get_possible_moves()
        total_libres = len(movimientos_disponibles)
        tam = tablero.tamano

        if total_libres >= 40:
            profundidad = 1
        elif total_libres >= 20:
            profundidad = 2
        else:
            profundidad = 3

        if total_libres == tam * tam:
            centro = tam // 2
            if tablero.tablero[centro][centro] == 0:
                return (centro, centro)

        tablero_flat = sum(tablero.tablero, [])
        args = [(self.jugador_id, tablero_flat, tam, mov, profundidad) for mov in movimientos_disponibles]
        with concurrent.futures.ProcessPoolExecutor() as executor:
            resultados = list(executor.map(evaluar_movimiento_global, args))

        mejor_puntaje, mejor_movimiento = max(resultados, key=lambda x: x[0])
        return mejor_movimiento

    def minimax(self, tablero, profundidad, es_maximizador, alfa, beta):
        key = self.generar_hash(tablero)
        if key in transposition_table and transposition_table[key][0] >= profundidad:
            return transposition_table[key][1]

        if profundidad == 0 or tablero.check_connection(self.jugador_id) or tablero.check_connection(self.oponente_id):
            score = self.evaluar(tablero)
            transposition_table[key] = (profundidad, score)
            return score

        movimientos = tablero.get_possible_moves()

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
            transposition_table[key] = (profundidad, maximo)
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
            transposition_table[key] = (profundidad, minimo)
            return minimo

    def generar_hash(self, tablero):
        plano = str(tablero.tablero)
        return sha256(plano.encode()).hexdigest()

    def evaluar(self, tablero):
        tam = tablero.tamano
        total_libres = sum(fila.count(0) for fila in tablero.tablero)

        def distancia_conexion(jugador_id):
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
                            nuevo_costo = costo + 1
                        else:
                            continue
                        if nuevo_costo < dist[nf][nc]:
                            dist[nf][nc] = nuevo_costo
                            heapq.heappush(heap, (nuevo_costo, nf, nc))

            if jugador_id == 1:
                return min(dist[tam - 1][col] for col in range(tam))
            else:
                return min(dist[fila][tam - 1] for fila in range(tam))

        def contar_puentes(jugador_id):
            bonus = 0
            direcciones = [(-1, 1), (1, -1), (-1, -1), (1, 1)]
            for fila in range(tam):
                for col in range(tam):
                    if tablero.tablero[fila][col] == jugador_id:
                        for df, dc in direcciones:
                            nf, nc = fila + 2*df, col + 2*dc
                            mf, mc = fila + df, col + dc
                            if 0 <= nf < tam and 0 <= nc < tam and 0 <= mf < tam and 0 <= mc < tam:
                                if tablero.tablero[nf][nc] == jugador_id and tablero.tablero[mf][mc] == 0:
                                    bonus += 1
            return bonus

        # Detecta si hay una jugada que une dos regiones propias no conectadas (doble amenaza)
        def detectar_doble_conexion(jugador_id):
            contador = 0
            for fila in range(tam):
                for col in range(tam):
                    if tablero.tablero[fila][col] == 0:
                        conexiones = 0
                        for df, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,1),(1,-1)]:
                            nf, nc = fila + df, col + dc
                            if 0 <= nf < tam and 0 <= nc < tam:
                                if tablero.tablero[nf][nc] == jugador_id:
                                    conexiones += 1
                        if conexiones >= 2:
                            contador += 1
            return contador

        d_propio = distancia_conexion(self.jugador_id)
        d_oponente = distancia_conexion(self.oponente_id)
        puente_bonus = contar_puentes(self.jugador_id)
        doble_amenaza = detectar_doble_conexion(self.jugador_id)

        centro = tam // 2
        centro_score = 0
        for fila in range(tam):
            for col in range(tam):
                if tablero.tablero[fila][col] == self.jugador_id:
                    centro_score += max(0, 5 - (abs(fila - centro) + abs(col - centro)))

        amenaza_oponente = -1000 if d_oponente <= 1 else 0

        if total_libres >= tam * tam * 0.7:
            return (d_oponente - d_propio) * 8 + centro_score + puente_bonus * 3 + doble_amenaza * 5 + amenaza_oponente
        elif total_libres >= tam * tam * 0.3:
            return (d_oponente - d_propio) * 12 + centro_score + puente_bonus * 3 + doble_amenaza * 5 + amenaza_oponente
        else:
            return (d_oponente - d_propio) * 15 + puente_bonus * 3 + doble_amenaza * 5 + amenaza_oponente


class HexBoard:
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

    def get_possible_moves(self) -> list:
        return [(fila, col) for fila in range(self.tamano)
                for col in range(self.tamano) if self.tablero[fila][col] == 0]

    def check_connection(self, jugador_id: int) -> bool:
        visitado = set()
        pila = []

        if jugador_id == 1:
            for col in range(self.tamano):
                if self.tablero[0][col] == jugador_id:
                    pila.append((0, col))
        else:
            for fila in range(self.tamano):
                if self.tablero[fila][0] == jugador_id:
                    pila.append((fila, 0))

        while pila:
            fila, col = pila.pop()
            if (fila, col) in visitado:
                continue
            visitado.add((fila, col))

            if jugador_id == 1 and fila == self.tamano - 1:
                return True
            if jugador_id == 2 and col == self.tamano - 1:
                return True

            for df, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]:
                nf, nc = fila + df, col + dc
                if 0 <= nf < self.tamano and 0 <= nc < self.tamano:
                    if self.tablero[nf][nc] == jugador_id and (nf, nc) not in visitado:
                        pila.append((nf, nc))

        return False
