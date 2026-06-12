import pandas as pd
import networkx as nx
from collections import defaultdict
import requests

def cargar_recursos():
    """Carga el grafo, el catálogo y los links para imágenes[cite: 160, 276]."""
    G = nx.read_gml("data/grafo_bipartito_peliculas.gml")
    df_movies = pd.read_csv("data/peliculas_2000.csv")[['movieId', 'title', 'genres', 'year']].drop_duplicates()
    
    # Cargamos el mapeo de IDs para obtener fotos [cite: 276]
    df_links = pd.read_csv("data/ml-latest-small/links.csv") # small...
    
    return G, df_movies, df_links

def obtener_url_poster(tmdb_id):
    """Consulta la API de TMDB para obtener la URL del póster[cite: 142, 281]."""
    api_key = "881e28cad3d79854054bcc62f31dab70"
    try:
        # URL de la API de TMDB [cite: 281]
        url = f"https://api.themoviedb.org/3/movie/{int(tmdb_id)}?api_key={api_key}"
        response = requests.get(url, timeout=5)
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w200{poster_path}" # URL de la imagen [cite: 281]
    except:
        pass
    return None

# 2. El "Cerebro" que acepta las calificaciones manuales [cite: 136, 137, 161]
def obtener_recomendaciones_interactivas(G, mis_calificaciones, rating_min=4.0, top_n=10):
    """
    mis_calificaciones: Diccionario tipo {'M_123': 5.0, 'M_456': 4.0} [cite: 137]
    """
    ID_INVITADO = "U_NUEVO" # El nodo temporal [cite: 116, 136]

    # Insertar datos temporalmente en el grafo [cite: 116, 161]
    G.add_node(ID_INVITADO, tipo="usuario", bipartite=0)
    for m_id, calif in mis_calificaciones.items():
        if G.has_node(m_id):
            G.add_edge(ID_INVITADO, m_id, rating=float(calif))
    
    # Nivel 1: Las películas positivas [cite: 45, 53]
    pos_usuario = [m for m in G.neighbors(ID_INVITADO) if G[ID_INVITADO][m].get('rating', 0) >= rating_min]
    
    if not pos_usuario:
        G.remove_node(ID_INVITADO)
        return pd.DataFrame()

    # Nivel 2: Usuarios similares [cite: 45, 54]
    similares = set()
    for m in pos_usuario:
        for u in G.neighbors(m):
            if u != ID_INVITADO and G.nodes[u]['tipo'] == 'usuario':
                if G[u][m].get('rating', 0) >= rating_min:
                    similares.add(u)

    # Nivel 3: Películas candidatas [cite: 45, 55, 56]
    candidatas = defaultdict(list)
    pelis_ya_vistas = set(G.neighbors(ID_INVITADO))
    
    for u in similares:
        for m in G.neighbors(u):
            if G.nodes[m]['tipo'] == 'pelicula' and m not in pelis_ya_vistas:
                r = G[u][m].get('rating', 0)
                if r >= rating_min:
                    candidatas[m].append(r)

    resultados = []
    for m, ratings in candidatas.items():
        datos = G.nodes[m]
        # Extraemos el ID numérico (ej: "M_123" -> 123) para facilitar el mapeo de fotos
        m_id = int(m.replace("M_", ""))
        
        resultados.append({
            "movie_node": m,
            "movieId": m_id,  # <--- Agregamos este campo
            "titulo": datos.get("titulo", m),
            "rating_promedio": round(sum(ratings)/len(ratings), 2),
            "votos": len(ratings)
        })

    # Limpiar el grafo borrando el usuario temporal [cite: 116, 161]
    G.remove_node(ID_INVITADO)

    df_res = pd.DataFrame(resultados)
    if not df_res.empty:
        return df_res.sort_values(by=["rating_promedio", "votos"], ascending=False).head(top_n)
    return df_res
