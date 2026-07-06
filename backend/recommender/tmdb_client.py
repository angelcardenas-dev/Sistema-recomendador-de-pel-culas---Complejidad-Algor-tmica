import json
import os
import re
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
CACHE_PATH = DATA_DIR / "tmdb_posters_cache.json"

load_dotenv(PROJECT_ROOT / ".env")

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_API_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


def cargar_cache():
    """
    Carga la caché local de pósters.
    Evita consultar TMDB repetidas veces por la misma película.
    """
    if not CACHE_PATH.exists():
        return {}

    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except Exception:
        return {}


def guardar_cache(cache):
    """
    Guarda la caché local de pósters.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(CACHE_PATH, "w", encoding="utf-8") as archivo:
        json.dump(cache, archivo, ensure_ascii=False, indent=2)


def construir_url_poster(poster_path: Optional[str]):
    """
    Construye la URL final del póster.
    """
    if not poster_path:
        return None

    return f"{TMDB_IMAGE_BASE}{poster_path}"


def extraer_anio(title: str):
    """
    Extrae el año del título MovieLens.

    Ejemplo:
        Amazing Spider-Man, The (2012) -> 2012
    """
    coincidencias = re.findall(r"\((\d{4})\)", title)

    if not coincidencias:
        return None

    return coincidencias[-1]


def limpiar_titulo_movielens(title: str):
    """
    Limpia títulos de MovieLens para mejorar la búsqueda en TMDB.

    Ejemplos:
        Amazing Spider-Man, The (2012) -> The Amazing Spider-Man
        Day of the Doctor, The (2013) -> The Day of the Doctor
    """
    titulo = re.sub(r"\(\d{4}\)", "", title).strip()
    titulo = re.sub(r"\s+", " ", titulo)

    articulos = {
        ", The": "The ",
        ", A": "A ",
        ", An": "An ",
    }

    for sufijo, prefijo in articulos.items():
        if titulo.endswith(sufijo):
            titulo = prefijo + titulo[: -len(sufijo)]

    return titulo.strip()


def obtener_url_poster_por_tmdb_id(tmdb_id, cache):
    """
    Obtiene el póster usando el ID exacto de TMDB.
    Esta es la opción más precisa.
    """
    if not TMDB_API_KEY:
        return None

    if pd.isna(tmdb_id):
        return None

    try:
        tmdb_id = int(tmdb_id)
    except Exception:
        return None

    cache_key = f"id:{tmdb_id}"

    if cache_key in cache:
        return cache[cache_key]

    try:
        url = f"{TMDB_API_BASE}/movie/{tmdb_id}"

        response = requests.get(
            url,
            params={
                "api_key": TMDB_API_KEY,
                "language": "en-US",
            },
            timeout=5,
        )

        if response.status_code != 200:
            cache[cache_key] = None
            return None

        data = response.json()
        poster_url = construir_url_poster(data.get("poster_path"))

        cache[cache_key] = poster_url
        return poster_url

    except Exception:
        cache[cache_key] = None
        return None


def buscar_url_poster_por_titulo(title: str, cache):
    """
    Busca el póster por título cuando no existe tmdbId.
    Es un respaldo.
    """
    if not TMDB_API_KEY:
        return None

    titulo_limpio = limpiar_titulo_movielens(title)
    anio = extraer_anio(title)

    cache_key = f"title:{titulo_limpio}:{anio}"

    if cache_key in cache:
        return cache[cache_key]

    try:
        params = {
            "api_key": TMDB_API_KEY,
            "query": titulo_limpio,
            "include_adult": "false",
            "language": "en-US",
            "page": 1,
        }

        if anio:
            params["year"] = anio

        response = requests.get(
            f"{TMDB_API_BASE}/search/movie",
            params=params,
            timeout=5,
        )

        if response.status_code != 200:
            cache[cache_key] = None
            return None

        data = response.json()
        resultados = data.get("results", [])

        poster_url = None

        for pelicula in resultados:
            poster_path = pelicula.get("poster_path")

            if poster_path:
                poster_url = construir_url_poster(poster_path)
                break

        cache[cache_key] = poster_url
        return poster_url

    except Exception:
        cache[cache_key] = None
        return None


def agregar_posters_a_dataframe(df, links=None):
    """
    Agrega la columna poster_url a un DataFrame de películas.

    Primero intenta usar links.csv:
        movieId -> tmdbId

    Si no encuentra tmdbId, busca por título.
    """
    if df.empty:
        df["poster_url"] = []
        return df

    df_resultado = df.copy()
    cache = cargar_cache()

    mapa_tmdb = {}

    if links is not None and not links.empty:
        links_limpio = links.dropna(subset=["tmdbId"])

        mapa_tmdb = {
            int(fila["movieId"]): int(fila["tmdbId"])
            for _, fila in links_limpio.iterrows()
        }

    poster_urls = []

    for _, fila in df_resultado.iterrows():
        movie_id = int(fila["movieId"])
        title = str(fila["title"])

        tmdb_id = mapa_tmdb.get(movie_id)

        poster_url = None

        if tmdb_id is not None:
            poster_url = obtener_url_poster_por_tmdb_id(tmdb_id, cache)

        if not poster_url:
            poster_url = buscar_url_poster_por_titulo(title, cache)

        poster_urls.append(poster_url)

    df_resultado["poster_url"] = poster_urls

    guardar_cache(cache)

    return df_resultado