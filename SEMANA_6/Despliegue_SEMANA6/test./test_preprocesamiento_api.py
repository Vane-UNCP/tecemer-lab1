import sys, os
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from preprocesamiento_api import extraer_caracteristicas


def test_extraer_caracteristicas_orden_correcto():
    entrada = {"temp_max": 20.0, "temp_min": 5.0, "viento_max": 10.0}
    resultado = extraer_caracteristicas(entrada)
    assert resultado.shape == (1, 3)
    assert np.allclose(resultado, [[20.0, 5.0, 10.0]])


def test_extraer_caracteristicas_campo_faltante():
    entrada = {"temp_max": 20.0, "viento_max": 10.0}
    with pytest.raises(ValueError):
        extraer_caracteristicas(entrada)
