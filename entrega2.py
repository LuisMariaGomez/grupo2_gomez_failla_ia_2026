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

    variables = var_habs + var_generators + var_labs + var_deposits + var_airlocks

    # dominio, todas las coor menos las que haya un crater asi ya sacamos r1 y r2 con esots planteos
    dominio = []
    for fila in range(filas):
        for columna in range(columnas):
            coordenada_a_verificar = (fila, columna)
            if(coordenada_a_verificar not in craters):
                dominio.append(coordenada_a_verificar)

    domains = {var: dominio for var in variables}
# problem = CspProblem(variables, domains, constraints)
# solution = backtrack(problem)
# return solution