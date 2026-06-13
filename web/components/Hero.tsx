// Secci�n inicial tipo landing
"use client";

import { motion } from "framer-motion";
import { Film, Network, Sparkles } from "lucide-react";

export default function Hero() {
  return (
    <section className="relative overflow-hidden px-6 py-24">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,#22d3ee33,transparent_35%),radial-gradient(circle_at_bottom_right,#a855f733,transparent_35%)]" />

      <div className="relative mx-auto grid max-w-6xl items-center gap-12 md:grid-cols-2">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-cyan-400/40 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-200">
            <Sparkles size={16} />
            Complejidad Algorítmica · TB2
          </div>

          <h1 className="text-5xl font-black tracking-tight md:text-7xl">
            MovieRec{" "}
            <span className="bg-gradient-to-r from-cyan-300 to-violet-400 bg-clip-text text-transparent">
              Pro
            </span>
          </h1>

          <p className="mt-6 max-w-xl text-lg leading-8 text-slate-300">
            Sistema recomendador de películas basado en filtrado colaborativo,
            correlación de Pearson y ponderación por género usando MovieLens.
          </p>

          <div className="mt-8 flex flex-wrap gap-4">
            <a
              href="#recomendador"
              className="rounded-xl bg-cyan-400 px-6 py-3 font-bold text-slate-950 transition hover:bg-cyan-300"
            >
              Probar recomendador
            </a>

            <a
              href="#funcionamiento"
              className="rounded-xl border border-white/15 px-6 py-3 font-semibold text-white transition hover:bg-white/10"
            >
              Ver cómo funciona
            </a>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.92 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur"
        >
          <div className="mb-5 flex items-center gap-3">
            <div className="rounded-2xl bg-cyan-400 p-3 text-slate-950">
              <Film />
            </div>
            <div>
              <h2 className="text-xl font-bold">Motor de recomendación</h2>
              <p className="text-sm text-slate-400">Pearson + Géneros</p>
            </div>
          </div>

          <div className="space-y-4">
            {[
              "Usuario califica películas",
              "Se buscan usuarios similares",
              "Se pondera por géneros preferidos",
              "Se genera el ranking final",
            ].map((item, index) => (
              <div
                key={item}
                className="flex items-center gap-4 rounded-2xl border border-white/10 bg-slate-900/80 p-4"
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-violet-500/20 text-violet-300">
                  {index + 1}
                </div>
                <p className="text-slate-200">{item}</p>
              </div>
            ))}
          </div>

          <div className="mt-6 flex items-center gap-3 rounded-2xl bg-cyan-400/10 p-4 text-cyan-200">
            <Network size={20} />
            Grafo usuario-película + similitud colaborativa
          </div>
        </motion.div>
      </div>
    </section>
  );
}