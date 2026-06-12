from typing import List

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.recommender.service import (
    cargar_datos,
    buscar_peliculas_servicio,
    obtener_peliculas_populares_servicio,
    recomendar_servicio,
)


app = FastAPI(
    title="MovieRec Pro API",
    description="API para el sistema recomendador de películas usando MovieLens, Pearson y géneros.",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RatingInput(BaseModel):
    movieId: int = Field(..., description="ID de la película en MovieLens")
    rating: float = Field(..., ge=0.5, le=5.0, description="Calificación entre 0.5 y 5.0")


class RecommendationRequest(BaseModel):
    ratings: List[RatingInput]
    top_n: int = Field(10, ge=1, le=50, description="Cantidad de recomendaciones")
    top_k_users: int = Field(10, ge=1, le=100, description="Cantidad de usuarios similares")


@app.get("/")
def root():
    return {
        "mensaje": "MovieRec Pro API funcionando correctamente.",
        "documentacion": "/docs"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.get("/dataset/resumen")
def dataset_resumen():
    datos = cargar_datos()

    matriz = datos["matriz"]
    ratings = datos["ratings"]
    movies = datos["movies"]

    return {
        "usuarios": int(matriz.shape[0]),
        "peliculas_matriz": int(matriz.shape[1]),
        "ratings": int(len(ratings)),
        "peliculas_catalogo": int(len(movies))
    }


@app.get("/movies/search")
def search_movies(
    q: str = Query(..., min_length=1, description="Texto a buscar en el título"),
    limit: int = Query(10, ge=1, le=50, description="Cantidad máxima de resultados")
):
    resultados = buscar_peliculas_servicio(
        texto=q,
        limite=limit
    )

    return {
        "query": q,
        "total": len(resultados),
        "movies": resultados
    }


@app.get("/movies/popular")
def popular_movies(
    limit: int = Query(10, ge=1, le=50)
):
    peliculas = obtener_peliculas_populares_servicio(
        limite=limit
    )

    return {
        "total": len(peliculas),
        "movies": peliculas
    }


@app.post("/recommendations")
def recommendations(request: RecommendationRequest):
    calificaciones = [
        rating.model_dump()
        for rating in request.ratings
    ]

    resultado = recomendar_servicio(
        calificaciones=calificaciones,
        top_n=request.top_n,
        top_k_usuarios=request.top_k_users
    )

    return resultado