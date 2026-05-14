from importlib import import_module


try:
    _simple_search = import_module("simpleai.search")
except ImportError:
    try:
        _simple_search = import_module("simpleia.search")
    except ImportError:
        _simple_search = None

if _simple_search is not None:
    SearchProblem = _simple_search.SearchProblem
    astar = _simple_search.astar
else:
        from heapq import heappop, heappush
        from itertools import count

        class SearchProblem:
            def __init__(self, initial_state):
                self.initial_state = initial_state

        class _SearchNode:
            def __init__(self, state, parent=None, action=None, cost=0):
                self.state = state
                self.parent = parent
                self.action = action
                self.cost = cost

            def path(self):
                node = self
                result = []
                while node is not None:
                    result.append((node.action, node.state))
                    node = node.parent
                return list(reversed(result))

        def astar(problem):
            tie_breaker = count()
            initial = _SearchNode(problem.initial_state)
            frontier = []
            heappush(frontier, (problem.heuristic(initial.state), next(tie_breaker), initial))
            best_cost = {initial.state: 0}

            while frontier:
                _, _, node = heappop(frontier)

                if node.cost != best_cost[node.state]:
                    continue

                if problem.is_goal(node.state):
                    return node

                for action in problem.actions(node.state):
                    new_state = problem.result(node.state, action)
                    new_cost = node.cost + problem.cost(node.state, action, new_state)

                    if new_cost < best_cost.get(new_state, float("inf")):
                        best_cost[new_state] = new_cost
                        new_node = _SearchNode(new_state, node, action, new_cost)
                        priority = new_cost + problem.heuristic(new_state)
                        heappush(frontier, (priority, next(tie_breaker), new_node))

            return None


MAX_BATERIA = 20
MOVIMIENTOS = ((-1, 0), (1, 0), (0, -1), (0, 1))
TIPO_A_TALADRO = {
    "ignea": "termico",
    "sedimentaria": "percusion",
}


class RoverProblem(SearchProblem):
    def __init__(self, inicio, bateria_inicial, zonas_sombra, igneas, sedimentarias):
        self.zonas_sombra = set(zonas_sombra)

        estado_inicial = (
            inicio,
            min(bateria_inicial, MAX_BATERIA),
            None,
            tuple(),
            frozenset(igneas),
            frozenset(sedimentarias),
        )

        super().__init__(estado_inicial)

    def puede_pagar(self, bateria, costo_bateria):
        return bateria - costo_bateria >= 1

    def actions(self, state):
        posicion, bateria, taladro, carga, igneas, sedimentarias = state
        acciones = []

        if self.puede_pagar(bateria, 1):
            for df, dc in MOVIMIENTOS:
                acciones.append(("moverse", (posicion[0] + df, posicion[1] + dc)))

            if taladro != "termico":
                acciones.append(("equipar", "termico"))
            if taladro != "percusion":
                acciones.append(("equipar", "percusion"))

            if carga and (len(carga) == 2 or not igneas and not sedimentarias):
                acciones.append(("depositar", None))

        if self.puede_pagar(bateria, 4):
            for df, dc in MOVIMIENTOS:
                acciones.append(("sobremarcha", (posicion[0] + 2 * df, posicion[1] + 2 * dc)))

        if len(carga) < 2 and self.puede_pagar(bateria, 3):
            if posicion in igneas and taladro == "termico":
                acciones.append(("recolectar", "ignea"))
            if posicion in sedimentarias and taladro == "percusion":
                acciones.append(("recolectar", "sedimentaria"))

        if posicion not in self.zonas_sombra and bateria < MAX_BATERIA:
            acciones.append(("recargar", None))

        return acciones

    def result(self, state, action):
        posicion, bateria, taladro, carga, igneas, sedimentarias = state
        tipo_accion, parametro = action
        carga = list(carga)
        igneas = set(igneas)
        sedimentarias = set(sedimentarias)

        if tipo_accion == "moverse":
            posicion = parametro
            bateria -= 1
        elif tipo_accion == "sobremarcha":
            posicion = parametro
            bateria -= 4
        elif tipo_accion == "equipar":
            taladro = parametro
            bateria -= 1
        elif tipo_accion == "recolectar":
            bateria -= 3
            carga.append(parametro)
            if parametro == "ignea":
                igneas.remove(posicion)
            else:
                sedimentarias.remove(posicion)
        elif tipo_accion == "depositar":
            bateria -= 1
            carga = []
        elif tipo_accion == "recargar":
            bateria = min(MAX_BATERIA, bateria + 10)

        return (
            posicion,
            bateria,
            taladro,
            tuple(sorted(carga)),
            frozenset(igneas),
            frozenset(sedimentarias),
        )

    def cost(self, state, action, state2):
        tipo_accion, _ = action

        if tipo_accion in ("moverse", "sobremarcha"):
            return 1
        if tipo_accion == "equipar":
            return 3
        if tipo_accion == "recolectar":
            return 2
        if tipo_accion == "depositar":
            return len(state[3])
        if tipo_accion == "recargar":
            return 4

        return 0

    def is_goal(self, state):
        _, _, _, carga, igneas, sedimentarias = state
        return not carga and not igneas and not sedimentarias

    def heuristic(self, state):
        posicion, _, _, carga, igneas, sedimentarias = state
        muestras_pendientes = list(igneas) + list(sedimentarias)

        costo_recoleccion_y_deposito = 3 * len(muestras_pendientes) + len(carga)
        if not muestras_pendientes:
            return costo_recoleccion_y_deposito

        distancia_minima = min(
            self.tiempo_minimo_de_movimiento(posicion, muestra)
            for muestra in muestras_pendientes
        )

        return distancia_minima + costo_recoleccion_y_deposito

    def tiempo_minimo_de_movimiento(self, origen, destino):
        distancia_filas = abs(origen[0] - destino[0])
        distancia_columnas = abs(origen[1] - destino[1])
        return (distancia_filas + 1) // 2 + (distancia_columnas + 1) // 2


def planear_rover(
    rover_inicio,
    bateria_inicial,
    zonas_sombra,
    muestras_igneas,
    muestras_sedimentarias,
):
    problema = RoverProblem(
        rover_inicio,
        bateria_inicial,
        zonas_sombra,
        muestras_igneas,
        muestras_sedimentarias,
    )

    resultado = astar(problema)
    if resultado is None:
        return []

    return [accion for accion, _ in resultado.path()[1:]]
