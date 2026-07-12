import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MovieRec Pro",
  description:
    "Sistema recomendador de películas con Pearson, géneros y TMDB",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body>
        {children}

        {/* Registra visitantes y vistas de página en Vercel */}
        <Analytics />
      </body>
    </html>
  );
}