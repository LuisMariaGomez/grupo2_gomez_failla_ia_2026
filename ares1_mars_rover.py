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
acciones:
    - se puede mover en las 4 direcciones cardinales, cada movimiento consume 1 unidad de bateria y 1 min
    - puede "sprintar" saltando una casilla y moviendose 2 en un minuto, pero 4 unidades de bateria
    - puede equipar un taladro, lo que consume 3 minuto y 1 unidad de bateria
    - juntar una muestra consume 2 minutos y 3 unidad de bateria (debe estar arriba de la muestra, tener el taladro correcto equipado y lugar en la capsula)
    - dejar la capsula con las muestras consume 1 minuto por muestra y 1 unidad de bateria (debe estar en la base)
    - recargar la bateria consume 4 minutos y restaura la bateria en 10 (no debe estar en zona de sombra)
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
        self.drill = None

    def actions(state):
        acciones_posibles = []
        if state.bateria <= 4:
            pass
    def cost(state1, action, state2):

        pass
    def heuristic(state):

        pass
    def is_goal(state):

        pass
    def result(state, action):

        pass

estado_incial = Rover(10, [(1,1), (2,2)], [(0,0), (3,3)], [(4,4), (5,5)], (0,0))