export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="mx-auto flex min-h-screen max-w-6xl flex-col items-center justify-center px-6 text-center">
        <p className="mb-4 rounded-full border border-cyan-400/40 px-4 py-2 text-sm text-cyan-300">
          Complejidad Algorítmica · TB2
        </p>

        <h1 className="max-w-4xl text-5xl font-bold tracking-tight md:text-7xl">
          MovieRec Pro
        </h1>

        <p className="mt-6 max-w-2xl text-lg text-slate-300">
          Sistema recomendador de películas basado en filtrado colaborativo,
          correlación de Pearson y ponderación por género.
        </p>

        <a
          href="#recomendador"
          className="mt-8 rounded-xl bg-cyan-400 px-6 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300"
        >
          Probar recomendador
        </a>
      </section>

      <section id="recomendador" className="mx-auto max-w-6xl px-6 py-20">
        <h2 className="text-3xl font-bold">Recomendador</h2>
        <p className="mt-3 text-slate-300">
          Aquí se integrará el buscador, calificador y resultados de películas.
        </p>
      </section>
    </main>
  );
}
