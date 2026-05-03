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
"""
from simpleai import SearchProblem, astar_search

INITIAL = 
class Rover():
    def __init__(self, bateria, zonas_sombra, muestras_igneas, muestras_sedimentarias, posicion_incial):
        self.posicion_incial = posicion_incial
        self.bateria = bateria
        self.zonas_sombra = zonas_sombra
        self.muestras_igneas = muestras_igneas
        self.muestras_sedimentarias = muestras_sedimentarias
        self.muestras = []
        self.taladro = None

    def actions(state):
        acciones_posibles = []
        if state.bateria > 4:
            acciones_posibles.append("sprintar")
        if state.bateria > 3:
            acciones_posibles.append("equipar_taladro")  
        if state.bateria > 2 and len(state.muestras) < 2 and state.posicion in state.muestras_igneas and state.taladro == "igneo":
            acciones_posibles.append("juntar_muestra_igneo")
        if state.bateria > 2 and len(state.muestras) < 2 and state.posicion in state.muestras_sedimentarias and state.taladro == "sedimentario":
            acciones_posibles.append("juntar_muestra_sedimentario")
        if state.bateria > len(state.muestras) and len(state.muestras) > 0:
            acciones_posibles.append("dejar_capsula")
        if state.bateria > 1:
            acciones_posibles.append("movimiento_normal")
        acciones_posibles.append("recargar_bateria")
        return acciones_posibles
    
    def cost(state1, action, state2):

        pass
    def heuristic(state):

        pass
    def is_goal(state):

        pass
    def result(state, action):

        pass

estado_incial = Rover(10, [(1,1), (2,2)], [(0,0), (3,3)], [(4,4), (5,5)], (0,0))