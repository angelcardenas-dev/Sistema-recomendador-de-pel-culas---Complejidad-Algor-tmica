import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from backend.recommender.data_loader import (
    preparar_matriz_usuario_pelicula,
    obtener_catalogo_peliculas,
    buscar_peliculas,
    validar_calificaciones_usuario,
)


# Importaciones opcionales.
# Si las ramas de Pearson o género todavía no están fusionadas,
# el backend igual podrá funcionar con recomendaciones populares.
try:
    from backend.recommender.pearson import obtener_usuarios_similares
except Exception:
    obtener_usuarios_similares = None


try:
    from backend.recommender.genre_filter import (
        construir_perfil_generos,
        ajustar_ranking_con_genero,
    )
except Exception:
    construir_perfil_generos = None
    ajustar_ranking_con_genero = None


_DATA_CACHE = None


def cargar_datos():
    """
    Carga los datos una sola vez y los guarda en memoria.

    Esto evita leer los CSV en cada petición del backend.
    """
    global _DATA_CACHE

    if _DATA_CACHE is None:
        matriz, ratings, movies = preparar_matriz_usuario_pelicula()
        catalogo = obtener_catalogo_peliculas(movies)

        _DATA_CACHE = {
            "matriz": matriz,
            "ratings": ratings,
            "movies": movies,
            "catalogo": catalogo,
        }

    return _DATA_CACHE


def limpiar_dataframe_para_json(df):
    """
    Convierte un DataFrame a una lista de diccionarios compatibles con JSON.
    """
    if df.empty:
        return []

    df_limpio = df.replace({np.nan: None})

    registros = df_limpio.to_dict(orient="records")

    for registro in registros:
        for clave, valor in registro.items():
            if isinstance(valor, np.integer):
                registro[clave] = int(valor)
            elif isinstance(valor, np.floating):
                registro[clave] = float(valor)

    return registros


def buscar_peliculas_servicio(texto, limite=10):
    """
    Busca películas por título.
    """
    datos = cargar_datos()
    catalogo = datos["catalogo"]

    resultados = buscar_peliculas(
        catalogo=catalogo,
        texto_busqueda=texto,
        limite=limite
    )

    columnas = ["movieId", "title", "genres"]

    return limpiar_dataframe_para_json(resultados[columnas])


def obtener_peliculas_populares_servicio(limite=10):
    """
    Devuelve películas populares según promedio de rating y cantidad de votos.
    """
    datos = cargar_datos()
    ratings = datos["ratings"]
    movies = datos["movies"]

    estadisticas = ratings.groupby("movieId").agg(
        rating_promedio=("rating", "mean"),
        cantidad_votos=("rating", "count")
    ).reset_index()

    estadisticas = estadisticas[estadisticas["cantidad_votos"] >= 5]

    estadisticas["rating_promedio"] = estadisticas["rating_promedio"].round(3)

    populares = estadisticas.merge(
        movies,
        on="movieId",
        how="left"
    )

    populares = populares.sort_values(
        by=["rating_promedio", "cantidad_votos"],
        ascending=False
    ).head(limite)

    columnas = [
        "movieId",
        "title",
        "genres",
        "rating_promedio",
        "cantidad_votos"
    ]

    return limpiar_dataframe_para_json(populares[columnas])


def normalizar_calificaciones(calificaciones):
    """
    Convierte la lista recibida desde la API en un diccionario:

    Entrada:
        [
            {"movieId": 4993, "rating": 5.0},
            {"movieId": 5952, "rating": 4.5}
        ]

    Salida:
        {
            4993: 5.0,
            5952: 4.5
        }
    """
    calificaciones_dict = {}

    for item in calificaciones:
        movie_id = int(item["movieId"])
        rating = float(item["rating"])
        calificaciones_dict[movie_id] = rating

    datos = cargar_datos()
    matriz = datos["matriz"]

    calificaciones_validas = validar_calificaciones_usuario(
        calificaciones_dict,
        matriz
    )

    return calificaciones_validas


def generar_candidatos_populares(matriz, movies, calificaciones_usuario, top_n=30):
    """
    Genera recomendaciones populares como respaldo.

    Se usa cuando todavía no existe el módulo Pearson o cuando
    no se encuentran usuarios similares.
    """
    peliculas_ya_calificadas = set(calificaciones_usuario.keys())

    candidatos = []

    for movie_id in matriz.columns:
        if movie_id in peliculas_ya_calificadas:
            continue

        ratings_pelicula = matriz[movie_id].dropna()

        if len(ratings_pelicula) < 5:
            continue

        candidatos.append({
            "movieId": int(movie_id),
            "score_pearson": round(float(ratings_pelicula.mean()), 3),
            "cantidad_votos_similares": int(len(ratings_pelicula))
        })

    df_candidatos = pd.DataFrame(candidatos)

    if df_candidatos.empty:
        return df_candidatos

    df_candidatos = df_candidatos.merge(
        movies,
        on="movieId",
        how="left"
    )

    df_candidatos = df_candidatos.sort_values(
        by=["score_pearson", "cantidad_votos_similares"],
        ascending=False
    ).head(top_n)

    return df_candidatos


def generar_recomendaciones_pearson(
    matriz,
    movies,
    calificaciones_usuario,
    top_k_usuarios=10,
    top_n=10,
    rating_minimo=4.0,
    min_comunes=2
):
    """
    Genera recomendaciones usando usuarios similares por Pearson.

    Si el módulo Pearson todavía no está disponible,
    se usa una recomendación popular como respaldo.
    """
    if obtener_usuarios_similares is None:
        usuarios_similares = pd.DataFrame()
        recomendaciones = generar_candidatos_populares(
            matriz=matriz,
            movies=movies,
            calificaciones_usuario=calificaciones_usuario,
            top_n=top_n
        )

        return recomendaciones, usuarios_similares

    usuarios_similares = obtener_usuarios_similares(
        matriz=matriz,
        calificaciones_usuario_nuevo=calificaciones_usuario,
        min_comunes=min_comunes,
        top_k=top_k_usuarios
    )

    if usuarios_similares.empty:
        recomendaciones = generar_candidatos_populares(
            matriz=matriz,
            movies=movies,
            calificaciones_usuario=calificaciones_usuario,
            top_n=top_n
        )

        return recomendaciones, usuarios_similares

    peliculas_ya_calificadas = set(calificaciones_usuario.keys())
    puntajes = {}

    for _, fila in usuarios_similares.iterrows():
        user_id = fila["userId"]
        similitud = float(fila["similitud"])

        ratings_usuario = matriz.loc[user_id].dropna()

        for movie_id, rating in ratings_usuario.items():
            if movie_id in peliculas_ya_calificadas:
                continue

            if rating < rating_minimo:
                continue

            if movie_id not in puntajes:
                puntajes[movie_id] = {
                    "suma_ponderada": 0,
                    "suma_similitudes": 0,
                    "cantidad_votos": 0
                }

            puntajes[movie_id]["suma_ponderada"] += similitud * rating
            puntajes[movie_id]["suma_similitudes"] += abs(similitud)
            puntajes[movie_id]["cantidad_votos"] += 1

    recomendaciones = []

    for movie_id, datos in puntajes.items():
        if datos["suma_similitudes"] == 0:
            continue

        score = datos["suma_ponderada"] / datos["suma_similitudes"]

        recomendaciones.append({
            "movieId": int(movie_id),
            "score_pearson": round(score, 3),
            "cantidad_votos_similares": int(datos["cantidad_votos"])
        })

    df_recomendaciones = pd.DataFrame(recomendaciones)

    if df_recomendaciones.empty:
        df_recomendaciones = generar_candidatos_populares(
            matriz=matriz,
            movies=movies,
            calificaciones_usuario=calificaciones_usuario,
            top_n=top_n
        )

        return df_recomendaciones, usuarios_similares

    df_recomendaciones = df_recomendaciones.merge(
        movies,
        on="movieId",
        how="left"
    )

    df_recomendaciones = df_recomendaciones.sort_values(
        by=["score_pearson", "cantidad_votos_similares"],
        ascending=False
    ).head(top_n)

    return df_recomendaciones, usuarios_similares


def recomendar_servicio(
    calificaciones,
    top_n=10,
    top_k_usuarios=10
):
    """
    Servicio principal para recomendar películas.

    Recibe calificaciones desde la API y devuelve:
        - recomendaciones
        - usuarios similares
        - perfil de géneros si el módulo existe
    """
    datos = cargar_datos()

    matriz = datos["matriz"]
    movies = datos["movies"]

    calificaciones_validas = normalizar_calificaciones(calificaciones)

    if not calificaciones_validas:
        return {
            "mensaje": "No se recibieron calificaciones válidas.",
            "ratings_validos": 0,
            "usuarios_similares": [],
            "perfil_generos": {},
            "recommendations": []
        }

    recomendaciones, usuarios_similares = generar_recomendaciones_pearson(
        matriz=matriz,
        movies=movies,
        calificaciones_usuario=calificaciones_validas,
        top_k_usuarios=top_k_usuarios,
        top_n=top_n,
        rating_minimo=4.0,
        min_comunes=2
    )

    perfil_generos = {}

    if construir_perfil_generos is not None and ajustar_ranking_con_genero is not None:
        perfil_generos = construir_perfil_generos(
            movies=movies,
            calificaciones_usuario=calificaciones_validas,
            rating_minimo=4.0
        )

        recomendaciones = ajustar_ranking_con_genero(
            df_recomendaciones=recomendaciones,
            movies=movies,
            perfil_generos=perfil_generos,
            peso_pearson=0.75,
            peso_genero=0.25
        )
    else:
        if not recomendaciones.empty:
            recomendaciones["score_final"] = recomendaciones["score_pearson"]

    columnas_recomendaciones = [
        columna for columna in [
            "movieId",
            "title",
            "genres",
            "score_pearson",
            "score_genero",
            "score_final",
            "cantidad_votos_similares"
        ]
        if columna in recomendaciones.columns
    ]

    recomendaciones = recomendaciones[columnas_recomendaciones]

    return {
        "mensaje": "Recomendaciones generadas correctamente.",
        "ratings_validos": len(calificaciones_validas),
        "usuarios_similares": limpiar_dataframe_para_json(usuarios_similares),
        "perfil_generos": perfil_generos,
        "recommendations": limpiar_dataframe_para_json(recomendaciones)
    }