
#%%
# ============================================================
# Objetivo:
# Cargar el dataset MovieLens, filtrar películas desde el año
# 2000 y guardar un subconjunto con 3000 nodos aproximados:
#
# Nodos = usuarios únicos + películas únicas
# ============================================================

# Si les sale error, instalar desde CMD:
# pip install pandas

import pandas as pd


#%%
# ============================================================
# 1. Cargar archivos principales
# ============================================================

ratings = pd.read_csv("data/ml-latest-small/ratings.csv")
movies = pd.read_csv("data/ml-latest-small/movies.csv")

print("Archivos cargados correctamente.")
print("Ratings:", ratings.shape)
print("Películas:", movies.shape)


#%%
# ============================================================
# 2. Unir ratings con películas
# ============================================================

df = ratings.merge(movies, on="movieId")

print("Dataset unido correctamente.")
print("Registros totales:", len(df))


#%%
# ============================================================
# 3. Extraer año desde el título
# ============================================================

df["year"] = df["title"].str.extract(r"\((\d{4})\)")
df["year"] = pd.to_numeric(df["year"], errors="coerce")


#%%
# ============================================================
# 4. Filtrar películas desde el año 2000
# ============================================================

df_2000 = df[df["year"] >= 2000].copy()

print("\nDataset filtrado desde el año 2000.")
print("Ratings desde el año 2000:", len(df_2000))
print("Usuarios únicos:", df_2000["userId"].nunique())
print("Películas únicas:", df_2000["movieId"].nunique())
print("Total de nodos:", df_2000["userId"].nunique() + df_2000["movieId"].nunique())


#%%
# ============================================================
# 5. Seleccionar subconjunto de 3000 nodos
# ============================================================

NODOS_OBJETIVO = 3000

# Cantidad de usuarios disponibles después del filtro
usuarios_disponibles = df_2000["userId"].nunique()

# Como los nodos son usuarios + películas,
# calculamos cuántas películas necesitamos para llegar a 3000 nodos.
peliculas_necesarias = NODOS_OBJETIVO - usuarios_disponibles

if peliculas_necesarias <= 0:
    raise ValueError("La cantidad de usuarios supera o iguala los 3000 nodos objetivo.")

print("\nUsuarios disponibles:", usuarios_disponibles)
print("Películas necesarias:", peliculas_necesarias)

# Seleccionamos las películas con mayor cantidad de ratings.
# Esto ayuda a que el grafo tenga más conexiones y no quede demasiado disperso.
peliculas_seleccionadas = (
    df_2000["movieId"]
    .value_counts()
    .head(peliculas_necesarias)
    .index
)

# Filtramos el dataset solo con esas películas
df_3000 = df_2000[df_2000["movieId"].isin(peliculas_seleccionadas)].copy()


#%%
# ============================================================
# 6. Verificar cantidad final de nodos
# ============================================================

usuarios_finales = df_3000["userId"].nunique()
peliculas_finales = df_3000["movieId"].nunique()
total_nodos_final = usuarios_finales + peliculas_finales
aristas_finales = len(df_3000)

print("\n========== RESUMEN DEL DATASET FINAL ==========")
print("Usuarios únicos:", usuarios_finales)
print("Películas únicas:", peliculas_finales)
print("Total de nodos:", total_nodos_final)
print("Total de aristas / ratings:", aristas_finales)
print("================================================")

if total_nodos_final == NODOS_OBJETIVO:
    print("El dataset final tiene exactamente 3000 nodos.")
elif total_nodos_final > NODOS_OBJETIVO:
    print("El dataset final supera los 3000 nodos.")
else:
    print("El dataset final tiene menos de 3000 nodos. Revisar selección.")


#%%
# ============================================================
# 7. Guardar dataset final
# ============================================================

df_3000.to_csv("data/peliculas_2000.csv", index=False)

print("\nDataset preprocesado guardado correctamente en:")
print("data/peliculas_2000.csv")
# %%
