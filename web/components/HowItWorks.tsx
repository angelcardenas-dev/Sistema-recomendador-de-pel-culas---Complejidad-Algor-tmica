// Secci�n que explica el funcionamiento del algoritmo
import { Brain, Database, Filter, Star } from "lucide-react";

const steps = [
  {
    icon: Database,
    title: "MovieLens",
    description:
      "Se usa un dataset real con usuarios, películas, géneros y calificaciones.",
  },
  {
    icon: Star,
    title: "Calificaciones",
    description:
      "El usuario selecciona películas y les asigna un rating de 0.5 a 5.",
  },
  {
    icon: Brain,
    title: "Pearson",
    description:
      "Se comparan gustos para encontrar usuarios con patrones similares.",
  },
  {
    icon: Filter,
    title: "Géneros",
    description:
      "El ranking se ajusta según los géneros preferidos del usuario.",
  },
];

export default function HowItWorks() {
  return (
    <section id="funcionamiento" className="px-6 py-20">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-3xl font-black md:text-4xl">
          ¿Cómo funciona el sistema?
        </h2>

        <p className="mt-4 max-w-2xl text-slate-300">
          La recomendación combina similitud entre usuarios y afinidad por
          géneros para generar resultados más personalizados.
        </p>

        <div className="mt-10 grid gap-5 md:grid-cols-4">
          {steps.map((step) => {
            const Icon = step.icon;

            return (
              <div
                key={step.title}
                className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 shadow-xl"
              >
                <div className="mb-5 inline-flex rounded-2xl bg-cyan-400/10 p-3 text-cyan-300">
                  <Icon />
                </div>

                <h3 className="text-xl font-bold">{step.title}</h3>

                <p className="mt-3 text-sm leading-6 text-slate-400">
                  {step.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}