import customtkinter as ctk
from PIL import Image, ImageTk # Para manejar las imágenes 
import requests
import io
import threading  # <--- Hilos integrados para segundo plano
from obtener_posters_recomendacion import cargar_recursos, obtener_recomendaciones_interactivas, obtener_url_poster

class AppRecomendacion(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MovieRec Pro")
        self.geometry("1200x800")

        # Cargar recursos (ahora incluye df_links) [cite: 182, 280]
        self.G, self.df_movies, self.df_links = cargar_recursos()
        self.mis_calificaciones_dict = {}

        # --- DISEÑO DE GRID (3 Columnas) ---
        self.grid_columnconfigure(0, weight=1) # Buscador
        self.grid_columnconfigure(1, weight=1) # Mis Calificaciones
        self.grid_columnconfigure(2, weight=1) # Recomendaciones
        self.grid_rowconfigure(0, weight=1)

        # === COLUMNA 1: BUSCADOR ===
        self.frame_busqueda = ctk.CTkFrame(self, corner_radius=10)
        self.frame_busqueda.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.lbl_busca = ctk.CTkLabel(self.frame_busqueda, text="🔍 Buscar Películas", font=("Segoe UI", 18, "bold"))
        self.lbl_busca.pack(pady=10)

        self.entry_busqueda = ctk.CTkEntry(self.frame_busqueda, placeholder_text="Ej: Inception...")
        self.entry_busqueda.pack(pady=10, padx=20, fill="x")

        self.btn_buscar = ctk.CTkButton(self.frame_busqueda, text="Buscar", command=self.buscar_pelicula)
        self.btn_buscar.pack(pady=5)

        self.scroll_resultados = ctk.CTkScrollableFrame(self.frame_busqueda, label_text="Catálogo")
        self.scroll_resultados.pack(pady=10, padx=10, fill="both", expand=True)

        # === COLUMNA 2: MIS RATINGS ===
        self.frame_ratings = ctk.CTkFrame(self, corner_radius=10)
        self.frame_ratings.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.lbl_mis_votos = ctk.CTkLabel(self.frame_ratings, text="⭐ Mis Calificaciones", font=("Segoe UI", 18, "bold"))
        self.lbl_mis_votos.pack(pady=10)

        self.scroll_mis_votos = ctk.CTkScrollableFrame(self.frame_ratings)
        self.scroll_mis_votos.pack(pady=10, padx=10, fill="both", expand=True)

        self.btn_recomendar = ctk.CTkButton(self.frame_ratings, text="GENERAR RECOMENDACIONES", 
                                           fg_color="#28a745", hover_color="#218838",
                                           command=self.procesar_recomendaciones)
        self.btn_recomendar.pack(pady=20)

        # === COLUMNA 3: RECOMENDACIONES ===
        self.frame_final = ctk.CTkFrame(self, corner_radius=10, fg_color="#1a1a1a")
        self.frame_final.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        self.lbl_final = ctk.CTkLabel(self.frame_final, text="🎬 Recomendadas", font=("Segoe UI", 18, "bold"))
        self.lbl_final.pack(pady=10)

        self.scroll_final = ctk.CTkScrollableFrame(self.frame_final)
        self.scroll_final.pack(pady=10, padx=10, fill="both", expand=True)

    def descargar_imagen(self, url):
        """Descarga una imagen de internet y la convierte para CTk."""
        try:
            response = requests.get(url, timeout=5)
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            # Ajustamos el tamaño al cuadro (100x150 es estándar de póster)
            return ctk.CTkImage(light_image=img, dark_image=img, size=(100, 150))
        except:
            return None

    def iniciar_descarga_async(self, url, label_widget):
        """Crea un hilo para descargar la imagen sin congelar la interfaz."""
        def worker():
            ctk_img = self.descargar_imagen(url)
            # Verificamos de forma segura si el label aún existe en pantalla
            if label_widget.winfo_exists():
                if ctk_img:
                    # .after manda la instrucción al hilo principal de Tkinter de forma segura
                    self.after(0, lambda: label_widget.configure(image=ctk_img, text=""))
                else:
                    self.after(0, lambda: label_widget.configure(text="🎬\n(No disponible)"))
        
        # daemon=True hace que los hilos se cierren automáticamente si cierras la app
        hilo = threading.Thread(target=worker, daemon=True)
        hilo.start()
    
    def buscar_pelicula(self):
        """Busca películas y muestra su póster si está disponible[cite: 174, 283]."""
        for widget in self.scroll_resultados.winfo_children():
            widget.destroy()

        query = self.entry_busqueda.get().lower()
        if len(query) < 2:
            ctk.CTkLabel(self.scroll_resultados, 
                         text="⚠️ Escribe al menos 2 caracteres para buscar.", 
                         font=("Segoe UI", 12, "italic"),
                         text_color="gray").pack(pady=20)
            return

        resultados = self.df_movies[self.df_movies['title'].str.lower().str.contains(query)].head(15)
        # Si no hay resultados, mostramos un mensaje amigable en lugar de una pantalla vacía
        if resultados.empty:
            ctk.CTkLabel(self.scroll_resultados, 
                         text="❌ No se encontraron coincidencias.\nEsta película no existe en el catálogo.", 
                         font=("Segoe UI", 13, "bold"),
                         text_color="#ff4444").pack(pady=20)
            return

        for _, row in resultados.iterrows():
            # Buscar el tmdbId usando el movieId [cite: 276]
            link_row = self.df_links[self.df_links['movieId'] == row['movieId']]
            
            frame_item = ctk.CTkFrame(self.scroll_resultados)
            frame_item.pack(pady=5, fill="x", padx=5)
            
            # Creamos el Label de la imagen inmediatamente con un texto temporal de carga
            lbl_img = ctk.CTkLabel(frame_item, text="⌛ Cargando...")
            lbl_img.pack(side="top", pady=5)

            # Intentar cargar imagen 
            if not link_row.empty:
                tmdb_id = link_row.iloc[0]['tmdbId']
                url = obtener_url_poster(tmdb_id)
                self.iniciar_descarga_async(url, lbl_img)
            else:
                lbl_img.configure(text="🎬\n(Sin link)")
                
                # ctk_img = self.descargar_imagen(url)
                # if ctk_img:
                #     lbl_img = ctk.CTkLabel(frame_item, image=ctk_img, text="")
                #     lbl_img.pack(side="top", pady=5)

            btn = ctk.CTkButton(frame_item, text=f"{row['title']}", 
                               command=lambda r=row: self.agregar_a_calificaciones(r))
            btn.pack(pady=5, fill="x")

    def agregar_a_calificaciones(self, peli_row):
        m_id = f"M_{peli_row['movieId']}"
        if m_id in self.mis_calificaciones_dict: return

        item_frame = ctk.CTkFrame(self.scroll_mis_votos)
        item_frame.pack(pady=5, fill="x", padx=5)

        lbl_titulo = ctk.CTkLabel(item_frame, text=peli_row['title'], wraplength=120, font=("Segoe UI", 12))
        lbl_titulo.pack(side="left", padx=5)

        # Label que mostrará las estrellas (ej: ⭐⭐⭐⭐½)
        lbl_stars = ctk.CTkLabel(item_frame, text="⭐⭐⭐⭐⭐", text_color="#FFD700")
        lbl_stars.pack(side="right", padx=5)

        # Slider con pasos de 0.5 (8 pasos entre 1 y 5)
        slider = ctk.CTkSlider(item_frame, from_=1, to=5, number_of_steps=8, width=100,
                            command=lambda v, l=lbl_stars: self.actualizar_estrellas(v, l))
        slider.pack(side="right", padx=5)
        slider.set(5)

        self.mis_calificaciones_dict[m_id] = slider

    def actualizar_estrellas(self, valor, label_objetivo):
        """Convierte el valor numérico en iconos de estrellas"""
        enteras = int(valor)
        media = "½" if (valor - enteras) >= 0.5 else ""
        label_objetivo.configure(text=f"{'⭐' * enteras}{media}")

    def procesar_recomendaciones(self):
        """Llama al motor BFS y dibuja los resultados con sus respectivos pósters[cite: 184, 290, 378]."""
        # Limpiar resultados anteriores
        for widget in self.scroll_final.winfo_children():
            widget.destroy()

        if not self.mis_calificaciones_dict:
            return

        # Extraer valores de los sliders (Nivel 0: Usuario objetivo)[cite: 45, 363]
        ratings_finales = {m_id: s.get() for m_id, s in self.mis_calificaciones_dict.items()}

        # Ejecutar lógica BFS (Niveles 1, 2 y 3)[cite: 45, 137, 365]
        recomendaciones = obtener_recomendaciones_interactivas(self.G, ratings_finales)

        if recomendaciones.empty:
            ctk.CTkLabel(self.scroll_final, text="No se encontraron coincidencias.\n¡Califica más películas!").pack(pady=20)
        else:
            for _, row in recomendaciones.iterrows():
                # Crear contenedor para cada recomendación
                f = ctk.CTkFrame(self.scroll_final, border_width=1)
                f.pack(pady=5, fill="x", padx=5)

                # --- BLOQUE DE IMAGEN ---
                # Buscar el tmdbId en el mapeo de links usando el movieId[cite: 276, 291]
                lbl_img = ctk.CTkLabel(f, text="⌛ Cargando...")
                lbl_img.pack(side="top", pady=5)
                link_row = self.df_links[self.df_links['movieId'] == row['movieId']]
                if not link_row.empty:
                    tmdb_id = link_row.iloc[0]['tmdbId']
                    # Consultar URL a la API de TMDB[cite: 142, 369]
                    url = obtener_url_poster(tmdb_id)
                    # Descargar y convertir imagen para CustomTkinter[cite: 283, 370]
                    self.iniciar_descarga_async(url, lbl_img)
                else:
                    lbl_img.configure(text="🎬")
                    # ctk_img = self.descargar_imagen(url)
                    # if ctk_img:
                    #     lbl_img = ctk.CTkLabel(f, image=ctk_img, text="")
                    #     lbl_img.pack(side="top", pady=5)

                # --- BLOQUE DE TEXTO ---
                ctk.CTkLabel(f, text=f"{row['titulo']}", font=("Segoe UI", 13, "bold"), wraplength=250).pack()
                ctk.CTkLabel(f, text=f"Puntaje: {row['rating_promedio']} | Votos: {row['votos']}", 
                            text_color="gray").pack()

if __name__ == "__main__":
    app = AppRecomendacion()
    app.mainloop()