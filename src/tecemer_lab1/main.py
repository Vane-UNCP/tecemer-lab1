import requests


def obtener_chiste():
    try:
        respuesta = requests.get(
            "https://official-joke-api.appspot.com/random_joke", timeout=5
        )
        respuesta.raise_for_status()
        datos = respuesta.json()
        return f"{datos['setup']}\n{datos['punchline']}"
    except requests.RequestException as error:
        return f"No se pudo obtener el chiste: {error}"


if __name__ == "__main__":
    print(obtener_chiste())