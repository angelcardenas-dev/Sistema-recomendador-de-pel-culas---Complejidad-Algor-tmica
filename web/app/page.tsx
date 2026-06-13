"use client";

import { useState } from "react";

import Hero from "@/components/Hero";
import HowItWorks from "@/components/HowItWorks";
import MovieSearch from "@/components/MovieSearch";
import RatingPanel from "@/components/RatingPanel";
import RecommendationResults from "@/components/RecommendationResults";
import { getRecommendations } from "@/lib/api";
import type { RatedMovie, RecommendationResponse } from "@/lib/types";

export default function Home() {
  const [ratedMovies, setRatedMovies] = useState<RatedMovie[]>([]);
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);
  const [error, setError] = useState("");

  function addMovie(movie: RatedMovie) {
    setRatedMovies((current) => {
      const exists = current.some((item) => item.movieId === movie.movieId);

      if (exists) {
        return current;
      }

      return [...current, movie];
    });
  }

  function updateRating(movieId: number, rating: number) {
    setRatedMovies((current) =>
      current.map((movie) =>
        movie.movieId === movieId ? { ...movie, rating } : movie
      )
    );
  }

  function removeMovie(movieId: number) {
    setRatedMovies((current) =>
      current.filter((movie) => movie.movieId !== movieId)
    );
  }

  async function generateRecommendations() {
    try {
      setLoadingRecommendations(true);
      setError("");

      const response = await getRecommendations(ratedMovies, 10, 10);
      setResult(response);
    } catch {
      setError(
        "No se pudo conectar con la API. Verifica que el backend esté corriendo en http://127.0.0.1:8000"
      );
    } finally {
      setLoadingRecommendations(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <Hero />
      <HowItWorks />

      <section id="recomendador" className="px-6 py-20">
        <div className="mx-auto max-w-7xl">
          <div className="mb-10">
            <h2 className="text-3xl font-black md:text-4xl">
              Prueba el recomendador
            </h2>
            <p className="mt-4 max-w-2xl text-slate-300">
              Busca películas, califícalas y genera recomendaciones usando la
              API desarrollada con FastAPI.
            </p>
          </div>

          {error && (
            <div className="mb-6 rounded-2xl border border-red-400/30 bg-red-500/10 p-4 text-red-200">
              {error}
            </div>
          )}

          <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
            <MovieSearch ratedMovies={ratedMovies} onAddMovie={addMovie} />

            <RatingPanel
              ratedMovies={ratedMovies}
              loading={loadingRecommendations}
              onUpdateRating={updateRating}
              onRemoveMovie={removeMovie}
              onGenerateRecommendations={generateRecommendations}
            />
          </div>

          <div className="mt-6">
            <RecommendationResults result={result} />
          </div>
        </div>
      </section>
    </main>
  );
}