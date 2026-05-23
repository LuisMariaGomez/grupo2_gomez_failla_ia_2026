from itertools import combinations
from simpleai.search import(
    CspProblem,
    backtrack,
)

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    filas, columnas = camp_size

    # variables
    var_habs = [f'hab_{i}' for i in range(habs)]
    var_generators = [f'generator_{i}' for i in range(generators)]
    var_labs = [f'lab_{i}' for i in range(labs)]
    var_deposits = [f'deposit_{i}' for i in range(deposits)]
    var_airlocks = [f'airlock_{i}' for i in range(airlocks)]
        
    if (len(deposits) == 0 and len(var_labs > 0)): # hay una reestriccion que pide que todo lab tiene que tener un dep al lado, si no hay dep pero si labs, seria al cuete ver todo
        return None
    
    variables = var_habs + var_generators + var_labs + var_deposits + var_airlocks

    # dominio, todas las coor menos las que haya un crater asi ya sacamos r2 con eset planteo
    dominio = []
    for fila in range(filas):
        for columna in range(columnas):
            coordenada_a_verificar = (fila, columna)
            if(coordenada_a_verificar not in craters):
                dominio.append(coordenada_a_verificar)

    domains = {var: dominio for var in variables}   # Le estamos diciendo: "creá una clave que sea el nombre de la variable (var), y asignale como valor toda la lista de coordenadas que calculamos antes (dominio)".
    
    constraints = []

    # r1: sin superposicion

    def sin_superposicion(variables, values):   # values es una tupla que sAI esta probando --> ((0,0), (0,1), (0,0)), una forma de eliiminar dupliicados es con set()
        return len(values) == len(set(values))  # si el largo original es igual al del set, entonces no habia repetidos
    
    constraints.append((variables, sin_superposicion))

    # r3: Esclusas en el borde

    def esclusas_borde(variables, values):
        # 'variables' va a traer solo las esclusas (ej: ['airlock_0', 'airlock_1'])
        # 'values' trae las coordenadas que SimpleAI quiere probar para esas esclusas
        for fila, columna in values:
            if((fila != 0 or fila != filas-1 or columna != 0 or columna != columnas-1)):  # si encuentra una que no este en el borde chau
                return False
        return True

    constraints.append((var_airlocks, esclusas_borde))

    

# problem = CspProblem(variables, domains, constraints)
# solution = backtrack(problem)
# return solution