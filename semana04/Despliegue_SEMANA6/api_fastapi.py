import pickle
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from tensorflow import keras

COLUMNAS_CARACTERISTICAS = ["temp_max", "temp_min", "viento_max"]

app = FastAPI(title="API de pronóstico de lluvia — Huancayo")
modelo = keras.models.load_model("modelo_produccion.keras")
with open("escalador_produccion.pkl", "rb") as f:
    escalador = pickle.load(f)


class DatosClima(BaseModel):
    temp_max: float
    temp_min: float
    viento_max: float


@app.post("/predecir")
def predecir(datos: DatosClima):
    caracteristicas = np.array([[datos.temp_max, datos.temp_min, datos.viento_max]])
    caracteristicas_esc = escalador.transform(caracteristicas)
    probabilidad = float(modelo.predict(caracteristicas_esc, verbose=0)[0][0])
    prediccion = "lluvia" if probabilidad > 0.5 else "no_lluvia"
    return {"prediccion": prediccion, "probabilidad": round(probabilidad, 4)}


@app.get("/salud")
def salud():
    return {"estado": "ok"}
