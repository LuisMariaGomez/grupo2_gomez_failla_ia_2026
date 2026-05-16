"""
Introduccion:
el rover se manejara en una grilla
tiene marcada las posiciones de:
    - las muestras de roca
    - las zonas de sombra
objetivo:
    -juntar las muestras de roca en el menor tiempo posible y dejar las captulas con las muetras
restricciones:
    -solo puede llevar 2 muestras a la vez, debe dejar la capsula para juntar mas
    -hay dos tipos de rocas, para cada una hay un taladro, el rover no peude tener equipados ambos a la vez, debe equipar uno para juntar una muestra y luego cambiarlo por el otro para juntar la otra muestra
    -la bateria no debe llegar a 0
acciones: (de mayor a menor asi dependiendo de la bateria armamos la lista de acciones posibles)
    - Sprint (4 batería / 1 min) salta dos casillas en una direccion (revisar que no se salga del mapa)
    - Juntar muestra (3 batería / 2 min) listo
    - Dejar cápsula (1 batería por muestra / 1 min c/u)
    - Equipar taladro (1 batería / 3 min)
    - Movimiento normal (1 batería / 1 min)
    - Recargar batería (+10 batería / 4 min)

supongo un tablero de 10x10

notas:
    ver donde calculamos gasto de bateria
    agregar el cambio de taladro - 59
    agregar el cambio de taladro
    rover_inicio=(0, 0),
    bateria_inicial=20,
    Revisar --> Para armar una cápsula es necesario que el rover tenga 2 muestras cargadas, a menos que sea la última existente.
""" 
# from simpleai import SearchProblem, astar_search
# INITIAL = 
class Rover():
    def __init__(self, bateria, zonas_sombra, muestras_igneas, muestras_sedimentarias, posicion_incial):
        self.posicion = posicion_incial
        self.bateria = bateria
        self.zonas_sombra = tuple(zonas_sombra)
        self.muestras_igneas = tuple(muestras_igneas)
        self.muestras_sedimentarias = tuple(muestras_sedimentarias)
        self.muestras = []
        self.taladro = None

    def actions(state):
        acciones_posibles = []

        movimientos_simples = [(0,1), (0,-1), (1,0), (-1,0)]
        movimientos_sprint = [(0,2), (0,-2), (2,0), (-2,0)]
        posicion_actual = state.posicion
        
        if state.bateria > 4:
            for (x, y) in movimientos_sprint:
                posicion_nueva = (posicion_actual[0] + x, posicion_actual[1] + y)
                acciones_posibles.append(("sobremarcha", posicion_nueva))
            # for movimientos in movimientos_sprint:
            #     posicion_a_validar = (posicion_actual[0] + movimientos[0], posicion_actual[1] + movimientos[1])
            #     if  0 <= posicion_a_validar[0] <= 10 and 0 <= posicion_a_validar[1] <= 10:
            #         acciones_posibles.append(("sobremarcha", (posicion_a_validar[0], posicion_a_validar[1]))) 
        if state.bateria > 3 and len(state.muestras) < 2 and state.posicion in state.muestras_igneas and state.taladro == "termico":
            acciones_posibles.append(("recolectar", "ignea"))
        if state.bateria > 3 and len(state.muestras) < 2 and state.posicion in state.muestras_sedimentarias and state.taladro == "percusion":
            acciones_posibles.append(("recolectar", "sedimentaria"))
        if state.bateria > 2 and len(state.muestras) == 2:
                acciones_posibles.append(("depositar", None)) # ver calculo de bateria y eso
        if state.bateria > 1 and len(state.muestras) == 1 and len(state.muestras_igneas) + len(state.muestras_sedimentarias) == 0:
                acciones_posibles.append(("depositar", None)) # ver calculo de bateria y eso
        if state.bateria > 1 and state.posicion in state.muestras_igneas and state.taladro != "termico":
            acciones_posibles.append(("equipar", "termico"))
        if state.bateria > 1 and state.posicion in state.muestras_sedimentarias and state.taladro != "percusion":
            acciones_posibles.append(("equipar", "percusion"))
        if state.bateria > 1:
            for (x, y) in movimientos_simples:
                posicion_nueva = (posicion_actual[0] + x, posicion_actual[1] + y)
                acciones_posibles.append(("moverse", posicion_nueva))
        if (state.posicion not in state.zonas_sombra and state.bateria < 20):
            acciones_posibles.append(("recargar", None))
        return acciones_posibles
    
    def cost(state1, action, state2):
        if action[0] == "sobremarcha" or action[0] == "moverse":
            return 1
        if action[0] == "depositar":
            if len(state1.muestras) == 2:
                return 2
            else:
                return 1
        if action[0] == "recolectar":
            return 2
        if action[0] == "equipar":
            return 3
        if action[0] == "recargar":
            return 4
        else:
            raise ValueError(f"Accion desconocida: {action}")
    
    def heuristic(state):
        
        pass

    def is_goal(state):
        # si no hay mas muestras y no tengo muentras en la mochila
        if len(state.muestras_igneas) == 0 and len(state.muestras_sedimentarias) == 0 and len(state.muestras) == 0:
            return True
        return False
    
    def result(state, action):
        nuevo_estado = Rover(
            state.bateria,
            state.zonas_sombra,
            tuple(state.muestras_igneas),
            tuple(state.muestras_sedimentarias),
            state.posicion,
        )
        nuevo_estado.muestras = list(state.muestras)
        nuevo_estado.taladro = state.taladro

        if action[0] == "sobremarcha":
            nuevo_estado.bateria -= 4
            nuevo_estado.posicion = action[1]

        if action[0] == "recolectar":
            nuevo_estado.bateria -= 3
            nuevo_estado.muestras.append(action[1])
            if action[1] == "ignea":
                lista_temporal = list(nuevo_estado.muestras_igneas)
                lista_temporal.remove(nuevo_estado.posicion)
                nuevo_estado.muestras_igneas = tuple(lista_temporal)
            else:
                lista_temporal = list(nuevo_estado.muestras_sedimentarias)
                lista_temporal.remove(nuevo_estado.posicion)
                nuevo_estado.muestras_sedimentarias = tuple(lista_temporal)

        if action[0] == "depositar":
            nuevo_estado.bateria -= len(nuevo_estado.muestras)
            nuevo_estado.muestras = []

        if action[0] == "equipar":
            nuevo_estado.bateria -= 1
            nuevo_estado.taladro = action[1]

        if action[0] == "moverse":
            nuevo_estado.bateria -= 1
            nuevo_estado.posicion = action[1]

        if action[0] == "recargar":
            nuevo_estado.bateria = min(20, nuevo_estado.bateria + 10)

        return nuevo_estado