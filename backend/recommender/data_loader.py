from pathlib import Path

import pandas as pd


# Ruta raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Rutas principales
DATA_DIR = PROJECT_ROOT / "data"
MOVIELENS_DIR = DATA_DIR / "ml-latest-small"

RATINGS_PATH = MOVIELENS_DIR / "ratings.csv"
MOVIES_PATH = MOVIELENS_DIR / "movies.csv"
PELICULAS_2000_PATH = DATA_DIR / "peliculas_2000.csv"


def cargar_ratings():
    """
    Carga el archivo ratings.csv de MovieLens.

    Retorna:
        DataFrame con columnas:
        userId, movieId, rating, timestamp
    """
    if not RATINGS_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {RATINGS_PATH}\n"
            "Ejecuta primero scripts/01_descarga_dataset.py"
        )

    return pd.read_csv(RATINGS_PATH)


def cargar_movies():
    """
    Carga el archivo movies.csv de MovieLens.

    Retorna:
        DataFrame con columnas:
        movieId, title, genres
    """
    if not MOVIES_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {MOVIES_PATH}\n"
            "Ejecuta primero scripts/01_descarga_dataset.py"
        )

    return pd.read_csv(MOVIES_PATH)


def cargar_peliculas_filtradas():
    """
    Carga el archivo peliculas_2000.csv si existe.

    Este archivo fue generado en el preprocesamiento del Hito 1.
    Si no existe, retorna None.
    """
    if not PELICULAS_2000_PATH.exists():
        return None

    return pd.read_csv(PELICULAS_2000_PATH)


def preparar_matriz_usuario_pelicula():
    """
    Prepara la matriz usuario-película.

    Filas:
        userId

    Columnas:
        movieId

    Valores:
        rating

    Si existe peliculas_2000.csv, se usa como filtro para trabajar
    con el conjunto reducido del proyecto.
    """
    ratings = cargar_ratings()
    movies = cargar_movies()
    peliculas_filtradas = cargar_peliculas_filtradas()

    if peliculas_filtradas is not None and "movieId" in peliculas_filtradas.columns:
        movie_ids_validos = peliculas_filtradas["movieId"].unique()
        ratings = ratings[ratings["movieId"].isin(movie_ids_validos)]
        movies = movies[movies["movieId"].isin(movie_ids_validos)]

    matriz = ratings.pivot_table(
        index="userId",
        columns="movieId",
        values="rating"
    )

    return matriz, ratings, movies


def obtener_catalogo_peliculas(movies):
    """
    Ordena y prepara el catálogo de películas.
    """
    catalogo = movies.copy()
    catalogo = catalogo.sort_values("title").reset_index(drop=True)
    return catalogo


def buscar_peliculas(catalogo, texto_busqueda, limite=10):
    """
    Busca películas por texto dentro del título.

    Parámetros:
        catalogo: DataFrame de películas
        texto_busqueda: texto ingresado por el usuario
        limite: cantidad máxima de resultados

    Retorna:
        DataFrame con películas encontradas
    """
    texto_busqueda = texto_busqueda.lower().strip()

    resultados = catalogo[
        catalogo["title"].str.lower().str.contains(texto_busqueda, na=False)
    ]

    return resultados.head(limite)


def obtener_rating_usuario(matriz, user_id, movie_id):
    """
    Obtiene el rating de un usuario para una película.

    Si no existe rating, retorna None.
    """
    if user_id not in matriz.index:
        return None

    if movie_id not in matriz.columns:
        return None

    rating = matriz.loc[user_id, movie_id]

    if pd.isna(rating):
        return None

    return float(rating)


def validar_calificaciones_usuario(calificaciones_usuario, matriz):
    """
    Valida que las películas calificadas por el usuario nuevo
    existan dentro de la matriz usuario-película.

    Parámetros:
        calificaciones_usuario: diccionario {movieId: rating}
        matriz: matriz usuario-película

    Retorna:
        Diccionario filtrado con solo películas válidas.
    """
    peliculas_validas = set(matriz.columns)

    calificaciones_validas = {}

    for movie_id, rating in calificaciones_usuario.items():
        if movie_id in peliculas_validas:
            calificaciones_validas[movie_id] = float(rating)

    return calificaciones_validas


def mostrar_resumen_datos(matriz, ratings, movies):
    """
    Muestra un resumen básico de los datos cargados.
    """
    print("RESUMEN DEL DATASET")
    print("-" * 50)
    print(f"Usuarios en matriz: {matriz.shape[0]}")
    print(f"Películas en matriz: {matriz.shape[1]}")
    print(f"Cantidad de ratings: {len(ratings)}")
    print(f"Películas en catálogo: {len(movies)}")
    print("-" * 50)