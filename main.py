from base2 import materias, profesores, horarios, salones
import random
# ---------------------------------------------
# PLANIFICADOR DE HORARIOS EN PYTHON (BACKTRACKING)
# ---------------------------------------------

from copy import deepcopy

# Importar todo desde base2
from base2 import (
    materias,
    profesores,
    horarios,
    salones,
)

# Variables dinámicas según usuario
preferencia_turno = None
preferencia_profesor = []
preferencia_semestre = None


# ==========================================
# FUNCIONES DE APOYO
# ==========================================

def materias_del_semestre(semestre):
    """Devuelve lista de materias del semestre elegido."""
    return [m for m, s in materias.items() if s == semestre]


def profesor_adecuado(materia):
    """Devuelve el profesor preferido si imparte la materia, sino otro profesor válido."""

    # 1. Profesor preferido
    for p in preferencia_profesor:
        if p in profesores and materia in profesores[p]:
            return p

    # 2. Cualquier profesor que la imparta
    for p, mats in profesores.items():
        if materia in mats:
            return p

    return None  # Ningún profesor imparte esta materia → horario imposible


def hay_conflicto(clase, clases_existentes):
    """
    Verifica traslapes por profesor o salón en día y hora.
    clase: (dia, inicio, fin, profesor, salon, materia)
    """
    dia1, i1, f1, profesor1, salon1, materia1 = clase

    for (dia2, i2, f2, profesor2, salon2, materia2) in clases_existentes:

        mismo_dia = (dia1 == dia2)
        traslape = not (f1 <= i2 or f2 <= i1)

        # Conflicto de profesor
        if profesor1 == profesor2 and mismo_dia and traslape:
            return True

        # Conflicto de salón
        if salon1 == salon2 and mismo_dia and traslape:
            return True

    return False


# ==========================================
# BACKTRACKING
# ==========================================

def asignar(materias_pendientes, clases_asignadas, soluciones, limite=5):
    """
    Intenta asignar horarios recursivamente.
    """

    # Si ya tenemos suficientes soluciones → detener búsqueda
    if len(soluciones) >= limite:
        return

    # Caso base: no quedan materias
    if not materias_pendientes:
        soluciones.append(deepcopy(clases_asignadas))
        return

    materia = materias_pendientes[0]
    profesor = profesor_adecuado(materia)

    if profesor is None:
        # Si ninguna profesor imparte esta materia → abortar rama
        return
    
    # Copias mezcladas para variedad
    horarios_shuffle = horarios[:]
    salones_shuffle = salones[:]

    random.shuffle(horarios_shuffle)
    random.shuffle(salones_shuffle)

    for dia, inicio, fin, turno in horarios_shuffle:

        if turno != preferencia_turno:
            continue

    for salon in salones_shuffle:
            nueva_clase = (dia, inicio, fin, profesor, salon, materia)

            # Verificar conflictos
            if not hay_conflicto(nueva_clase, clases_asignadas):

                clases_asignadas.append(nueva_clase)

                asignar(
                    materias_pendientes[1:],
                    clases_asignadas,
                    soluciones,
                    limite
                )

                clases_asignadas.pop()


def generar_horarios(limite=5):
    """Genera horarios válidos según las preferencias actuales."""
    materias_sem = materias_del_semestre(preferencia_semestre)
    soluciones = []
    asignar(materias_sem, [], soluciones, limite=limite)
    return soluciones


# ==========================================
# MODO INTERACTIVO
# ==========================================

def generar_horarios_interactivo():

    print("\n=== PLANIFICADOR DE HORARIOS ===\n")

    # --- SEMESTRE ---
    semestre = input("¿Qué semestre quieres cursar? (1-9): ").strip()

    mapa_semestres = {
        "1": "primer semestre",
        "2": "segundo semestre",
        "3": "tercer semestre",
        "4": "cuarto semestre",
        "5": "quinto semestre",
        "6": "sexto semestre",
        "7": "septimo semestre",
        "8": "octavo semestre",
        "9": "noveno semestre"
    }

    if semestre not in mapa_semestres:
        print("❌ Semestre inválido.")
        return

    global preferencia_semestre
    preferencia_semestre = mapa_semestres[semestre]

    # --- TURNO ---
    turno = input("¿Turno? (Matutino/Vespertino): ").strip()
    if turno not in ["Matutino", "Vespertino"]:
        print("❌ Turno inválido.")
        return

    global preferencia_turno
    preferencia_turno = turno

    # --- PROFESOR PREFERIDO ---
    profe = input("¿Profesor preferido? (deja vacío si no): ").strip()
    global preferencia_profesor

    if profe:
        # validar si imparte alguna materia del semestre elegido
        imparte_algo = False
        for materia, sem in materias.items():
            if sem == preferencia_semestre and profe in profesores and materia in profesores[profe]:
                imparte_algo = True
                break

        if not imparte_algo:
            print(f"\n El profesor “{profe}” NO imparte materias del semestre seleccionado.")
            print("    Se ignorará esta preferencia.\n")
            preferencia_profesor = []
        else:
            preferencia_profesor = [profe]
    else:
        preferencia_profesor = []

    # --- LÍMITE ---
    limite = input("¿Cuántas soluciones deseas generar? (ej. 5): ").strip()
    limite = int(limite) if limite.isdigit() else 5

    print("\nGenerando horarios...\n")

    soluciones = generar_horarios(limite)

    if not soluciones:
        print(" No se encontraron horarios válidos.")
        return

    print(f"\nSe generaron {len(soluciones)} horarios válidos:\n")

    for idx, sol in enumerate(soluciones, 1):
        print(f"\n--------- HORARIO {idx} ---------")
        for clase in sol:
            dia, ini, fin, prof, salon, mat = clase
            print(f"{mat} | {dia} {ini}-{fin} | {salon} | {prof}")


# ==========================================
# EJECUCIÓN DIRECTA
# ==========================================

if __name__ == "__main__":
    generar_horarios_interactivo()
