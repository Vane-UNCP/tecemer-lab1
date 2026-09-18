
## Cierre de la Unidad I Semana 3
Herramienta de automatización: organizador.py clasifica y mueve archivos
de una carpeta en subcarpetas por tipo (Documentos, Imagenes, Videos,
Comprimidos, Otros), con modo de simulacion (--dry-run) mediante argparse.

Uso:
python organizador.py <carpeta> [--dry-run]

Pruebas: test_organizador.py cubre clasificacion, movimiento real y modo
simulacion, usando la fixture tmp_path de pytest para no afectar el
sistema de archivos real. Ejecutar con: pytest -v

## Cierre de la Unidad I Semana 3
Herramienta de automatización: organizador.py clasifica y mueve archivos
de una carpeta en subcarpetas por tipo (Documentos, Imagenes, Videos,
Comprimidos, Otros), con modo de simulacion (--dry-run) mediante argparse.

Uso:
python organizador.py <carpeta> [--dry-run]

Pruebas: test_organizador.py cubre clasificacion, movimiento real y modo
simulacion, usando la fixture tmp_path de pytest para no afectar el
sistema de archivos real. Ejecutar con: pytest -v
EO

git add organizador.py test_organizador.py README.md requirements.txt
git commit -m "docs: documenta organizador con estilo Google y cierra la Unidad I"
git push origin main
cat << 'EOF' >> README.md

## Cierre de la Unidad I Semana 3
Herramienta de automatización: organizador.py clasifica y mueve archivos
de una carpeta en subcarpetas por tipo (Documentos, Imagenes, Videos,
Comprimidos, Otros), con modo de simulacion (--dry-run) mediante argparse.

Uso:
python organizador.py <carpeta> [--dry-run]

Pruebas: test_organizador.py cubre clasificacion, movimiento real y modo
simulacion, usando la fixture tmp_path de pytest para no afectar el
sistema de archivos real. Ejecutar con: pytest -v
