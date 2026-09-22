import sys
from pathlib import Path
from unittest.mock import patch
import sklearn.model_selection

# Parchear train_test_split sin stratify para evitar el error con datasets pequeños
_original_split = sklearn.model_selection.train_test_split

def _mock_split(*args, **kwargs):
    kwargs.pop('stratify', None)
    return _original_split(*args, **kwargs)

with patch('sklearn.model_selection.train_test_split', side_effect=_mock_split):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "semana04"))
    from preparar_dataset import calcular_dia_lluvioso


def test_dia_con_lluvia_devuelve_uno():
    assert calcular_dia_lluvioso(2.5) == 1


def test_dia_sin_lluvia_devuelve_cero():
    assert calcular_dia_lluvioso(0.0) == 0


def test_precipitacion_negativa_se_trata_como_sin_lluvia():
    assert calcular_dia_lluvioso(-1.0) == 0
