// Tipos TypeScript usados en la web
export type Movie = {
  movieId: number;
  title: string;
  genres: string;
  poster_url?: string | null;
  rating_promedio?: number;
  cantidad_votos?: number;
};

export type RatedMovie = {
  movieId: number;
  title: string;
  genres: string;
  rating: number;
  poster_url?: string | null;
};

export type SimilarUser = {
  userId: number;
  similitud: number;
  peliculas_en_comun: number;
};

export type Recommendation = {
  movieId: number;
  title: string;
  genres: string;
  poster_url?: string | null;
  score_pearson?: number;
  score_genero?: number;
  score_final?: number;
  cantidad_votos_similares?: number;
};

export type RecommendationResponse = {
  mensaje: string;
  ratings_validos: number;
  usuarios_similares: SimilarUser[];
  perfil_generos: Record<string, number>;
  recommendations: Recommendation[];
};