import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MovieRec Pro",
  description: "Sistema recomendador de películas con Pearson y géneros",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
