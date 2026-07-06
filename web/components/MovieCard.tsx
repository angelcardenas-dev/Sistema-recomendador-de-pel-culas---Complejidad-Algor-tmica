// Tarjeta visual para mostrar película
import { Film, Plus, Star, Trash2 } from "lucide-react";
import type { Movie, Recommendation } from "@/lib/types";

type MovieCardProps = {
  movie: Movie | Recommendation;
  action?: "add" | "remove" | "none";
  onAdd?: () => void;
  onRemove?: () => void;
};

export default function MovieCard({
  movie,
  action = "none",
  onAdd,
  onRemove,
}: MovieCardProps) {
  const initial = movie.title?.charAt(0) || "M";

  const genres = movie.genres
    ? movie.genres.split("|").filter((genre) => genre.trim() !== "")
    : [];

  return (
    <div className="group flex h-full flex-col overflow-hidden rounded-3xl border border-white/10 bg-slate-900/80 p-4 shadow-xl transition hover:-translate-y-1 hover:bg-slate-900">
      <div className="mb-4 h-72 overflow-hidden rounded-2xl bg-gradient-to-br from-cyan-400/20 to-violet-500/20">
        {movie.poster_url ? (
          <img
            src={movie.poster_url}
            alt={movie.title}
            className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-white/10 text-4xl font-black text-cyan-200">
              {initial}
            </div>
          </div>
        )}
      </div>

      <div className="flex flex-1 flex-col">
        <div className="flex items-start gap-3">
          <div className="shrink-0 rounded-xl bg-cyan-400/10 p-2 text-cyan-300">
            <Film size={18} />
          </div>

          <div className="min-w-0 flex-1">
            <h3 className="break-words text-sm font-bold leading-5 text-white">
              {movie.title}
            </h3>
          </div>
        </div>

        {genres.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {genres.map((genre) => (
              <span
                key={genre}
                className="rounded-full bg-cyan-400/10 px-2.5 py-1 text-xs font-medium text-cyan-200"
              >
                {genre}
              </span>
            ))}
          </div>
        )}

        {"score_final" in movie && movie.score_final !== undefined && (
          <div className="mt-5 flex items-center gap-2 rounded-xl bg-yellow-400/10 px-3 py-2 text-sm text-yellow-200">
            <Star size={16} />
            Score final: {movie.score_final}
          </div>
        )}

        {action === "add" && (
          <div className="mt-auto pt-6">
            <button
              onClick={onAdd}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-cyan-400 px-4 py-2 font-bold text-slate-950 transition hover:bg-cyan-300"
            >
              <Plus size={18} />
              Agregar
            </button>
          </div>
        )}

        {action === "remove" && (
          <div className="mt-auto pt-6">
            <button
              onClick={onRemove}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-red-500/20 px-4 py-2 font-bold text-red-200 transition hover:bg-red-500/30"
            >
              <Trash2 size={18} />
              Quitar
            </button>
          </div>
        )}
      </div>
    </div>
  );
}