"""
App Streamlit — Predicción de lluvia (Semana 06, ISO46B)
==========================================================
Interfaz web simple que consume el modelo de producción generado en el
Laboratorio 06 (modelo_produccion.keras + escalador_produccion.pkl) para
predecir si lloverá mañana en Huancayo, a partir de temp_max, temp_min y
viento_max de hoy.

Este archivo es la evidencia de "frontend" del despliegue: un backend
(Flask o FastAPI, ya construidos en la guía y en el notebook de despliegue
aplicado) responde a solicitudes HTTP, y esta app ilustra cómo un usuario
final -sin saber nada de JSON ni de curl- podría consumir ese mismo modelo
a través de una interfaz visual.

Cómo ejecutarla (desde la carpeta semana06/, después de completar el
Laboratorio 06 y tener modelo_produccion.keras / escalador_produccion.pkl):

    pip install streamlit
    streamlit run app_streamlit.py

Se abrirá automáticamente en el navegador (normalmente http://localhost:8501).
"""

import json
import pickle
from pathlib import Path

import numpy as np
import streamlit as st

COLUMNAS_CARACTERISTICAS = ["temp_max", "temp_min", "viento_max"]

MODELO_PATH = Path("modelo_produccion.keras")
ESCALADOR_PATH = Path("escalador_produccion.pkl")
VERSION_INFO_PATH = Path("version_info_produccion.json")

st.set_page_config(
    page_title="Predicción de lluvia — Semana 06",
    page_icon="🌦️",
    layout="centered",
)


@st.cache_resource
def cargar_artefactos():
    """Carga el modelo, el escalador y los metadatos de versión UNA SOLA VEZ.

    @st.cache_resource asegura que, aunque el usuario mueva los sliders
    muchas veces, el modelo no se recargue en cada interacción -el mismo
    principio de "cargar una sola vez" que se enseñó para la API Flask/FastAPI.
    """
    if not MODELO_PATH.exists() or not ESCALADOR_PATH.exists():
        return None, None

    # Import diferido: evita cargar TensorFlow si los artefactos no existen todavía
    from tensorflow import keras

    modelo = keras.models.load_model(MODELO_PATH)
    with open(ESCALADOR_PATH, "rb") as f:
        escalador = pickle.load(f)

    return modelo, escalador


def cargar_metadatos():
    """Lee la ficha de versión SIN caché, para que un archivo recién creado
    aparezca al recargar la página sin reiniciar Streamlit."""
    if VERSION_INFO_PATH.exists():
        with open(VERSION_INFO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


st.title("🌦️ Predicción de lluvia — Huancayo")
st.caption(
    "Tecnologías Emergentes (ISO46B) · Semana 06 · Evidencia de despliegue "
    "(frontend sobre el modelo entrenado en el Laboratorio 06)"
)

modelo, escalador = cargar_artefactos()
metadatos = cargar_metadatos()

if modelo is None:
    st.error(
        "No se encontraron **modelo_produccion.keras** y/o "
        "**escalador_produccion.pkl** en esta carpeta.\n\n"
        "Antes de usar esta app, completa el Laboratorio 06 "
        "(`entrenar_modelo.py` → `entrenar_modelo_v2.py` → "
        "`comparar_versiones.py`), o copia aquí los archivos que esos "
        "scripts generan."
    )
    st.stop()

# --- Panel lateral: ficha del modelo ("model card" mínima) ---
with st.sidebar:
    st.header("📋 Ficha del modelo en producción")
    if metadatos:
        st.markdown(f"**Versión:** `{metadatos.get('version', '—')}`")
        st.markdown(f"**Entrenado:** `{metadatos.get('fecha_entrenamiento', '—')}`")
        st.markdown("**Hiperparámetros:**")
        st.json(metadatos.get("hiperparametros", {}))
        st.markdown("**Métricas (conjunto de prueba):**")
        metricas = metadatos.get("metricas", {})
        col1, col2 = st.columns(2)
        col1.metric("Accuracy", f"{metricas.get('accuracy', 0):.3f}")
        col2.metric("F1 (clase lluvia)", f"{metricas.get('f1_clase_1', 0):.3f}")
        col1.metric("Precision", f"{metricas.get('precision_clase_1', 0):.3f}")
        col2.metric("Recall", f"{metricas.get('recall_clase_1', 0):.3f}")
    else:
        st.info("No se encontró `version_info_produccion.json`.")

    st.divider()
    st.caption(
        "Esta app NO reentrena el modelo: solo consume los artefactos que "
        "ya guardó el pipeline de entrenamiento/versionado. Si el modelo "
        "cambia, basta con volver a ejecutar `comparar_versiones.py` y "
        "recargar esta página."
    )

# --- Formulario de entrada ---
st.subheader("Datos de hoy")

col_a, col_b, col_c = st.columns(3)
with col_a:
    temp_max = st.number_input(
        "Temp. máxima (°C)", min_value=-10.0, max_value=45.0, value=18.5, step=0.1
    )
with col_b:
    temp_min = st.number_input(
        "Temp. mínima (°C)", min_value=-15.0, max_value=30.0, value=4.2, step=0.1
    )
with col_c:
    viento_max = st.number_input(
        "Viento máximo (km/h)", min_value=0.0, max_value=150.0, value=12.0, step=0.5
    )

if st.button("🔮 Predecir lluvia de mañana", type="primary", use_container_width=True):
    entrada = {
        "temp_max": temp_max,
        "temp_min": temp_min,
        "viento_max": viento_max,
    }

    # Misma lógica de preprocesamiento que preprocesamiento_api.py / api.py:
    # construir el vector en el ORDEN correcto antes de escalar.
    vector = np.array([[entrada[c] for c in COLUMNAS_CARACTERISTICAS]])
    vector_escalado = escalador.transform(vector)
    probabilidad = float(modelo.predict(vector_escalado, verbose=0)[0][0])
    prediccion = "lluvia" if probabilidad > 0.5 else "no_lluvia"

    st.divider()
    if prediccion == "lluvia":
        st.warning(f"### ☔ Se predice **lluvia** mañana")
    else:
        st.success(f"### ☀️ Se predice **sin lluvia** mañana")

    st.progress(probabilidad, text=f"Probabilidad de lluvia: {probabilidad:.1%}")

    with st.expander("Ver la solicitud equivalente a la API (JSON)"):
        st.code(
            "POST /predecir\n"
            "Content-Type: application/json\n\n"
            f"{json.dumps(entrada, indent=2, ensure_ascii=False)}",
            language="http",
        )
        st.code(
            json.dumps(
                {"prediccion": prediccion, "probabilidad": round(probabilidad, 4)},
                indent=2,
                ensure_ascii=False,
            ),
            language="json",
        )
        st.caption(
            "Esta app llama al modelo directamente en memoria (sin red), "
            "pero el resultado es idéntico al que devolvería el endpoint "
            "/predecir de la API Flask o FastAPI construida en el "
            "Laboratorio 06 y en el notebook de despliegue aplicado, "
            "porque usa exactamente el mismo modelo, escalador y orden "
            "de características."
        )

st.divider()
st.caption(
    "💡 Para ver el mismo modelo servido como API (backend puro, sin "
    "interfaz), ejecuta `api.py` (Flask) o `api_fastapi.py` del notebook "
    "de despliegue aplicado, y consume `/predecir` con la colección de "
    "Postman incluida en el paquete de la semana."
)
