// Tarjeta visual para mostrar pel�cula
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

  return (
    <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-4 shadow-xl transition hover:-translate-y-1 hover:bg-slate-900">
      <div className="mb-4 flex h-40 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400/20 to-violet-500/20">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-white/10 text-4xl font-black text-cyan-200">
          {initial}
        </div>
      </div>

      <div className="flex items-start gap-3">
        <div className="rounded-xl bg-cyan-400/10 p-2 text-cyan-300">
          <Film size={18} />
        </div>

        <div className="min-w-0 flex-1">
          <h3 className="line-clamp-2 font-bold text-white">{movie.title}</h3>
          <p className="mt-2 line-clamp-2 text-sm text-slate-400">
            {movie.genres}
          </p>
        </div>
      </div>

      {"score_final" in movie && movie.score_final !== undefined && (
        <div className="mt-4 flex items-center gap-2 rounded-xl bg-yellow-400/10 px-3 py-2 text-sm text-yellow-200">
          <Star size={16} />
          Score final: {movie.score_final}
        </div>
      )}

      {action === "add" && (
        <button
          onClick={onAdd}
          className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-cyan-400 px-4 py-2 font-bold text-slate-950 transition hover:bg-cyan-300"
        >
          <Plus size={18} />
          Agregar
        </button>
      )}

      {action === "remove" && (
        <button
          onClick={onRemove}
          className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-red-500/20 px-4 py-2 font-bold text-red-200 transition hover:bg-red-500/30"
        >
          <Trash2 size={18} />
          Quitar
        </button>
      )}
    </div>
  );
}