import pickle
from flask import Flask, request, jsonify
from tensorflow import keras

from preprocesamiento_api import extraer_caracteristicas

app = Flask(__name__)

# --- Carga ÚNICA, al iniciar el servidor ---
modelo = keras.models.load_model("modelo_produccion.keras")
with open("escalador_produccion.pkl", "rb") as f:
    escalador = pickle.load(f)


@app.route("/predecir", methods=["POST"])
def predecir():
    datos_json = request.get_json(silent=True)
    if datos_json is None:
        return jsonify({"error": "Se esperaba un cuerpo JSON válido"}), 400

    try:
        caracteristicas = extraer_caracteristicas(datos_json)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    caracteristicas_esc = escalador.transform(caracteristicas)
    probabilidad = float(modelo.predict(caracteristicas_esc, verbose=0)[0][0])
    prediccion = "lluvia" if probabilidad > 0.5 else "no_lluvia"

    return jsonify({"prediccion": prediccion, "probabilidad": round(probabilidad, 4)})


@app.route("/salud", methods=["GET"])
def salud():
    return jsonify({"estado": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
