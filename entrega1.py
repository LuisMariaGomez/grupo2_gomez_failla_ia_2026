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
        self.zonas_sombra = zonas_sombra
        self.muestras_igneas = muestras_igneas #[]
        self.muestras_sedimentarias = muestras_sedimentarias
        self.muestras = []
        self.taladro = None

    def actions(state):
        acciones_posibles = []

        movimientos_simples = [(0,1), (0,-1), (1,0), (-1,0)]
        movimientos_sprint = [(0,2), (0,-2), (2,0), (-2,0)]
        posicion_actual = state.posicion
        
        if state.bateria > 4:
            for movimientos in movimientos_sprint:
                posicion_a_validar = (posicion_actual[0] + movimientos[0], posicion_actual[1] + movimientos[1])
                if  0 <= posicion_a_validar[0] <= 10 and 0 <= posicion_a_validar[1] <= 10:
                    acciones_posibles.append(("sobremarcha", (posicion_a_validar[0], posicion_a_validar[1]))) 
        if state.bateria > 3 and len(state.muestras) < 2 and state.posicion in state.muestras_igneas and state.taladro == "igneo":
            acciones_posibles.append("recolectar", "ignea")
        if state.bateria > 3 and len(state.muestras) < 2 and state.posicion in state.muestras_sedimentarias and state.taladro == "sedimentario":
            acciones_posibles.append("recolectar", "sedimentaria")
        if state.bateria > 3 and len(state.muestras) == 2 or len(state.muestras_igneas)+len(state.muestras_sedimentarias) < 2 :
            acciones_posibles.append("entregar", None) # ver calculo de bateria y eso
        if state.bateria > 1 and state.posicion in state.muestras_igneas and state.taladro != "igneo":
            acciones_posibles.append("equipar", "termico")
        if state.bateria > 1 and state.posicion in state.muestras_sedimentarias and state.taladro != "sedimentario":
            acciones_posibles.append("equipar", "percusión")
        if state.bateria > 1:
            for movimientos in movimientos_simples:
                posicion_a_validar = (posicion_actual[0] + movimientos[0], posicion_actual[1] + movimientos[1])
                if  0 <= posicion_a_validar[0] <= 10 and 0 <= posicion_a_validar[1] <= 10:
                    acciones_posibles.append(("moverse", (posicion_a_validar[0], posicion_a_validar[1])))
        acciones_posibles.append("recargar_bateria")
        return acciones_posibles
    
    def cost(state1, action, state2):
        if action == "sobremarcha" or action == "moverse":
            return 1
        if action == "entregar":
            if len(state1.muestras) == 2:
                return 2
            else:
                return 1
        if action == "recolectar":
            return 2
        if action == "equipar":
            return 3
        if action == "recargar_bateria":
            return 4
        # por accion ir sumando tiempo
        # tiempo_minutos = 0
        # if action == "sobremarcha":
        #     tiempo_minutos += 1
        # if action == "recolectar":
        #     tiempo_minutos += 2
        # if action == "entregar":
        #     tiempo_minutos +=2
        # if action == "equipar":
        #     tiempo_minutos += 3
        # if action == "moverse":
        #     tiempo_minutos += 1
        # if action == "recargar_bateria":
        #     tiempo_minutos += 4
        # return tiempo_minutos
    
    def heuristic(state):
        
        pass

    def is_goal(state):
        # si no hay mas muestras y no tengo muentras en la mochila
        if len(state.muestras_igneas) == 0 and len(state.muestras_sedimentarias) == 0 and len(state.muestras) == 0:
            return True
        pass

    def result(state, action):
        #aca se sacaria bateria, las muestras del piso (la pos) y las muestras en la mochila
        if action == "sobremarcha":
            state.bateria -= 4
            state.posicion = action[1] #cambia la posicion a la que se mueve, la action seria ("sobremarcha", (x,y)), asi que agarro el (x,y)
        if action == "recolectar":
            state.bateria -= 3
            state.muestras.append(action[1]) # la action seria ("recolectar", "ignea") o ("recolectar", "sedimentaria"), asi que agarro el tipo de muestra
            if action[1] == "ignea":
                state.muestras_igneas.remove(state.posicion) # saco la muestra del piso, la pos es la del rover
            else:
                state.muestras_sedimentarias.remove(state.posicion) # saco la muestra del piso, la pos es la del rover
        if action == "entregar":
            if len(state.muestras) == 2: # si tengo 2 muestras, gasto 2 bateria
                state.bateria -= 2
            else:
                state.bateria -= 1 # si tengo 1 muestra, gasto 1 bateria, si tengo 2 muestras gasto 2 bateria
            state.muestras = [] # dejo las muestras en la capsula, asi que se vacia la mochila
        if action == "equipar":
            state.bateria -= 1
            state.taladro = action[1] # la action seria ("equipar", "termico") o ("equipar", "percusión"), asi que agarro el tipo de taladro
        if action == "moverse":
            state.bateria -= 1
            state.posicion = action[1] #cambia la posicion a la que se mueve, la action seria ("moverse", (x,y)), asi que agarro el (x,y)                
        if action == "recargar_bateria":
            state.bateria +=10 
        return state.bateria, state.posicion, state.muestras, state.taladro, state.muestras_igneas, state.muestras_sedimentarias
    
estado_incial = Rover(10, [(1,1), (2,2)], [(0,0), (3,3)], [(4,4), (5,5)], (0,0))