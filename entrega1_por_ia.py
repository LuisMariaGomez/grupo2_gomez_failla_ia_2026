from simpleai.search import SearchProblem, astar

# movimientos posibles:
# arriba, abajo, izquierda, derecha
MOVIMIENTOS = [
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
]


class RoverProblem(SearchProblem):

    def __init__(
        self,
        rover_inicio,
        bateria_inicial,
        zonas_sombra,
        muestras_igneas,
        muestras_sedimentarias,
    ):

        # guardamos las zonas donde NO se puede recargar
        self.zonas_sombra = set(zonas_sombra)

        # diccionario:
        # clave -> coordenada
        # valor -> tipo de muestra
        self.muestras = {}

        # agregamos muestras ígneas
        for muestra in muestras_igneas:
            self.muestras[muestra] = "ignea"

        # agregamos muestras sedimentarias
        for muestra in muestras_sedimentarias:
            self.muestras[muestra] = "sedimentaria"

        # cantidad total de muestras del mapa
        self.total_muestras = len(self.muestras)

        # limitar el espacio de búsqueda al área relevante del mapa
        filas = [rover_inicio[0]] + [coord[0] for coord in self.muestras]
        columnas = [rover_inicio[1]] + [coord[1] for coord in self.muestras]
        margen = 6
        self.min_fila = min(filas) - margen
        self.max_fila = max(filas) + margen
        self.min_columna = min(columnas) - margen
        self.max_columna = max(columnas) + margen

        estado_inicial = (
            rover_inicio,
            bateria_inicial,
            None,
            tuple(),
            0,
            False
        )

        super().__init__(estado_inicial)

    def actions(self, state):

        acciones = []

        posicion, bateria, taladro, recolectadas, carga, deposito = state

        fila, columna = posicion

        for df, dc in MOVIMIENTOS:

            nf = fila + df
            nc = columna + dc

            if bateria > 1 and self.min_fila <= nf <= self.max_fila and self.min_columna <= nc <= self.max_columna:
                acciones.append(("moverse", (nf, nc)))

        for df, dc in MOVIMIENTOS:

            nf = fila + (df * 2)
            nc = columna + (dc * 2)

            if bateria > 4 and self.min_fila <= nf <= self.max_fila and self.min_columna <= nc <= self.max_columna:
                acciones.append(("sobremarcha", (nf, nc)))

        quedan_ignea = any(
            self.muestras[coord] == "ignea"
            for coord in self.muestras
            if coord not in recolectadas
        )
        quedan_sedimentaria = any(
            self.muestras[coord] == "sedimentaria"
            for coord in self.muestras
            if coord not in recolectadas
        )

        if quedan_ignea and taladro != "termico" and bateria > 1:
            acciones.append(("equipar", "termico"))

        if quedan_sedimentaria and taladro != "percusion" and bateria > 1:
            acciones.append(("equipar", "percusion"))

        if (
            posicion in self.muestras
            and posicion not in recolectadas
            and carga < 2
            and bateria > 3
        ):

            tipo = self.muestras[posicion]

            # muestra ígnea -> requiere térmico
            if tipo == "ignea" and taladro == "termico":
                acciones.append(("recolectar", "ignea"))

            # sedimentaria -> requiere percusión
            if tipo == "sedimentaria" and taladro == "percusion":
                acciones.append(("recolectar", "sedimentaria"))

        restantes = self.total_muestras - len(recolectadas)

        # puede formar cápsula normal
        if carga == 2 and bateria > 1:
            acciones.append(("depositar", None))

        # excepción:
        # últimas muestras existentes
        elif carga > 0 and restantes == carga and bateria > 1:
            acciones.append(("depositar", None))

        if posicion not in self.zonas_sombra and bateria < 20:
            acciones.append(("recargar", None))

        return acciones

    def result(self, state, action):

        posicion, bateria, taladro, recolectadas, carga, deposito = state

        tipo, parametro = action

        # convertimos a lista temporal para poder modificar
        recolectadas = list(recolectadas)

        if tipo == "moverse":

            posicion = parametro
            bateria -= 1

        elif tipo == "sobremarcha":

            posicion = parametro
            bateria -= 4

        elif tipo == "equipar":

            taladro = parametro
            bateria -= 1

        elif tipo == "recolectar":

            # agregamos la muestra recolectada
            recolectadas.append(posicion)

            # aumenta la carga
            carga += 1
            bateria -= 3

        elif tipo == "depositar":

            # vacía completamente la carga
            carga = 0

            bateria -= 1

            # si ya se recolectaron todas las muestras
            # entonces el objetivo ya puede cumplirse
            if len(recolectadas) == self.total_muestras:
                deposito = True

        elif tipo == "recargar":

            # máximo 20 batería
            bateria = min(20, bateria + 10)

        return (
            posicion,
            bateria,
            taladro,
            tuple(sorted(recolectadas)),
            carga,
            deposito
        )

    def is_goal(self, state):

        _, _, _, recolectadas, carga, deposito = state

        if self.total_muestras == 0:
            return carga == 0

        return (
            len(recolectadas) == self.total_muestras
            and carga == 0
            and deposito
        )

    def cost(self, state, action, state2):

        tipo, _ = action

        if tipo == "moverse":
            return 1

        if tipo == "sobremarcha":
            return 1

        if tipo == "equipar":
            return 3

        if tipo == "recolectar":
            return 2

        if tipo == "depositar":

            carga = state[4]
            return carga

        if tipo == "recargar":
            return 4

        return 1
    
    # =========================================================
    # estima:
    # distancia mínima a una muestra restante
    # +
    # costo aproximado de recolectar
    # =========================================================
    def heuristic(self, state):

        posicion, _, taladro, recolectadas, carga, _ = state

        # buscamos muestras aún no recolectadas
        restantes = [
            coord
            for coord in self.muestras
            if coord not in recolectadas
        ]

        # si no quedan muestras -> ya estamos
        if not restantes:
            return carga

        fila, columna = posicion

        distancias = []

        # distancia Manhattan
        for rf, rc in restantes:

            distancia = abs(rf - fila) + abs(rc - columna)

            distancias.append((distancia + 1) // 2)

        dist_minima = min(distancias)

        quedan_ignea = any(
            self.muestras[coord] == "ignea"
            for coord in restantes
        )
        quedan_sedimentaria = any(
            self.muestras[coord] == "sedimentaria"
            for coord in restantes
        )

        costo_equipar = 0
        if quedan_ignea and quedan_sedimentaria:
            if taladro == "ninguno":
                costo_equipar = 6
            elif taladro in ("termico", "percusion"):
                costo_equipar = 3
        elif quedan_ignea:
            if taladro != "termico":
                costo_equipar = 3
        elif quedan_sedimentaria:
            if taladro != "percusion":
                costo_equipar = 3

        costo_recolectar = 2 * len(restantes)
        costo_depositar = 1

        return dist_minima + costo_equipar + costo_recolectar + costo_depositar


# =============================================================
# reconstruye la lista de acciones desde la solución de A*
# =============================================================

def reconstruir_acciones(resultado):

    acciones = []

    nodo = resultado

    while nodo.parent is not None:

        acciones.append(nodo.action)

        nodo = nodo.parent

    acciones.reverse()

    return acciones

# =============================================================
# FUNCIÓN PEDIDA POR LA CONSIGNA
# =============================================================

def planear_rover(
    rover_inicio=(0, 0),
    bateria_inicial=20,
    zonas_sombra=None,
    muestras_igneas=None,
    muestras_sedimentarias=None,
):

    # evitamos problemas con parámetros mutables
    if zonas_sombra is None:
        zonas_sombra = []

    if muestras_igneas is None:
        muestras_igneas = []

    if muestras_sedimentarias is None:
        muestras_sedimentarias = []

    # creamos el problema
    problema = RoverProblem(
        rover_inicio,
        bateria_inicial,
        zonas_sombra,
        muestras_igneas,
        muestras_sedimentarias,
    )

    # ejecutamos A*
    #
    # graph_search=True evita revisitar estados
    resultado = astar(problema, graph_search=True)

    # si no encuentra solución
    if resultado is None:
        return []

    # devolvemos solo la lista de acciones
    return reconstruir_acciones(resultado)