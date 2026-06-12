import pandas as pd


def separar_generos(generos):
    """
    Separa los géneros de MovieLens.

    Ejemplo:
        "Action|Adventure|Sci-Fi"
        -> ["Action", "Adventure", "Sci-Fi"]
    """
    if pd.isna(generos):
        return []

    if generos == "(no genres listed)":
        return []

    return str(generos).split("|")


def obtener_generos_pelicula(movies, movie_id):
    """
    Obtiene la lista de géneros de una película según su movieId.
    """
    pelicula = movies[movies["movieId"] == movie_id]

    if pelicula.empty:
        return []

    generos = pelicula.iloc[0]["genres"]

    return separar_generos(generos)


def construir_perfil_generos(movies, calificaciones_usuario, rating_minimo=4.0):
    """
    Construye el perfil de géneros preferidos del usuario nuevo.

    Parámetros:
        movies: DataFrame con columnas movieId, title, genres
        calificaciones_usuario: diccionario {movieId: rating}
        rating_minimo: solo se consideran gustos fuertes desde este rating

    Retorna:
        Diccionario con peso por género.
        Ejemplo:
            {
                "Adventure": 0.35,
                "Fantasy": 0.30,
                "Action": 0.20,
                "Drama": 0.15
            }
    """
    pesos_generos = {}

    for movie_id, rating in calificaciones_usuario.items():
        if rating < rating_minimo:
            continue

        generos = obtener_generos_pelicula(movies, movie_id)

        # El peso aumenta según la calificación del usuario.
        # Si rating = 4.0, peso = 1.0
        # Si rating = 5.0, peso = 2.0
        peso_rating = rating - 3.0

        for genero in generos:
            if genero not in pesos_generos:
                pesos_generos[genero] = 0

            pesos_generos[genero] += peso_rating

    suma_total = sum(pesos_generos.values())

    if suma_total == 0:
        return {}

    perfil_normalizado = {
        genero: round(peso / suma_total, 4)
        for genero, peso in pesos_generos.items()
    }

    return dict(
        sorted(
            perfil_normalizado.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )


def calcular_score_genero(generos_pelicula, perfil_generos):
    """
    Calcula qué tanto coincide una película con el perfil de géneros del usuario.

    Parámetros:
        generos_pelicula: lista de géneros de una película
        perfil_generos: diccionario {genero: peso}

    Retorna:
        score entre 0 y 1 aproximadamente.
    """
    if not perfil_generos:
        return 0

    if not generos_pelicula:
        return 0

    score = 0

    for genero in generos_pelicula:
        if genero in perfil_generos:
            score += perfil_generos[genero]

    return round(score, 4)


def agregar_score_genero(df_recomendaciones, movies, perfil_generos):
    """
    Agrega una columna score_genero a un DataFrame de recomendaciones.

    El DataFrame debe tener una columna movieId.
    """
    if df_recomendaciones.empty:
        return df_recomendaciones

    recomendaciones = df_recomendaciones.copy()

    recomendaciones = recomendaciones.merge(
        movies[["movieId", "genres"]],
        on="movieId",
        how="left",
        suffixes=("", "_catalogo")
    )

    # Si ya existía una columna genres, se mantiene.
    # Si no existía, se usa genres_catalogo.
    if "genres" not in recomendaciones.columns and "genres_catalogo" in recomendaciones.columns:
        recomendaciones["genres"] = recomendaciones["genres_catalogo"]

    if "genres_catalogo" in recomendaciones.columns:
        recomendaciones["genres"] = recomendaciones["genres"].fillna(
            recomendaciones["genres_catalogo"]
        )

    recomendaciones["lista_generos"] = recomendaciones["genres"].apply(separar_generos)

    recomendaciones["score_genero"] = recomendaciones["lista_generos"].apply(
        lambda generos: calcular_score_genero(generos, perfil_generos)
    )

    recomendaciones = recomendaciones.drop(columns=["lista_generos"], errors="ignore")
    recomendaciones = recomendaciones.drop(columns=["genres_catalogo"], errors="ignore")

    return recomendaciones


def ajustar_ranking_con_genero(
    df_recomendaciones,
    movies,
    perfil_generos,
    peso_pearson=0.75,
    peso_genero=0.25
):
    """
    Ajusta el ranking final combinando Pearson y género.

    Fórmula:
        score_final = score_pearson_normalizado * peso_pearson
                      + score_genero * peso_genero

    Si no existe score_pearson, se usa solo score_genero.
    """
    if df_recomendaciones.empty:
        return df_recomendaciones

    recomendaciones = agregar_score_genero(
        df_recomendaciones,
        movies,
        perfil_generos
    )

    if "score_pearson" in recomendaciones.columns:
        max_pearson = recomendaciones["score_pearson"].max()

        if max_pearson > 0:
            recomendaciones["score_pearson_normalizado"] = (
                recomendaciones["score_pearson"] / max_pearson
            )
        else:
            recomendaciones["score_pearson_normalizado"] = 0

        recomendaciones["score_final"] = (
            recomendaciones["score_pearson_normalizado"] * peso_pearson
            + recomendaciones["score_genero"] * peso_genero
        )
    else:
        recomendaciones["score_final"] = recomendaciones["score_genero"]

    recomendaciones["score_final"] = recomendaciones["score_final"].round(4)

    recomendaciones = recomendaciones.sort_values(
        by=["score_final", "score_genero"],
        ascending=False
    ).reset_index(drop=True)

    return recomendaciones


def obtener_generos_preferidos_texto(perfil_generos, limite=5):
    """
    Retorna los géneros preferidos en formato de texto.
    """
    if not perfil_generos:
        return "No se detectaron géneros preferidos."

    principales = list(perfil_generos.items())[:limite]

    return ", ".join([
        f"{genero} ({peso})"
        for genero, peso in principales
    ])