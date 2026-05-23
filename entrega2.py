from itertools import combinations
from simpleai.search import(
    CspProblem,
    backtrack,
)

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    filas, columnas = camp_size

    #Variables: modulos pedidos
    modulos_hab = []
    modulos_gen = []
    modulos_lab = []
    modulos_dep = []
    modulos_air = []
    
    for i in range(habs):
        modulos_hab.append(f"hab_{i}")
        
    for i in range(generators):
        modulos_gen.append(f"gen_{i}")
        
    for i in range(labs):
        modulos_lab.append(f"lab_{i}")
        
    for i in range(deposits):
        modulos_dep.append(f"dep_{i}")
        
    for i in range(airlocks):
        modulos_air.append(f"air_{i}")

    # juntar todas esas sub-listas
    variables = []
    for m in modulos_hab: variables.append(m)
    for m in modulos_gen: variables.append(m)
    for m in modulos_lab: variables.append(m)
    for m in modulos_dep: variables.append(m)
    for m in modulos_air: variables.append(m)
    
    # Casos en los que el problema es imposible (asi ahorramos un tiempito je)
    # Si no nos piden construir ningún módulo, devolvemos lista vacía
    if len(variables) == 0:
        return []

    # Si hay laboratorios pero no hay depósitos, el problema es imposible (Regla 7)
    if labs > 0 and deposits == 0:
        return None
    
    #Dominios: todas las celdas disponibles (sin cráteres r2), se fija si es habitacion y esta en el borde (la descarta), y si es esclusa y no esta en el borde (la descarta)
    domains = {}
    for var in variables:
        coordenadas_validas = []
        for f in range(filas):
            for c in range(columnas):
                posicion = (f, c)
                
                # r2: Sin cráteres
                if posicion in craters:
                    continue
                
                es_borde = (f == 0 or f == filas - 1 or c == 0 or c == columnas - 1)
                
                # r4: Habs no pueden ir en el borde
                if var.startswith("hab") and es_borde:
                    continue
                
                # r2: Esclusas obligatoriamente en el borde
                if var.startswith("air") and not es_borde:
                    continue
                
                coordenadas_validas.append(posicion)
                
        domains[var] = coordenadas_validas
    constraints = []

    # en muchas de las restricciones comparaba si eran adyacente o no, pngo unas funciones asi la llamo y listo
    def son_adyacentes(pos1, pos2):
        distancia = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        return distancia == 1
    
    def no_adyacentes(variables, values):
        pos_A = values[0]
        pos_B = values[1]
        # Aquí sí llamamos a la función y negamos su resultado
        return not son_adyacentes(pos_A, pos_B)
    
    # r1: Sin superposición: no puede haber dos módulos en la misma celda.
    def posiciones_distintas(variables, values):
        pos_modulo_A = values[0]
        pos_modulo_B = values[1]
        return pos_modulo_A != pos_modulo_B

    # compara "todos contra todos"
    cantidad_variables = len(variables)
    
    for i in range(cantidad_variables):
        for j in range(i + 1, cantidad_variables): # Empieza en i+1 para no comparar un módulo consigo mismo
            modulo_A = variables[i]
            modulo_B = variables[j]
            
            constraints.append(((modulo_A, modulo_B), posiciones_distintas))
        
    # r5: Generador vs Habitacional (Listas distintas)
    for gen in modulos_gen:
        for hab in modulos_hab:
            constraints.append(((gen, hab), no_adyacentes))
            
    # r6: Generador vs Generador (Misma lista, usamos índices)
    cantidad_gen = len(modulos_gen)
    for i in range(cantidad_gen):
        for j in range(i + 1, cantidad_gen):
            gen_A = modulos_gen[i]
            gen_B = modulos_gen[j]
            constraints.append(((gen_A, gen_B), no_adyacentes))

    # r7: Laboratorio junto a depósito (Listas distintas)
    def lab_junto_deposito(variables, values):
        pos_lab = values[0]
        pos_dep = values[1]
        return son_adyacentes(pos_lab, pos_dep)
    
    for lab in modulos_lab:
        for dep in modulos_dep:
            constraints.append(((lab, dep), lab_junto_deposito))

    # r8: Habitación con vecino libre (Misma lista, usamos índices)
    def hab_con_vecino_libre(variables, values):
        pos_hab = values[0]
        for pos_vecina in [(pos_hab[0] - 1, pos_hab[1]), (pos_hab[0] + 1, pos_hab[1]), (pos_hab[0], pos_hab[1] - 1), (pos_hab[0], pos_hab[1] + 1)]:
            if pos_vecina not in craters and all(pos_vecina != values[i] for i in range(len(values))):
                return True
        return False
    constraints.append((tuple(modulos_hab), hab_con_vecino_libre))

    problem = CspProblem(variables, domains, constraints)
    solution = backtrack(problem)
    return solution