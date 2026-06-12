import sys
from pathlib import Path

import pandas as pd


# Permite importar módulos desde la raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from backend.recommender.data_loader import (
    preparar_matriz_usuario_pelicula,
    validar_calificaciones_usuario,
    mostrar_resumen_datos,
)

from backend.recommender.genre_filter import (
    construir_perfil_generos,
    obtener_generos_preferidos_texto,
    ajustar_ranking_con_genero,
)


def generar_candidatos_populares(matriz, movies, calificaciones_usuario, top_n=30):
    """
    Genera candidatos de prueba usando películas populares.

    Esta función sirve para probar el filtro por género sin depender todavía
    del módulo final de recomendación por Pearson.

    Proceso:
        1. Calcula rating promedio por película.
        2. Cuenta cantidad de votos.
        3. Excluye películas ya calificadas por el usuario nuevo.
        4. Selecciona películas con buena cantidad de votos.
    """
    peliculas_ya_calificadas = set(calificaciones_usuario.keys())

    estadisticas = []

    for movie_id in matriz.columns:
        if movie_id in peliculas_ya_calificadas:
            continue

        ratings_pelicula = matriz[movie_id].dropna()

        if len(ratings_pelicula) < 5:
            continue

        estadisticas.append({
            "movieId": int(movie_id),
            "score_pearson": round(float(ratings_pelicula.mean()), 3),
            "cantidad_votos_similares": int(len(ratings_pelicula))
        })

    candidatos = pd.DataFrame(estadisticas)

    if candidatos.empty:
        return candidatos

    candidatos = candidatos.merge(
        movies,
        on="movieId",
        how="left"
    )

    candidatos = candidatos.sort_values(
        by=["score_pearson", "cantidad_votos_similares"],
        ascending=False
    )

    return candidatos.head(top_n)


def main():
    print("PRUEBA DE FILTRO Y PONDERACIÓN POR GÉNERO")
    print("=" * 70)

    matriz, ratings, movies = preparar_matriz_usuario_pelicula()

    mostrar_resumen_datos(matriz, ratings, movies)

    # Usuario nuevo de prueba.
    # Perfil orientado a aventura, fantasía, acción y algo de animación.
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

    if not calificaciones_usuario_nuevo:
        print("No hay películas válidas para construir el perfil de género.")
        return

    print("\nPELÍCULAS CALIFICADAS POR EL USUARIO NUEVO")
    print("-" * 70)

    peliculas_usuario = movies[
        movies["movieId"].isin(calificaciones_usuario_nuevo.keys())
    ].copy()

    peliculas_usuario["rating_usuario_nuevo"] = peliculas_usuario["movieId"].map(
        calificaciones_usuario_nuevo
    )

    print(peliculas_usuario[[
        "movieId",
        "title",
        "genres",
        "rating_usuario_nuevo"
    ]])

    perfil_generos = construir_perfil_generos(
        movies=movies,
        calificaciones_usuario=calificaciones_usuario_nuevo,
        rating_minimo=4.0
    )

    print("\nPERFIL DE GÉNEROS DEL USUARIO")
    print("-" * 70)
    print(perfil_generos)

    print("\nGÉNEROS PREFERIDOS")
    print("-" * 70)
    print(obtener_generos_preferidos_texto(perfil_generos))

    candidatos = generar_candidatos_populares(
        matriz=matriz,
        movies=movies,
        calificaciones_usuario=calificaciones_usuario_nuevo,
        top_n=30
    )

    print("\nCANDIDATOS ANTES DE APLICAR GÉNERO")
    print("-" * 70)

    if candidatos.empty:
        print("No se generaron candidatos.")
        return

    print(candidatos[[
        "movieId",
        "title",
        "genres",
        "score_pearson",
        "cantidad_votos_similares"
    ]].head(10))

    recomendaciones_ajustadas = ajustar_ranking_con_genero(
        df_recomendaciones=candidatos,
        movies=movies,
        perfil_generos=perfil_generos,
        peso_pearson=0.75,
        peso_genero=0.25
    )

    print("\nRECOMENDACIONES AJUSTADAS POR GÉNERO")
    print("-" * 70)

    columnas = [
        "movieId",
        "title",
        "genres",
        "score_pearson",
        "score_genero",
        "score_final",
        "cantidad_votos_similares"
    ]

    print(recomendaciones_ajustadas[columnas].head(10))

    output_dir = PROJECT_ROOT / "data" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "recomendaciones_genero.csv"
    recomendaciones_ajustadas[columnas].to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nArchivo generado: {output_path}")


if __name__ == "__main__":
    main()