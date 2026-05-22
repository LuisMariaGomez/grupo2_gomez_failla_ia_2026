
from simpleai.search import (
    SearchProblem,
    astar,
)
from simpleai.search.viewers import BaseViewer, WebViewer

class Rover(SearchProblem):
    def __init__(self, initial_state):
        super().__init__(initial_state)

    def actions(self, state):
        acciones_posibles = []
        movimientos_simples = [(0,1), (0,-1), (1,0), (-1,0)]
        movimientos_sprint = [(0,2), (0,-2), (2,0), (-2,0)]

        (
            posicion_rover,
            bateria,
            zonas_sombra,
            muestras_igneas,
            muestras_sedimentarias,
            taladro_equipado,
            muestras_almacenadas,
        ) = state

        cantidad_muestras = len(muestras_igneas) + len(muestras_sedimentarias)
        
        if bateria > 4:
            for (x, y) in movimientos_sprint:
                posicion_nueva = (posicion_rover[0] + x, posicion_rover[1] + y)
                acciones_posibles.append(("sobremarcha", posicion_nueva))

        if bateria > 3 and len(muestras_almacenadas) < 2 and posicion_rover in muestras_igneas and taladro_equipado == "termico":
            acciones_posibles.append(("recolectar", "ignea"))

        if bateria > 3 and len(muestras_almacenadas) < 2 and posicion_rover in muestras_sedimentarias and taladro_equipado == "percusion":
            acciones_posibles.append(("recolectar", "sedimentaria"))

        if (bateria > 1 and len(muestras_almacenadas) > 0) and (len(muestras_almacenadas) == 2 or cantidad_muestras == 0):
            acciones_posibles.append(("depositar", None))

        if bateria > 1 and posicion_rover in muestras_igneas and taladro_equipado != "termico":
            acciones_posibles.append(("equipar", "termico"))

        if bateria > 1 and posicion_rover in muestras_sedimentarias and taladro_equipado != "percusion":
            acciones_posibles.append(("equipar", "percusion"))

        if bateria > 1:
            for (x, y) in movimientos_simples:
                posicion_nueva = (posicion_rover[0] + x, posicion_rover[1] + y)
                acciones_posibles.append(("moverse", posicion_nueva))

        if posicion_rover not in zonas_sombra and bateria < 20:
            acciones_posibles.append(("recargar", None))

        return acciones_posibles
    
    def cost(self, state1, action, state2):
        muestras_almacenadas = state1[6]
        valor_accion = 0
        if action[0] == "sobremarcha":
            return 1 
        if action[0] == "moverse":
            return 1 
        if action[0] == "depositar":
            valor_accion = len(muestras_almacenadas)
        if action[0] == "recolectar":
            valor_accion = 2
        if action[0] == "equipar":
            valor_accion = 3
        if action[0] == "recargar":
            valor_accion = 4
        return valor_accion
    
    def heuristic(self, state):
        (
            posicion_rover,
            bateria,
            zonas_sombra,
            muestras_igneas,
            muestras_sedimentarias,
            taladro_equipado,
            muestras_almacenadas,
        ) = state

        muestras_restantes = muestras_igneas + muestras_sedimentarias
        if not muestras_restantes:
            return len(muestras_almacenadas)

        distancia_minima = min(
            abs(posicion_rover[0] - muestra[0]) + abs(posicion_rover[1] - muestra[1])
            for muestra in muestras_restantes
        )
        
        # --- NUEVA FÓRMULA DE MOVIMIENTO OPTIMIZADA ---
        # T >= max(dist/2, 1.3 * dist - 0.4 * bateria)
        estimacion_tiempo_viaje = max(
            distancia_minima / 2.0,
            1.3 * distancia_minima - 0.4 * bateria
        )
        # Truncamos (int) para redondear hacia abajo y garantizar que siga siendo Admisible
        movimientos_minimos = int(estimacion_tiempo_viaje)

        tiempo_base_muestras = 3 * len(muestras_restantes)
        tiempo_deposito_actuales = len(muestras_almacenadas)

        costo_taladro = 0
        if taladro_equipado is None: 
            costo_taladro = 3
        elif taladro_equipado == "termico" and muestras_sedimentarias:
            costo_taladro = 3
        elif taladro_equipado == "percusion" and muestras_igneas:
            costo_taladro = 3

        return movimientos_minimos + tiempo_base_muestras + tiempo_deposito_actuales + costo_taladro

    def is_goal(self, state):
        (
            _posicion_rover,
            _bateria,
            _zonas_sombra,
            muestras_igneas,
            muestras_sedimentarias,
            _taladro_equipado,
            muestras_almacenadas,
        ) = state

        # si no hay mas muestras y no hay muentras en la mochila
        if len(muestras_igneas) == 0 and len(muestras_sedimentarias) == 0 and len(muestras_almacenadas) == 0:
            return True
        return False
    
    def result(self, state, action):
        (
            posicion_rover,
            bateria,
            zonas_sombra,
            muestras_igneas,
            muestras_sedimentarias,
            taladro_equipado,
            muestras_almacenadas,
        ) = state

        tipo_accion, parametro = action
        muestras_igneas = list(muestras_igneas)
        muestras_sedimentarias = list(muestras_sedimentarias)
        muestras_almacenadas = list(muestras_almacenadas)

        if tipo_accion == "sobremarcha":
            bateria -= 4
            posicion_rover = parametro

        if tipo_accion == "recolectar":
            bateria -= 3
            muestras_almacenadas.append(parametro)
            if parametro == "ignea":
                muestras_igneas.remove(posicion_rover)
            else:
                muestras_sedimentarias.remove(posicion_rover)

        if tipo_accion == "depositar":
            bateria -= 1
            muestras_almacenadas = []

        if tipo_accion == "equipar":
            bateria -= 1
            taladro_equipado = parametro

        if tipo_accion == "moverse":
            bateria -= 1
            posicion_rover = parametro

        if tipo_accion == "recargar":
            bateria += 10
            if bateria > 20:
                bateria = 20 

        return (
            posicion_rover,
            bateria,
            zonas_sombra,
            tuple(muestras_igneas),
            tuple(muestras_sedimentarias),
            taladro_equipado,
            tuple(muestras_almacenadas),
        )
    
def planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
    estado_inicial = (
        rover_inicio,
        bateria_inicial,
        tuple(zonas_sombra),
        tuple(muestras_igneas),
        tuple(muestras_sedimentarias),
        "ninguno", #Taladro
        tuple(), #Muestras almacenadas
    )

    problema = Rover(estado_inicial)

    #viewer = WebViewer() # BaseViewer() para consola. IMPORTANTE: DESACTIVAR AL ENTREGAR
    resultado = astar(problema, graph_search=True) #, viewer=viewer)
    acciones = [accion for accion, estado in resultado.path() if accion is not None] #(problema.actions(estado_inicial))
    
    return acciones
