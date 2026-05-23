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
    
    # Las llenamos con ciclos for tradicionales
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

    # juntamos todas esas sub-listas
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
    
    #Dominios: todas las celdas disponibles (sin cráteres)
    dominios = [(f, c) for f in range(filas) for c in range(columnas) if (f, c) not in craters]

    constraints = []

    # en muchas de las restricciones comparaba si eran adyacente, porngo una funcion asi la llamo y listo
    def son_adyacentes(pos1, pos2):
        distancia = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        return distancia == 1
    
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
    
    def no_adyacentes(variables, values):
        pos_A = values[0]
        pos_B = values[1]
        return not son_adyacentes(pos_A, pos_B)
        
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

# def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):

#     tipos_modulos = ['habs', 'generators', 'labs', 'deposits', 'airlocks', 'vacio']
    
#     filas, columnas = camp_size
#     variables = [(f, c) for f in range(filas) for c in range(columnas) if (f, c) not in craters] # solo metemos las coordenadas de donde no haya crateres para la r2 y r1

#     domains = {celda: tipos_modulos for celda in variables}

#     contraints = []

#     # r1: Sin superposición: no puede haber dos módulos en la misma celda.
#     # Esto lo cocinamos al definir las variables como las coordenadas de las celdas

#     # r2: Cráteres intransitables: ningún módulo puede ubicarse en una celda marcada como cráter.
#     # No incluimos las coordenadas de los cráteres en las variables asi que chau

#     # r3: Esclusas en el borde: toda esclusa debe estar en el borde del mapa (primera o última fila, o primera o última columna), ya que necesita acceso directo al exterior.
#     def esclusas_en_borde(variables, values):
#         for (f, c), valor in tuple(variables, values):
#             if valor == 'airlocks' and (not (f == 0 or f == filas - 1 or c == 0 or c == columnas - 1)):
#                     return False
#         return True
#     contraints.append((tuple(tipos_modulos), esclusas_en_borde))
    
#     # r4: Habitacionales al interior: ningún módulo habitacional puede estar en el borde del mapa; necesitan una capa de protección contra los elementos marcianos.
#     def habs_al_interior(variables, values):
#         for (f, c), valor in tuple(variables, values):
#             if valor == 'habs' and (f == 0 or f == filas - 1 or c == 0 or c == columnas - 1):
#                     return False
#         return True
#     contraints.append((tuple(tipos_modulos), habs_al_interior))

    
#     # r5: Seguridad energética: un generador no puede ser adyacente a un módulo habitacional (riesgo de radiación para la tripulación).
#     def seguridad_energetica(variables, values):
#         for (f, c), valor in tuple(variables, values):
#             if valor == 'generators':
#                 for f_vecina, c_veciinia in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
#                     vecino = (f + f_vecina, c + c_veciinia)
#                     if vecino in variables:
#                         indice_vecino = variables.index(vecino)
#                         if values[indice_vecino] == 'habs':
#                             return False
#         return True
#     contraints.append((tuple(tipos_modulos), seguridad_energetica))

    
#     # r6: dos generadores no pueden ser vecino entre si
#     def separador_generadores(variables, values):
#         for (f, c), valor in tuple(variables, values):
#             if valor == 'generators':
#                 for f_vecina, c_veciinia in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
#                     vecino = (f + f_vecina, c + c_veciinia)
#                     if vecino in variables:
#                         indice_vecino = variables.index(vecino)
#                         if values[indice_vecino] == 'generators':
#                             return False
#         return True
#     contraints.append((tuple(tipos_modulos), separador_generadores))
    
#     # r7: cada laboratorio debe ser adyacente a al menos un depósito
#     def laboratorio_junto_deposito(variables, values):
#         for (f, c), valor in tuple(variables, values):
#             if valor == 'labs':
#                 for f_vecina, c_veciinia in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
#                     vecino = (f + f_vecina, c + c_veciinia)
#                     if vecino in variables:
#                         indice_vecino = variables.index(vecino)
#                         if values[indice_vecino] == 'deposits':
#                             return True
#         return False
#     contraints.append((tuple(tipos_modulos), laboratorio_junto_deposito))
    
#     # r8: cada módulo habitacional debe tener al menos una celda adyacente libre (sin módulo ni cráter)
#     def habitacion_vecino_libre(variables, values):
#         for (f, c), valor in tuple(variables, values):
#             if valor == 'habs':
#                 for f_vecina, c_veciinia in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
#                     vecino = (f + f_vecina, c + c_veciinia)
#                     if vecino in variables:
#                         indice_vecino = variables.index(vecino)
#                         if values[indice_vecino] == 'vacio':
#                             return True
#         return False
#     contraints.append((tuple(tipos_modulos), habitacion_vecino_libre))

#     problem = CspProblem(variables, domains, contraints)
#     solution = backtrack(problem)
#     return solution
