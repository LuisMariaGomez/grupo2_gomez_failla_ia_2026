from sympy import python
from simpleai.search import CspProblem, backtrack

# ------------------------------------------------------------
# Funciones auxiliares
# ------------------------------------------------------------

def adjacent(pos1, pos2):
    """Retorna True si dos posiciones son adyacentes ortogonalmente."""
    r1, c1 = pos1
    r2, c2 = pos2
    return abs(r1 - r2) + abs(c1 - c2) == 1


def is_border(position, rows, cols):
    """Verifica si una posición está en el borde del mapa."""
    r, c = position
    return r == 0 or r == rows - 1 or c == 0 or c == cols - 1

# ------------------------------------------------------------
# Función principal
# ------------------------------------------------------------

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    rows, cols = camp_size

    # Todas las posiciones válidas
    all_positions = [
        (r, c)
        for r in range(rows)
        for c in range(cols)
        if (r, c) not in craters
    ]

    variables = []

    hab_vars = [f"hab_{i}" for i in range(habs)]
    gen_vars = [f"gen_{i}" for i in range(generators)]
    lab_vars = [f"lab_{i}" for i in range(labs)]
    dep_vars = [f"dep_{i}" for i in range(deposits)]
    air_vars = [f"air_{i}" for i in range(airlocks)]

    variables.extend(hab_vars)
    variables.extend(gen_vars)
    variables.extend(lab_vars)
    variables.extend(dep_vars)
    variables.extend(air_vars)

    domains = {}

    # Habitacionales: NO pueden estar en el borde
    interior_positions = [
        pos for pos in all_positions
        if not is_border(pos, rows, cols)
    ]

    # Esclusas: SOLO en el borde
    border_positions = [
        pos for pos in all_positions
        if is_border(pos, rows, cols)
    ]

    for var in hab_vars:
        domains[var] = interior_positions

    for var in gen_vars + lab_vars + dep_vars:
        domains[var] = all_positions

    for var in air_vars:
        domains[var] = border_positions

    # --------------------------------------------------------
    # Restricciones
    # --------------------------------------------------------

    constraints = []

    # 1) Sin superposición
    def different_positions(variables, values):
        return len(values) == len(set(values))

    constraints.append((variables, different_positions))

    # 2) Generadores no adyacentes a habitacionales
    def gen_not_adjacent_hab(vars_, values):
        gen_pos, hab_pos = values
        return not adjacent(gen_pos, hab_pos)

    for g in gen_vars:
        for h in hab_vars:
            constraints.append(((g, h), gen_not_adjacent_hab))

    # 3) Generadores no adyacentes entre sí
    def gens_not_adjacent(vars_, values):
        p1, p2 = values
        return not adjacent(p1, p2)

    for i in range(len(gen_vars)):
        for j in range(i + 1, len(gen_vars)):
            constraints.append(((gen_vars[i], gen_vars[j]), gens_not_adjacent))

    # 4) Cada laboratorio debe ser adyacente a un depósito
    def lab_adjacent_dep(vars_, values):
        lab_pos = values[0]
        dep_positions = values[1:]

        return any(adjacent(lab_pos, dep) for dep in dep_positions)

    for lab in lab_vars:
        constraints.append(([lab] + dep_vars, lab_adjacent_dep))

    # 5) Ruta de evacuación para habitacionales
    def hab_escape_route(vars_, values):
        hab_pos = values[0]
        other_positions = values[1:]

        r, c = hab_pos

        neighbors = [
            (r - 1, c),
            (r + 1, c),
            (r, c - 1),
            (r, c + 1),
        ]

        valid_neighbors = [
            n for n in neighbors
            if 0 <= n[0] < rows
            and 0 <= n[1] < cols
            and n not in craters
        ]

        occupied = set(other_positions)

        return any(n not in occupied for n in valid_neighbors)

    for hab in hab_vars:
        other_vars = [v for v in variables if v != hab]
        constraints.append(([hab] + other_vars, hab_escape_route))

    # --------------------------------------------------------
    # Verificaciones rápidas de imposibilidad
    # --------------------------------------------------------

    # No hay interiores suficientes para habitacionales
    if habs > len(interior_positions):
        return None

    # No hay bordes suficientes para esclusas
    if airlocks > len(border_positions):
        return None

    # No hay espacio total suficiente
    total_modules = habs + generators + labs + deposits + airlocks
    if total_modules > len(all_positions):
        return None

    # Si hay laboratorios pero no depósitos, es imposible
    if labs > 0 and deposits == 0:
        return None


    problem = CspProblem(variables, domains, constraints)

    solution = backtrack(problem)

    if solution is None:
        return None

    result = []

    for var, pos in solution.items():
        module_type = var.split("_")[0]
        r, c = pos
        result.append((module_type, r, c))

    return result
