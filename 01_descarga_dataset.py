# ============================================================
# Verificación e instalación de librerías necesarias
# ============================================================
import os # para interactuar con el sistema operativo
import zipfile
import urllib.request # para realizar peticiones a internet

import importlib # Permite interactuar con el sistema de importaciones de Python de forma interna (para verificar si una librería existe)
import subprocess # Permite ejecutar comandos en la terminal o consola de tu computadora desde el propio código de Python.
import sys # Da acceso a variables y funciones específicas del sistema (como la ruta exacta del ejecutable de Python que se está usando).

librerias = {
    "pandas": "pandas",
    "numpy": "numpy",
    "networkx": "networkx",
    "matplotlib": "matplotlib",
    "pyvis": "pyvis",
    "openpyxl": "openpyxl",
    "ipykernel": "ipykernel",
    "customtkinter": "customtkinter",  # Para la interfaz
    "requests": "requests",            # Para las consultas a la API de TMDB
    "PIL": "pillow"                    # Para el manejo de imágenes y logos
}

def instalar_si_falta(paquete_import, paquete_pip):
    try:
        importlib.import_module(paquete_import)
        print(f"{paquete_pip} ya está instalado.")
    except ImportError:
        print(f"{paquete_pip} no está instalado. Instalando...")
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            paquete_pip
        ])
        print(f"{paquete_pip} instalado correctamente.")

for paquete_import, paquete_pip in librerias.items():
    instalar_si_falta(paquete_import, paquete_pip)


# ============================================================
# CONFIGURACIÓN INICIAL DE DIRECTORIOS
# ============================================================
# Definimos 'data' como la carpeta base del proyecto

if not os.path.exists('data'):
    os.makedirs('data')
    print("Carpeta 'data' creada con éxito.")

# 1. Descargar dataset movieLens
url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
zip_path = "ml-latest-small.zip"
extract_path = "data"

# Descargar el archivo ZIP
print(f"Descargando {zip_path}...")
urllib.request.urlretrieve(url, zip_path)

# Descomprimir el ZIP y almacenar los archivos en la carpeta 'ml-latest-small' y esta a a su vez dentro de la carpeta 'data'
with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(extract_path)

print(f"Dataset descomprimido en la carpeta: {extract_path}")

# 4. Verificación
# Listamos el contenido de data/ml-latest-small para asegurar que la ruta es correcta
# para tus siguientes scripts (02 y 03)
check_path = os.path.join(extract_path, "ml-latest-small")
if os.path.exists(check_path):
    print("Contenido verificado en:", check_path)
    print(os.listdir(check_path))
