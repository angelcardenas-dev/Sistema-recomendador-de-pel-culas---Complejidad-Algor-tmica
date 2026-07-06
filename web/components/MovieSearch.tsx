// Buscador de pel�culas
"use client";

import { useState } from "react";
import { Loader2, Search } from "lucide-react";

import { getPopularMovies, searchMovies } from "@/lib/api";
import type { Movie, RatedMovie } from "@/lib/types";
import MovieCard from "./MovieCard";

type MovieSearchProps = {
  ratedMovies: RatedMovie[];
  onAddMovie: (movie: RatedMovie) => void;
};

export default function MovieSearch({
  ratedMovies,
  onAddMovie,
}: MovieSearchProps) {
  const [query, setQuery] = useState("");
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const ratedIds = new Set(ratedMovies.map((movie) => movie.movieId));

  async function handleSearch() {
    if (!query.trim()) {
      setMessage("Escribe el nombre de una película.");
      return;
    }

    try {
      setLoading(true);
      setMessage("");
      const results = await searchMovies(query, 9);
      setMovies(results);

      if (results.length === 0) {
        setMessage("No se encontraron películas.");
      }
    } catch {
      setMessage("No se pudo conectar con la API. Verifica que FastAPI esté activo.");
    } finally {
      setLoading(false);
    }
  }

  async function handlePopular() {
    try {
      setLoading(true);
      setMessage("");
      const results = await getPopularMovies(9);
      setMovies(results);
    } catch {
      setMessage("No se pudieron cargar películas populares.");
    } finally {
      setLoading(false);
    }
  }

  function addMovie(movie: Movie) {
    if (ratedIds.has(movie.movieId)) {
      setMessage("Esa película ya fue agregada.");
      return;
    }

    onAddMovie({
      movieId: movie.movieId,
      title: movie.title,
      genres: movie.genres,
      poster_url: movie.poster_url,
      rating: 4.5,
    });
  }

  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 shadow-2xl">
      <h2 className="text-2xl font-black">Buscar películas</h2>

      <p className="mt-2 text-sm text-slate-400">
        Busca películas del dataset y agrégalas a tu perfil de gustos.
      </p>

      <div className="mt-6 flex flex-col gap-3 md:flex-row">
        <div className="relative flex-1">
          <Search
            className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
            size={18}
          />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                handleSearch();
              }
            }}
            placeholder="Ejemplo: Matrix, Batman, Toy Story..."
            className="w-full rounded-xl border border-white/10 bg-slate-950 py-3 pl-11 pr-4 outline-none transition focus:border-cyan-400"
          />
        </div>

        <button
          onClick={handleSearch}
          className="rounded-xl bg-cyan-400 px-5 py-3 font-bold text-slate-950 transition hover:bg-cyan-300"
        >
          Buscar
        </button>

        <button
          onClick={handlePopular}
          className="rounded-xl border border-white/10 px-5 py-3 font-semibold transition hover:bg-white/10"
        >
          Populares
        </button>
      </div>

      {message && <p className="mt-4 text-sm text-yellow-200">{message}</p>}

      {loading && (
        <div className="mt-8 flex items-center gap-3 text-cyan-200">
          <Loader2 className="animate-spin" />
          Cargando películas...
        </div>
      )}

      <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-3">
        {movies.map((movie) => (
          <MovieCard
            key={movie.movieId}
            movie={movie}
            action={ratedIds.has(movie.movieId) ? "none" : "add"}
            onAdd={() => addMovie(movie)}
          />
        ))}
      </div>
    </div>
  );
}