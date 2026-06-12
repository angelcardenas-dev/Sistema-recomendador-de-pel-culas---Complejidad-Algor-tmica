# Descargar la extension Jupyter para VSCode si no la tienen
# Descargar la extension Live Preview for Microsoft Edge para abrir el HTML generado
# Para ejecutar el html generado, da clic derecho sobre el archivo y selecciona "Open with Live Preview"
# Para ejecutar este script, abrirlo en VSCode y usar la opción "Run Cell" en cada bloque de código.
#%%
# ============================================================
# Objetivo:
# Construir un grafo bipartito Usuario-Película usando NetworkX
# a partir del dataset MovieLens filtrado desde el año 2000.
#
# Además, se genera una visualización interactiva con PyVis
# mostrando una muestra útil para explicar filtrado colaborativo.
# ============================================================

# ============================================================
# 1. Importar librerías
# ============================================================
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


from pyvis.network import Network

# Si estás en Jupyter Notebook o Google Colab, puedes usar:
try:
    from IPython.display import IFrame
    USAR_IFRAME = True
except ImportError:
    USAR_IFRAME = False

#%%
# ============================================================
# 2. Cargar dataset preprocesado
# ============================================================
df_2000 = pd.read_csv("data/peliculas_2000.csv")

print("Dataset cargado correctamente.")
print("Cantidad de registros:", len(df_2000))
print(df_2000.head())

#%%
# ============================================================
# 3. Crear grafo bipartito
# ============================================================
G = nx.Graph()

# En este grafo:
# - Los usuarios serán nodos con prefijo U_
# - Las películas serán nodos con prefijo M_
# Esto evita confundir un userId con un movieId que tengan el mismo número.

# ============================================================
# 4. Agregar nodos de usuarios
# ============================================================
usuarios_unicos = df_2000["userId"].unique()

for user_id in usuarios_unicos:
    G.add_node(
        f"U_{user_id}",
        tipo="usuario",
        bipartite=0
    )

print("Nodos de usuarios agregados.")

# ============================================================
# 5. Agregar nodos de películas
# ============================================================
peliculas_unicas = df_2000[["movieId", "title", "genres", "year"]].drop_duplicates()

for _, row in peliculas_unicas.iterrows():
    G.add_node(
        f"M_{row['movieId']}",
        tipo="pelicula",
        bipartite=1,
        titulo=row["title"],
        generos=row["genres"],
        year=row["year"]
    )

print("Nodos de películas agregados.")

# ============================================================
# 6. Agregar aristas con rating
# ============================================================

# Cada fila del dataset representa una calificación.
# En el grafo, cada calificación se convierte en una arista:
# Usuario ---- Película
# El peso de la arista es el rating.

for _, row in df_2000.iterrows():
    user_node = f"U_{row['userId']}"
    movie_node = f"M_{row['movieId']}"

    G.add_edge(
        user_node,
        movie_node,
        rating=row["rating"]
    )

print("Aristas usuario-película agregadas.")

# ============================================================
# 7. Verificar estructura del grafo
# ============================================================

usuarios_grafo = [
    n for n, d in G.nodes(data=True)
    if d["tipo"] == "usuario"
]

peliculas_grafo = [
    n for n, d in G.nodes(data=True)
    if d["tipo"] == "pelicula"
]

print("\n========== RESUMEN DEL GRAFO ==========")
print("Cantidad de usuarios:", len(usuarios_grafo))
print("Cantidad de películas:", len(peliculas_grafo))
print("Cantidad total de nodos:", G.number_of_nodes())
print("Cantidad total de aristas:", G.number_of_edges())

if G.number_of_nodes() >= 2500:
    print("El grafo cumple con el mínimo requerido de 2500 nodos.")
else:
    print("El grafo NO cumple con el mínimo requerido de 2500 nodos.")

print("=======================================\n")

# Guardar el grafo para usarlo en la siguiente etapa
nx.write_gml(G, "data/grafo_bipartito_peliculas.gml")

print("Grafo guardado en: data/grafo_bipartito_peliculas.gml")
#%%
# ============================================================
# 8. Visualización simple de una muestra con Matplotlib
# ============================================================

# más de 2500 nodos harían que la imagen se vea saturada.
# Por eso se toma un usuario y algunas películas que calificó.

usuario_objetivo = max(usuarios_grafo, key=lambda u: G.degree(u))

peliculas_del_usuario = list(G.neighbors(usuario_objetivo))

nodos_muestra = [usuario_objetivo] + peliculas_del_usuario[:30]

G_muestra = G.subgraph(nodos_muestra)

plt.figure(figsize=(14, 8))

pos = nx.spring_layout(G_muestra, seed=42)

nx.draw(
    G_muestra,
    pos,
    with_labels=True,
    node_size=600,
    font_size=8
)

edge_labels = nx.get_edge_attributes(G_muestra, "rating")

nx.draw_networkx_edge_labels(
    G_muestra,
    pos,
    edge_labels=edge_labels,
    font_size=8
)

plt.title(f"Muestra del grafo bipartito: películas calificadas por {usuario_objetivo}")
plt.show()
#%%
# ============================================================
# 9. Visualización interactiva con PyVis
#    Muestra orientada a filtrado colaborativo
# ============================================================

# Esta visualización es más útil para el informe porque muestra:
#
# Usuario objetivo
#     ↓
# Películas que calificó
#     ↓
# Otros usuarios que calificaron esas mismas películas
#
# Esto representa la base del filtrado colaborativo.

usuario_objetivo = max(usuarios_grafo, key=lambda u: G.degree(u))

# Nivel 1: películas calificadas por el usuario objetivo
peliculas_nivel1 = list(G.neighbors(usuario_objetivo))[:10] # Tomamos solo las primeras 10 para no saturar la visualización

# Nivel 2: usuarios que también calificaron esas películas
usuarios_nivel2 = set() # Usamos un set para evitar duplicados

for pelicula in peliculas_nivel1:
    for vecino in G.neighbors(pelicula):
        if vecino != usuario_objetivo and G.nodes[vecino]["tipo"] == "usuario":
            usuarios_nivel2.add(vecino)

usuarios_nivel2 = list(usuarios_nivel2)[:30] # Tomamos solo las primeras 30 para no saturar la visualización

# Nodos que se mostrarán en la visualización
nodos_colaborativos = [usuario_objetivo] + peliculas_nivel1 + usuarios_nivel2

G_colaborativo = G.subgraph(nodos_colaborativos)


# Crear red interactiva
net = Network(
    notebook=True,
    cdn_resources="in_line",
    height="650px",
    width="100%",
    bgcolor="#ffffff",
    font_color="black"
)

# Agregar nodos a PyVis
for nodo, datos in G_colaborativo.nodes(data=True):

    if nodo == usuario_objetivo:
        net.add_node(
            nodo,
            label=nodo,
            title="Usuario objetivo",
            color="orange",
            size=25
        )

    elif datos["tipo"] == "usuario":
        net.add_node(
            nodo,
            label=nodo,
            title="Usuario similar",
            color="lightblue",
            size=15
        )

    else:
        titulo = datos.get("titulo", nodo)
        year = datos.get("year", "")
        generos = datos.get("generos", "")

        net.add_node(
            nodo,
            label=titulo,
            title=f"Película: {titulo}\nAño: {year}\nGéneros: {generos}",
            color="lightgreen",
            size=20
        )

# Agregar aristas a PyVis
for u, v, datos in G_colaborativo.edges(data=True):
    rating = datos.get("rating", "")

    net.add_edge(
        u,
        v,
        title=f"Rating: {rating}",
        label=str(rating)
    )

# Activar física para que los nodos se distribuyan dinámicamente
net.toggle_physics(True)

# Guardar archivo HTML
archivo_html = "grafo_colaborativo.html"
html_content = net.generate_html()
with open(archivo_html, mode='w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Visualización interactiva generada: {archivo_html}")

# Mostrar dentro de Jupyter Notebook o Google Colab
if USAR_IFRAME:
    IFrame(archivo_html, width=900, height=650)


# ============================================================
# 10. Mostrar algunos vecinos como lista de adyacencia
# ============================================================

# cada nodo tiene una lista de nodos adyacentes.

print("\n========== EJEMPLO DE LISTA DE ADYACENCIA ==========")

for nodo in list(G.nodes())[:5]:
    vecinos = list(G.neighbors(nodo))[:10]
    print(nodo, "->", vecinos)

print("====================================================\n")

# #%%
# # ============================================================
# # 11. OPCIONAL: Intentar visualizar el grafo completo
# # ============================================================

# # IMPORTANTE:
# # No se recomienda activar este bloque para el informe principal.
# # El grafo completo puede tener más de 2500 nodos y muchas aristas,
# # por lo que el archivo HTML puede ser pesado y difícil de interpretar.
# #
# # Si el profesor pide ver el grafo completo, se puede descomentar
# # este bloque y probarlo.


# net_completo = Network(
#     notebook=True,
#     cdn_resources="in_line",
#     height="800px",
#     width="100%",
#     bgcolor="#ffffff",
#     font_color="black"
# )

# # Agregar todos los nodos
# for nodo, datos in G.nodes(data=True):

#     if datos["tipo"] == "usuario":
#         net_completo.add_node(
#             nodo,
#             label=nodo,
#             title="Usuario",
#             color="lightblue",
#             size=5
#         )

#     else:
#         titulo = datos.get("titulo", nodo)

#         net_completo.add_node(
#             nodo,
#             label=nodo,
#             title=f"Película: {titulo}",
#             color="lightgreen",
#             size=5
#         )

# # Agregar todas las aristas
# for u, v, datos in G.edges(data=True):
#     rating = datos.get("rating", "")

#     net_completo.add_edge(
#         u,
#         v,
#         title=f"Rating: {rating}"
#     )

# net_completo.toggle_physics(True)

# archivo_completo = "grafo_completo_3000_nodos.html"
# html_content = net_completo.generate_html()
# with open(archivo_completo, mode='w', encoding='utf-8') as f:
#     f.write(html_content)

# print(f"Grafo completo generado: {archivo_completo}")

# if USAR_IFRAME:
#     IFrame(archivo_completo, width=1000, height=800)

# # %%

# %%
