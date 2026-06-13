// Panel de pel�culas calificadas por el usuario
"use client";

import { Loader2, Play, Trash2 } from "lucide-react";
import type { RatedMovie } from "@/lib/types";

type RatingPanelProps = {
  ratedMovies: RatedMovie[];
  loading: boolean;
  onUpdateRating: (movieId: number, rating: number) => void;
  onRemoveMovie: (movieId: number) => void;
  onGenerateRecommendations: () => void;
};

export default function RatingPanel({
  ratedMovies,
  loading,
  onUpdateRating,
  onRemoveMovie,
  onGenerateRecommendations,
}: RatingPanelProps) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 shadow-2xl">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
        <div>
          <h2 className="text-2xl font-black">Tus calificaciones</h2>
          <p className="mt-2 text-sm text-slate-400">
            Ajusta los ratings antes de generar recomendaciones.
          </p>
        </div>

        <button
          onClick={onGenerateRecommendations}
          disabled={loading || ratedMovies.length < 2}
          className="flex items-center justify-center gap-2 rounded-xl bg-violet-500 px-5 py-3 font-bold text-white transition hover:bg-violet-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? <Loader2 className="animate-spin" size={18} /> : <Play size={18} />}
          Recomendar
        </button>
      </div>

      {ratedMovies.length < 2 && (
        <p className="mt-5 rounded-xl bg-yellow-400/10 px-4 py-3 text-sm text-yellow-200">
          Agrega al menos 2 películas para comparar similitud con otros usuarios.
        </p>
      )}

      <div className="mt-6 space-y-4">
        {ratedMovies.map((movie) => (
          <div
            key={movie.movieId}
            className="rounded-2xl border border-white/10 bg-slate-950/80 p-4"
          >
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <h3 className="font-bold">{movie.title}</h3>
                <p className="mt-1 text-sm text-slate-400">{movie.genres}</p>
              </div>

              <button
                onClick={() => onRemoveMovie(movie.movieId)}
                className="inline-flex items-center gap-2 rounded-xl bg-red-500/15 px-3 py-2 text-sm font-semibold text-red-200 hover:bg-red-500/25"
              >
                <Trash2 size={16} />
                Quitar
              </button>
            </div>

            <div className="mt-4 flex flex-col gap-3 md:flex-row md:items-center">
              <input
                type="range"
                min="0.5"
                max="5"
                step="0.5"
                value={movie.rating}
                onChange={(event) =>
                  onUpdateRating(movie.movieId, Number(event.target.value))
                }
                className="w-full"
              />

              <div className="rounded-xl bg-cyan-400/10 px-4 py-2 font-bold text-cyan-200">
                {movie.rating.toFixed(1)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}