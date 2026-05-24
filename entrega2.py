from itertools import combinations
from simpleai.search import CspProblem, backtrack


def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    filas, columnas = camp_size

    # variables
    var_habs = [f'hab_{i}' for i in range(habs)]
    var_generators = [f'generator_{i}' for i in range(generators)]
    var_labs = [f'lab_{i}' for i in range(labs)]
    var_deposits = [f'deposit_{i}' for i in range(deposits)]
    var_airlocks = [f'airlock_{i}' for i in range(airlocks)]

    # para las comparaciones de vecinos
    vecinos_ortogonales = [(0,1), (0,-1),(1,0),(-1,0)]
        
    if (deposits == 0 and labs > 0): # hay una reestriccion que pide que todo lab tiene que tener un dep al lado, si no hay dep pero si labs, seria al cuete ver todo
        return None
    
    variables = var_habs + var_generators + var_labs + var_deposits + var_airlocks

    # dominio sacando los crateres y evitando que haga hab en el borde

    domains = {}
    for var in variables:
        dominio_var = []
        for f in range(filas):
            for c in range(columnas):
                coor = (f, c)
                
                #  r2: no pisar cráteres
                if coor in craters:
                    continue
                
                es_borde = (f == 0 or f == filas - 1 or c == 0 or c == columnas - 1) # la coor esta en el borte
                
                #  r4: habs no pueden ir en el borde
                if var.startswith('hab') and es_borde:
                    continue
                    
                # r3: Esclusas no pueden ir en el interior
                if var.startswith('air') and not es_borde:
                    continue
                    
                dominio_var.append(coor)
                
        # si a alguna variable no le quedó ningún lugar válido, es imposible armar el campamento
        if not dominio_var:
            return None
            
        domains[var] = dominio_var

    constraints = []

    # funcion de vecinos ya que se cansa de pedirlo

    def son_vecinos(c1, c2):
        f1, col1 = c1
        f2, col2 = c2
        return abs(f1 - f2) + abs(col1 - col2) == 1
    
    def no_vecinos(variables, values):
        return not son_vecinos(values[0], values[1])
    
    # r1: sin superposicion

    def diferentes(variables, values):
        return values[0] != values[1]
        
    for v1, v2 in combinations(variables, 2):   #todas las combinaciones de 2 que puede haber en lo que quedo de dominio
        constraints.append(((v1, v2), diferentes))

    # r5: ningun generador al lado de hab
        
    for g in var_generators:
        for h in var_habs:
            constraints.append(((g, h), no_vecinos))

    # r6: ningun generador al lado de otro

    for g1, g2 in combinations(var_generators, 2):
        constraints.append(((g1, g2), no_vecinos))

    # r7: cadena suministro cientifico
   
    def lab_junto_dep(variables, values):
        coord_lab = values[0]
        lista_deps = values[1:]
        for dep in lista_deps:
            if son_vecinos(coord_lab, dep):
                return True # hay un depósito vecino, zafa
        return False
        
    if var_deposits:
        for lab in var_labs:
            #  un laboratorio por vez contra todos los depósitos
            constraints.append(([lab] + var_deposits, lab_junto_dep))

    # r8: ruta de evacuacion

    # def ruta_evacuacion(variables, values):       LA HABIA PENSADO ASI PERO ERA PESADA

    #     for i in range(len(var_habs)):
    #         cantidad_vecinos = 0
    #         for crater in craters:          # revisamos si algun crater es vecino
    #             if (son_vecinos(crater, values[i])):
    #                 cantidad_vecinos += 1

    #         for j in range(len(values)):
    #             if (i!=j and son_vecinos(values[i], values[j])):
    #                 cantidad_vecinos += 1
    #         if (cantidad_vecinos == 4):     #Si tiene 4 vecinos significa que tiene uno en cada posicion ortogonal
    #             return False
    #     return True

    def ruta_evacuacion(variables, values):
        hab_coord = values[0]
        otros_modulos = values[1:]
        
        # ver los 4 costados
        for f_v, c_v in [(0,1), (0,-1), (1,0), (-1,0)]:
            vecino = (hab_coord[0] + f_v, hab_coord[1] + c_v)
            
            #  ver que el vecino no se caiga del mapa
            if 0 <= vecino[0] < filas and 0 <= vecino[1] < columnas:
                #  no sea un cráter ni esté ocupado por otro módulo
                if vecino not in craters and vecino not in otros_modulos:
                    return True # hay una salida
        return False # atrapadoooo

    for hab in var_habs: # cada habitacio contra todos los demás mpdulos
        otras_variables = [v for v in variables if v != hab] # todas las cosas menos la hab que agarramos
        constraints.append(([hab] + otras_variables, ruta_evacuacion))

    # final/formato

    problem = CspProblem(variables, domains, constraints)
    solution = backtrack(problem)

    if solution is None:
        return None
    
    solucion_final = []
    for nombre_variable, coordenada in solution.items():
        if nombre_variable.startswith('hab'): tipo = 'hab'
        elif nombre_variable.startswith('gen'): tipo = 'gen'
        elif nombre_variable.startswith('lab'): tipo = 'lab'
        elif nombre_variable.startswith('dep'): tipo = 'dep'
        elif nombre_variable.startswith('air'): tipo = 'air'
        
        solucion_final.append((tipo, coordenada[0], coordenada[1]))
        
    return solucion_final