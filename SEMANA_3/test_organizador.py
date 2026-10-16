"""Pruebas unitarias para organizador.py mediante pytest."""

import pytest
from pathlib import Path
from organizador import clasificar, organizar_carpeta

def test_clasificar():
    """Verifica que la clasificacion por extension funcione correctamente."""
    assert clasificar(Path("doc.pdf")) == "Documentos"
    assert clasificar(Path("foto.png")) == "Imagenes"
    assert clasificar(Path("desconocido.xyz")) == "Otros"

def test_organizar_carpeta_real(tmp_path):
    """Verifica el movimiento real de archivos en un directorio temporal."""
    (tmp_path / "reporte.pdf").touch()
    (tmp_path / "foto.jpg").touch()

    total = organizar_carpeta(tmp_path, simulacion=False)

    assert total == 2
    assert (tmp_path / "Documentos" / "reporte.pdf").exists()
    assert (tmp_path / "Imagenes" / "foto.jpg").exists()

def test_organizar_carpeta_simulacion(tmp_path):
    """Verifica que en modo simulacion no se muevan los archivos."""
    (tmp_path / "reporte.pdf").touch()

    total = organizar_carpeta(tmp_path, simulacion=True)

    assert total == 1
    assert (tmp_path / "reporte.pdf").exists()
    assert not (tmp_path / "Documentos").exists()