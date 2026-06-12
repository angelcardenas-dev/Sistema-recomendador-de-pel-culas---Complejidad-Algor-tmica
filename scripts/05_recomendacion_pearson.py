import sys
from pathlib import Path

import numpy as np
import pandas as pd


# Permite importar archivos desde la raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from backend.recommender.data_loader import (
    preparar_matriz_usuario_pelicula,
    obtener_catalogo_peliculas,
    validar_calificaciones_usuario,
    mostrar_resumen_datos,
)


def calcular_pearson_usuario(matriz, calificaciones_usuario_nuevo, user_id, min_comunes=2):
    """
    Calcula la correlación de Pearson entre el usuario nuevo
    y un usuario existente del dataset.

    Parámetros:
        matriz: matriz usuario-película
        calificaciones_usuario_nuevo: diccionario {movieId: rating}
        user_id: usuario existente de MovieLens
        min_comunes: mínimo de películas en común para comparar

    Retorna:
        similitud de Pearson y cantidad de películas en común
    """
    usuario_nuevo = pd.Series(calificaciones_usuario_nuevo, dtype=float)
    usuario_existente = matriz.loc[user_id].dropna()

    peliculas_comunes = usuario_nuevo.index.intersection(usuario_existente.index)

    if len(peliculas_comunes) < min_comunes:
        return 0, len(peliculas_comunes)

    ratings_nuevo = usuario_nuevo.loc[peliculas_comunes]
    ratings_existente = usuario_existente.loc[peliculas_comunes]

    # Si alguno no tiene variación en sus ratings, Pearson no es útil
    if ratings_nuevo.std() == 0 or ratings_existente.std() == 0:
        return 0, len(peliculas_comunes)

    similitud = np.corrcoef(ratings_nuevo, ratings_existente)[0, 1]

    if np.isnan(similitud):
        return 0, len(peliculas_comunes)

    return float(similitud), len(peliculas_comunes)


def obtener_usuarios_similares(
    matriz,
    calificaciones_usuario_nuevo,
    min_comunes=2,
    top_k=10
):
    """
    Compara el usuario nuevo contra todos los usuarios existentes.

    Retorna:
        DataFrame con los usuarios más similares.
    """
    usuarios_similares = []

    for user_id in matriz.index:
        similitud, comunes = calcular_pearson_usuario(
            matriz,
            calificaciones_usuario_nuevo,
            user_id,
            min_comunes=min_comunes
        )

        # Se consideran solo similitudes positivas
        if similitud > 0:
            usuarios_similares.append({
                "userId": user_id,
                "similitud": similitud,
                "peliculas_en_comun": comunes
            })

    df_similares = pd.DataFrame(usuarios_similares)

    if df_similares.empty:
        return df_similares

    df_similares = df_similares.sort_values(
        by=["similitud", "peliculas_en_comun"],
        ascending=False
    )

    return df_similares.head(top_k)


def recomendar_peliculas_pearson(
    matriz,
    movies,
    calificaciones_usuario_nuevo,
    top_k_usuarios=10,
    top_n_peliculas=10,
    rating_minimo=4.0,
    min_comunes=2
):
    """
    Recomienda películas usando usuarios similares por Pearson.

    Proceso:
        1. Busca usuarios similares al usuario nuevo.
        2. Revisa películas bien calificadas por esos usuarios.
        3. Excluye películas que el usuario nuevo ya calificó.
        4. Calcula un puntaje ponderado usando la similitud.
    """
    usuarios_similares = obtener_usuarios_similares(
        matriz,
        calificaciones_usuario_nuevo,
        min_comunes=min_comunes,
        top_k=top_k_usuarios
    )

    if usuarios_similares.empty:
        return pd.DataFrame(), usuarios_similares

    peliculas_ya_calificadas = set(calificaciones_usuario_nuevo.keys())
    puntajes = {}

    for _, fila in usuarios_similares.iterrows():
        user_id = fila["userId"]
        similitud = fila["similitud"]

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
            "cantidad_votos_similares": datos["cantidad_votos"]
        })

    df_recomendaciones = pd.DataFrame(recomendaciones)

    if df_recomendaciones.empty:
        return df_recomendaciones, usuarios_similares

    df_recomendaciones = df_recomendaciones.merge(
        movies,
        on="movieId",
        how="left"
    )

    df_recomendaciones = df_recomendaciones.sort_values(
        by=["score_pearson", "cantidad_votos_similares"],
        ascending=False
    )

    df_recomendaciones = df_recomendaciones.head(top_n_peliculas)

    columnas = [
        "movieId",
        "title",
        "genres",
        "score_pearson",
        "cantidad_votos_similares"
    ]

    return df_recomendaciones[columnas], usuarios_similares


def main():
    print("SISTEMA RECOMENDADOR - PRUEBA CON PEARSON")
    print("=" * 60)

    matriz, ratings, movies = preparar_matriz_usuario_pelicula()
    catalogo = obtener_catalogo_peliculas(movies)

    mostrar_resumen_datos(matriz, ratings, movies)

    # Usuario nuevo de prueba.
    # Estas películas pertenecen a MovieLens y suelen existir en ml-latest-small.
    # Puedes cambiar las calificaciones para probar otros perfiles.
    calificaciones_usuario_nuevo = {
        4993: 5.0,    # Lord of the Rings: The Fellowship of the Ring
        5952: 4.5,    # Lord of the Rings: The Two Towers
        7153: 5.0,    # Lord of the Rings: The Return of the King
        6377: 4.0,    # Finding Nemo
        58559: 4.5    # The Dark Knight
    }

    calificaciones_usuario_nuevo = validar_calificaciones_usuario(
        calificaciones_usuario_nuevo,
        matriz
    )

    print("\nPELÍCULAS CALIFICADAS POR EL USUARIO NUEVO")
    print("-" * 60)

    if not calificaciones_usuario_nuevo:
        print("No hay películas válidas para comparar.")
        print("Revisa si el dataset filtrado contiene los movieId usados.")
        return

    peliculas_usuario = movies[
        movies["movieId"].isin(calificaciones_usuario_nuevo.keys())
    ].copy()

    peliculas_usuario["rating_usuario_nuevo"] = peliculas_usuario["movieId"].map(
        calificaciones_usuario_nuevo
    )

    print(peliculas_usuario[["movieId", "title", "genres", "rating_usuario_nuevo"]])

    recomendaciones, usuarios_similares = recomendar_peliculas_pearson(
        matriz=matriz,
        movies=movies,
        calificaciones_usuario_nuevo=calificaciones_usuario_nuevo,
        top_k_usuarios=10,
        top_n_peliculas=10,
        rating_minimo=4.0,
        min_comunes=2
    )

    print("\nUSUARIOS MÁS SIMILARES")
    print("-" * 60)

    if usuarios_similares.empty:
        print("No se encontraron usuarios similares.")
    else:
        print(usuarios_similares)

    print("\nRECOMENDACIONES GENERADAS")
    print("-" * 60)

    if recomendaciones.empty:
        print("No se generaron recomendaciones.")
    else:
        print(recomendaciones)

        output_dir = PROJECT_ROOT / "data" / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / "recomendaciones_pearson.csv"
        recomendaciones.to_csv(output_path, index=False, encoding="utf-8-sig")

        print(f"\nArchivo generado: {output_path}")


if __name__ == "__main__":
    main()