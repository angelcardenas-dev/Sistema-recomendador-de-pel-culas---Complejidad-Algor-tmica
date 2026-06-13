"""
Descarga y extracción del dataset MovieLens.

Antes de ejecutar este script, instalar dependencias con:
python -m pip install -r requirements.txt
"""

import zipfile
from pathlib import Path

import requests


DATA_DIR = Path("data")
DATASET_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
ZIP_PATH = DATA_DIR / "ml-latest-small.zip"


def descargar_dataset():
    DATA_DIR.mkdir(exist_ok=True)

    if ZIP_PATH.exists():
        print("El ZIP del dataset ya existe.")
        return

    print("Descargando dataset MovieLens...")
    response = requests.get(DATASET_URL, timeout=30)
    response.raise_for_status()

    ZIP_PATH.write_bytes(response.content)
    print("Dataset descargado correctamente.")


def extraer_dataset():
    destino = DATA_DIR / "ml-latest-small"

    if destino.exists():
        print("El dataset ya fue extraído.")
        return

    print("Extrayendo dataset...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(DATA_DIR)

    print("Dataset extraído correctamente.")


def main():
    descargar_dataset()
    extraer_dataset()


if __name__ == "__main__":
    main()