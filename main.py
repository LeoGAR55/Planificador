import random
from copy import deepcopy
from base2 import materias, profesores, salones, horarios, horas_materia

# Variables dinámicas
preferencia_turno = None
preferencia_profesor = []
preferencia_semestre = None


# ------------------------------------------
# UTILIDADES
# ------------------------------------------

def convertir_hora(hora_decimal):
    horas = int(hora_decimal)
    minutos = round((hora_decimal - horas) * 60)
    return f"{horas:02d}:{minutos:02d}"


def materias_del_semestre(semestre):
    return [m for m, s in materias.items() if s == semestre]


def profesor_adecuado_para_lista(materia):
    
    # Recorremos la lista de profesores para ver si esta dentro de la lista de profesores e imparte 
    # materias del semestre elegido
    for p in preferencia_profesor:
        if p in profesores and materia in profesores[p]:
            return p

    # Si no esta en la lista o no imparte la materia, elegimos uno al azar
    candidatos = [p for p, mats in profesores.items() if materia in mats]
    return random.choice(candidatos) if candidatos else None


def hay_conflicto(clase, clases_existentes):
    
    # Contruimos la clase a evaluar
    dia1, i1, f1, profesor1, salon1, materia1 = clase

    for (dia2, i2, f2, profesor2, salon2, materia2) in clases_existentes:

        mismo_dia = dia1 == dia2
        traslape = not (f1 <= i2 or f2 <= i1)

        if mismo_dia and traslape:
            # Conflicto de profesor
            if profesor1 == profesor2:
                return True
            # Conflicto de salón
            if salon1 == salon2:
                return True

        # Evitar que una materia tenga 2 bloques el mismo día
        if mismo_dia and materia1 == materia2:
            return True

    return False


# ------------------------------------------
# BACKTRACKING
# ------------------------------------------

def asignar(materias_pendientes, clases_asignadas, soluciones, limite=5):
    """
    materias_pendientes: lista de dicts con keys:
       {
         "materia": <str>,
         "profesor": <str>,
         "grupo": <str>  # usamos el nombre de la materia como group id
       }
    """

    if len(soluciones) >= limite:
        return

    if not materias_pendientes:
        soluciones.append(list(clases_asignadas))
        return

    # Elegir aleatoriamente una entrada pendiente (manteniendo el dict)
    entrada = random.choice(materias_pendientes)
    materia = entrada["materia"]
    profesor = entrada["profesor"]
    grupo = entrada["grupo"]

    # Creamos la lista restante (removemos sólo esa instancia)
    restantes = materias_pendientes[:]
    restantes.remove(entrada)

    # Si ya existe al menos un bloque asignado para esta materia, 
    # obtenemos su franja hora (inicio, fin) para forzar consistencia.
    slot_existente = None
    salon_fijo = None

    for (_d, ini, fin, profx, salx, matx) in clases_asignadas:
        if matx == grupo:        # si ya hay un bloque asignado de esta materia
            slot_existente = (ini, fin)
            salon_fijo = salx    # guardamos el salón que ya usa esta materia
            break


    horarios_shuffle = horarios[:]
    salones_shuffle = salones[:]
    random.shuffle(horarios_shuffle)
    random.shuffle(salones_shuffle)

    for dia, inicio_f, fin_f, turno in horarios_shuffle:

        # Respetar turno preferido
        if turno != preferencia_turno:
            continue

        # Si hay slot existente, forzamos mismo inicio/fin
        if slot_existente is not None:
            if not (round(inicio_f, 3) == round(slot_existente[0], 3) and round(fin_f, 3) == round(slot_existente[1], 3)):
                continue
            # además queremos día distinto (la función hay_conflicto ya evita mismo día)
            # pero mejor seguir intentando otros días de la misma franja
        # Si no hay slot existente, cualquier franja está bien (se fijará al primer bloque que se asigne)

        for salon in salones_shuffle:

            # Si ya existe un salón fijo, solo aceptar ese
            if salon_fijo is not None and salon != salon_fijo:
                continue

            nueva_clase = (dia, inicio_f, fin_f, profesor, salon, grupo)

            if hay_conflicto(nueva_clase, clases_asignadas):
                continue

            # Safeguard: check if exact same class is already assigned
            if nueva_clase in clases_asignadas:
                continue

            clases_asignadas.append(nueva_clase)
            asignar(restantes, clases_asignadas, soluciones, limite)
            clases_asignadas.pop()

            if len(soluciones) >= limite:
                return


def generar_horarios(limite=5):
    materias_sem = materias_del_semestre(preferencia_semestre)

    if not materias_sem:
        return []

    # --------------------------------------------
    # PRE-SELECCIONAR PROFESORES Y EXPANDIR A BLOQUES
    # --------------------------------------------

    duracion_bloque = 2 
    materias_pendientes = []

    for materia in materias_sem:
        horas = horas_materia.get(materia, 2)
        bloques = max(1, round(horas / duracion_bloque))

        # Elegimos UN profesor fijo por materia (respetando preferencias si aplica)
        profesor_fijo = profesor_adecuado_para_lista(materia)
        if profesor_fijo is None:
            # Si no hay profesor que imparta esta materia, no podemos generar horario válido
            # (podrías decidir ignorar la materia en lugar de abortar)
            return []

        # Añadimos N entradas (bloques) para la materia, todas con el mismo profesor y grupo
        for _ in range(bloques):
            materias_pendientes.append({
                "materia": materia,      # nombre de la materia (usado como id de grupo)
                "profesor": profesor_fijo,
                "grupo": materia
            })

    # Mezclamos para introducir variabilidad en el orden de asignación
    random.shuffle(materias_pendientes)

    soluciones = []
    asignar(materias_pendientes, [], soluciones, limite)

    # Filtrar duplicadas
    unicas = []
    vistas = set()
    for sol in soluciones:
        sol = list(set(sol))
        
        # Normalizamos la representación para comparar: ordenar por (materia, dia, inicio, fin, prof, salon)
        clave = tuple(sorted(sol, key=lambda x: (x[5], x[0], x[1], x[2], x[3], x[4])))
        if clave not in vistas:
            vistas.add(clave)
            unicas.append(sol)

    return unicas


# ------------------------------------------
# MODO INTERACTIVO
# ------------------------------------------

def generar_horarios_interactivo():

    print("\n=== PLANIFICADOR DE HORARIOS ===\n")

    semestre = input("¿Qué semestre quieres cursar? (1-9): ").strip()
    mapa_semestres = {
        "1": "primer semestre", "2": "segundo semestre", "3": "tercer semestre",
        "4": "cuarto semestre", "5": "quinto semestre", "6": "sexto semestre",
        "7": "septimo semestre", "8": "octavo semestre", "9": "noveno semestre"
    }

    if semestre not in mapa_semestres:
        print("Semestre inválido.")
        return

    global preferencia_semestre
    preferencia_semestre = mapa_semestres[semestre]

    turno = input("¿Turno? (Matutino/Vespertino): ").strip()
    if turno not in ["Matutino", "Vespertino"]:
        print("Turno inválido.")
        return

    global preferencia_turno
    preferencia_turno = turno

    profe = input("¿Profesor preferido? (deja vacío si no): ").strip()
    global preferencia_profesor

    if profe:
        imparte_algo = False
        for materia_n, sem_n in materias.items():
            if sem_n == preferencia_semestre and profe in profesores and materia_n in profesores[profe]:
                imparte_algo = True
                break

        if not imparte_algo:
            print(f"\nEl profesor “{profe}” NO imparte materias del semestre seleccionado. Se ignorará esta preferencia.\n")
            preferencia_profesor = []
        else:
            preferencia_profesor = [profe]
    else:
        preferencia_profesor = []

    limite = input("¿Cuántas soluciones deseas generar? (ej. 5): ").strip()
    limite = int(limite) if limite.isdigit() else 5

    print("\nGenerando horarios...\n")

    soluciones = generar_horarios(limite)

    if not soluciones:
        print("No se encontraron horarios válidos.")
        return

    print(f"\nSe generaron {len(soluciones)} horarios válidos:\n")

    for idx, sol in enumerate(soluciones, 1):
        print(f"\n--------- HORARIO {idx} ---------")
        for clase in sol:
            dia, ini, fin, prof, salon, mat = clase
            print(f"{mat} | {dia} {convertir_hora(ini)}-{convertir_hora(fin)} | {salon} | {prof}")

if __name__ == "__main__":
    generar_horarios_interactivo()
