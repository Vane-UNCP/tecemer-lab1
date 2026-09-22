from pathlib import Path

CATEGORIAS = {
    ".pdf": "Documentos", ".docx": "Documentos", ".txt": "Documentos",
    ".jpg": "Imagenes", ".jpeg": "Imagenes", ".png": "Imagenes",
    ".mp4": "Videos", ".mov": "Videos",
    ".zip": "Comprimidos", ".rar": "Comprimidos",
}
def clasificar(archivo):
    return CATEGORIAS.get(archivo.suffix.lower(), "Otros")
import shutil

def organizar_carpeta(carpeta, simulacion=False):
    movidos = 0
    for archivo in carpeta.iterdir():
        if archivo.is_dir() or archivo.name.startswith("."):
            continue
        categoria = clasificar(archivo)
        destino_carpeta = carpeta / categoria
        destino = destino_carpeta / archivo.name
        if simulacion:
            print(f"[SIMULACION] {archivo.name} -> {categoria}")
        else:
            destino_carpeta.mkdir(exist_ok=True)
            shutil.move(str(archivo), str(destino))
            print(f"Movido: {archivo.name} -> {categoria}")
        movidos += 1
    return movidos

import argparse
def main():
    parser = argparse.ArgumentParser(description="Organiza archivos por tipo.")
    parser.add_argument("carpeta", type=Path, help="Carpeta a organizar")
    parser.add_argument("--dry-run", action="store_true", help="Solo simula, no mueve archivos")
    args = parser.parse_args()

    total = organizar_carpeta(args.carpeta, simulacion=args.dry_run)
    print(f"Total de archivos procesados: {total}")
if __name__ == "__main__":
    main()

       