// Funciones para conectar el frontend con el backend
import type { Movie, RecommendationResponse, RatedMovie } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function searchMovies(query: string, limit = 8): Promise<Movie[]> {
  const response = await fetch(
    `${API_URL}/movies/search?q=${encodeURIComponent(query)}&limit=${limit}`
  );

  if (!response.ok) {
    throw new Error("No se pudo buscar películas.");
  }

  const data = await response.json();
  return data.movies || [];
}

export async function getPopularMovies(limit = 8): Promise<Movie[]> {
  const response = await fetch(`${API_URL}/movies/popular?limit=${limit}`);

  if (!response.ok) {
    throw new Error("No se pudo obtener películas populares.");
  }

  const data = await response.json();
  return data.movies || [];
}

export async function getRecommendations(
  ratedMovies: RatedMovie[],
  topN = 10,
  topKUsers = 10
): Promise<RecommendationResponse> {
  const body = {
    ratings: ratedMovies.map((movie) => ({
      movieId: movie.movieId,
      rating: movie.rating,
    })),
    top_n: topN,
    top_k_users: topKUsers,
  };

  const response = await fetch(`${API_URL}/recommendations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error("No se pudieron generar recomendaciones.");
  }

  return response.json();
}