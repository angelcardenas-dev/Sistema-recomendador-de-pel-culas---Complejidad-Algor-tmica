// Resultados de recomendaciones
"use client";

import { Award, Users } from "lucide-react";

import type { RecommendationResponse } from "@/lib/types";
import MovieCard from "./MovieCard";

type RecommendationResultsProps = {
  result: RecommendationResponse | null;
};

export default function RecommendationResults({
  result,
}: RecommendationResultsProps) {
  if (!result) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 shadow-2xl">
        <h2 className="text-2xl font-black">Resultados</h2>
        <p className="mt-3 text-slate-400">
          Aquí aparecerán las películas recomendadas después de enviar tus
          calificaciones.
        </p>
      </div>
    );
  }

  const generos = Object.entries(result.perfil_generos || {}).slice(0, 6);

  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 shadow-2xl">
      <div className="flex items-center gap-3">
        <div className="rounded-2xl bg-cyan-400/10 p-3 text-cyan-300">
          <Award />
        </div>
        <div>
          <h2 className="text-2xl font-black">Recomendaciones</h2>
          <p className="text-sm text-slate-400">{result.mensaje}</p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl bg-slate-950/80 p-4">
          <p className="text-sm text-slate-400">Ratings válidos</p>
          <p className="mt-1 text-3xl font-black text-cyan-300">
            {result.ratings_validos}
          </p>
        </div>

        <div className="rounded-2xl bg-slate-950/80 p-4">
          <p className="text-sm text-slate-400">Usuarios similares</p>
          <p className="mt-1 text-3xl font-black text-violet-300">
            {result.usuarios_similares?.length || 0}
          </p>
        </div>

        <div className="rounded-2xl bg-slate-950/80 p-4">
          <p className="text-sm text-slate-400">Recomendaciones</p>
          <p className="mt-1 text-3xl font-black text-yellow-300">
            {result.recommendations?.length || 0}
          </p>
        </div>
      </div>

      {generos.length > 0 && (
        <div className="mt-6">
          <h3 className="font-bold">Perfil de géneros detectado</h3>

          <div className="mt-3 flex flex-wrap gap-2">
            {generos.map(([genre, score]) => (
              <span
                key={genre}
                className="rounded-full bg-cyan-400/10 px-4 py-2 text-sm text-cyan-200"
              >
                {genre}: {score}
              </span>
            ))}
          </div>
        </div>
      )}

      {result.usuarios_similares?.length > 0 && (
        <div className="mt-6 rounded-2xl bg-slate-950/80 p-4">
          <div className="mb-3 flex items-center gap-2 text-slate-200">
            <Users size={18} />
            <h3 className="font-bold">Top usuarios similares</h3>
          </div>

          <div className="grid gap-3 md:grid-cols-5">
            {result.usuarios_similares.slice(0, 5).map((user) => (
              <div
                key={user.userId}
                className="rounded-xl border border-white/10 p-3 text-sm"
              >
                <p className="font-bold">Usuario {user.userId}</p>
                <p className="text-slate-400">Similitud: {user.similitud}</p>
                <p className="text-slate-400">
                  En común: {user.peliculas_en_comun}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {result.recommendations?.map((movie) => (
          <MovieCard key={movie.movieId} movie={movie} />
        ))}
      </div>
    </div>
  );
}