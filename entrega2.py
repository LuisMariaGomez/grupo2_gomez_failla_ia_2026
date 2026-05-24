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
        #  para 'variables' ver de traer solo las esclusas (ej: ['airlock_0', 'airlock_1'])
        # 'values' trae las coordenadas que SimpleAI quiere probar para esas esclusas
        for fila, columna in values:
            if((fila != 0 or fila != filas-1 or columna != 0 or columna != columnas-1)):  # si encuentra una que no este en el borde chau
                return False
        return True

    constraints.append((var_airlocks, esclusas_borde))

    # r4: habitaciones en el interior

    def hab_interiores(variables, values):
        #  para 'variables' ver de traer solo las hab
        # 'values' trae las coordenadas que SimpleAI quiere probar para esas habs
        for fila, columna in values:
            if((fila == 0 or fila == filas-1 or columna == 0 or columna == columnas-1)):  # lo mismo que antes pero al verez
                return False
        return True

    constraints.append((var_habs, hab_interiores))
    
    # los que siguen piden ver si son vecinos asi que hago una sola logica para ver si las cosas que pasan lo son
    def son_vecinos(coordenada1, coordenada2):
        fil_1, col_1 = coordenada1
        fil_2, col_2 = coordenada2
        vecinos_ortogonales = [(0,1), (0,-1),(1,0),(-1,0)]
        # vecinos_diagonales = [(1,1),(-1,-1),(1,-1),(-1,1)] # al final no

        for coordenada_ortogonal in vecinos_ortogonales:    #aca la onda es ver si son vecinos ortogonales
                    fil_co, col_co = coordenada_ortogonal
                    if (fil_1 + fil_co == fil_2) and (col_1 + col_co == col_2):
                        return True
        # for coordenada_diagonal in vecinos_diagonales:    #aca la onda es ver si son vecinos diagonales
                #     col_diag , fil_diag = coordenada_diagonal
                #     if (col_g + col_diag == col_h) and (fil_g + fil_diag == fil_h):
                #         return True
        return False


    # r5: seguridad energetica

    def seg_ener(variables, values):
        lista_gen = values[:len(var_generators)]
        lista_hab = values[len(var_generators):]
        for coordenada_gen in lista_gen:
            for coordenada_hab in lista_hab:
                if son_vecinos(coordenada_gen, coordenada_hab):
                    return False
        return True
    
    if var_generators and var_habs:
        constraints.append((var_generators + var_habs, seg_ener))

    # r6: aislamiento entre generadores

    def generadores_vecinos(variables, values):
        n = len(values)
        for i in range(n):
            for j in range(i+1,n):
                if (son_vecinos(values[i], values[j])):
                    return False
        return True

    constraints.append((var_generators, generadores_vecinos))

    # r7: cadena suministro cientifico
   
    def lab_junto_dep(variables, values):
        lista_labs = values[:len(var_labs)]
        lista_dep = values[len(var_labs):]

        for coord_lab in lista_labs:
            tiene_vecino_dep = False # ponemos que no tiene dep vecinos
            for coord_dep in lista_dep: #agarramos una coord de dep
                if(son_vecinos(coord_lab,coord_dep)): #vemos si son vecinos
                    tiene_vecino_dep = True #si lo son
                    break # termina con el 2do for y pasa al siguiente coor_lab en el 1er for y se resetea la variable tiene_vecino_dep eb false
            if (not tiene_vecino_dep): # cuando un lab no tenga vecinos se va a llegar aca con false, se entra y cerramos
                return False
        return True # si nunca llego a lo anterior con una lab "ailsado" de dep, todo okay

    constraints.append((var_labs + var_deposits, lab_junto_dep))

    # r8: ruta de evacuacion
    #  or (i!=j and values[j] in craters)

    def ruta_evacuacion(variables, values):

        for i in range(len(var_habs)):
            cantidad_vecinos = 0
            for crater in craters:          # revisamos si algun crater es vecino
                if (son_vecinos(crater, values[i])):
                    cantidad_vecinos += 1

            for j in range(len(values)):
                if (i!=j and son_vecinos(values[i], values[j])):
                    cantidad_vecinos += 1
            if (cantidad_vecinos == 4):     #Si tiene 4 vecinos significa que tiene uno en cada posicion ortogonal
                return False
        return True
    
    constraints.append((variables, ruta_evacuacion))

    problem = CspProblem(variables, domains, constraints)
    solution = backtrack(problem)

    if solution is None:
        return None
    
    solucion_final = []

    for nombre_variable, coordenada in solution.items():
        fila, columna = coordenada
        
        if nombre_variable.startswith('hab'):
            tipo = 'hab'
        elif nombre_variable.startswith('gen'):
            tipo = 'gen'
        elif nombre_variable.startswith('lab'):
            tipo = 'lab'
        elif nombre_variable.startswith('dep'):
            tipo = 'dep'
        elif nombre_variable.startswith('air'):
            tipo = 'air'
            
        solucion_final.append((tipo, fila, columna))
        
    return solucion_final