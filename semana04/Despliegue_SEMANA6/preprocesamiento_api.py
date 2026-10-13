import numpy as np

COLUMNAS_CARACTERISTICAS = ["temp_max", "temp_min", "viento_max"]


def extraer_caracteristicas(datos_json):
    """Convierte el JSON recibido por la API en un arreglo numpy en el orden correcto.

    Lanza ValueError si falta alguna característica requerida.
    """
    faltantes = [c for c in COLUMNAS_CARACTERISTICAS if c not in datos_json]
    if faltantes:
        raise ValueError(f"Faltan las siguientes características: {faltantes}")

    valores = [float(datos_json[c]) for c in COLUMNAS_CARACTERISTICAS]
    return np.array([valores])
