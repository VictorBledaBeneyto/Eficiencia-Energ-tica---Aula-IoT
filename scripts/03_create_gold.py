import pandas as pd
import numpy as np
import os

ruta_plata = "../data/silver/"
ruta_oro = "../data/gold/"

ruta_dataset_basico = ruta_oro + "dataset_entrenamiento.csv"

df_temp = pd.read_csv(ruta_plata + "temperatura_media_por_hora.csv")
df_hum = pd.read_csv(ruta_plata + "humedad_media_por_hora.csv")
df_sol_elev = pd.read_csv(ruta_plata + "sol_elevacion_media_por_hora.csv")
df_sol_azim = pd.read_csv(ruta_plata + "sol_azimut_media_por_hora.csv")
df_viento = pd.read_csv(ruta_plata + "mislata_viento_media_por_hora.csv")
df_vdir = pd.read_csv(ruta_plata + "mislata_viento_dir_media_por_hora.csv")
df_nubes = pd.read_csv(ruta_plata + "mislata_nubosidad_media_por_hora.csv")
df_mislata_hum = pd.read_csv(ruta_plata + "mislata_humedad_media_por_hora.csv")
df_derroche = pd.read_csv(ruta_plata + "target_derroche_energetico.csv")

df_ce = pd.read_csv(ruta_plata + "target_calefaccion.csv")[['dia', 'hora', 'target']]
df_ce.rename(columns={'target': 'CE'}, inplace=True)

dfs = [df_temp, df_hum, df_sol_elev, df_sol_azim, df_viento, df_vdir, df_nubes, df_mislata_hum, df_ce, df_derroche]
for d in dfs:
    d['dia'] = pd.to_datetime(d['dia']).dt.date

df_nn = df_temp
df_nn = pd.merge(df_nn, df_hum, on=['dia', 'hora'], how='inner')
df_nn = pd.merge(df_nn, df_sol_elev, on=['dia', 'hora'], how='inner')
df_nn = pd.merge(df_nn, df_sol_azim, on=['dia', 'hora'], how='inner')
df_nn = pd.merge(df_nn, df_viento, on=['dia', 'hora'], how='inner')
df_nn = pd.merge(df_nn, df_vdir, on=['dia', 'hora'], how='inner')
df_nn = pd.merge(df_nn, df_nubes, on=['dia', 'hora'], how='inner')
df_nn = pd.merge(df_nn, df_mislata_hum, on=['dia', 'hora'], how='inner')
df_nn = pd.merge(df_nn, df_ce, on=['dia', 'hora'], how='inner')
df_nn = pd.merge(df_nn, df_derroche[['dia', 'hora', 'derroche']], on=['dia', 'hora'], how='inner')

df_nn['fecha_dt'] = pd.to_datetime(df_nn['dia'])
df_nn['mes'] = df_nn['fecha_dt'].dt.month
df_nn['dia_de_la_semana'] = df_nn['fecha_dt'].dt.dayofweek

df_nn.rename(columns={
    'temp_media': 'temperatura_media',
    'sol_elevacion_media': 'sol_elevacion',
    'sol_azimut_media': 'sol_azimut',
    'viento_medio': 'mislata_viento',
    'viento_dir_moda': 'mislata_viento_dir', 
    'nubosidad_media': 'mislata_nubosidad',
    'mislata_humedad_media': 'mislata_humedad'
}, inplace=True)

df_nn = df_nn.sort_values(by=['fecha_dt', 'hora']).reset_index(drop=True)

df_nn['derroche_hora_siguiente'] = df_nn['derroche'].shift(-1)

df_nn.dropna(subset=['derroche_hora_siguiente'], inplace=True)

df_nn['derroche_hora_siguiente'] = df_nn['derroche_hora_siguiente'].astype(int)

columnas_basicas = [
    'mes', 'dia_de_la_semana', 'hora', 'temperatura_media', 'humedad_media', 
    'sol_elevacion', 'sol_azimut', 'mislata_viento', 'mislata_viento_dir', 
    'mislata_nubosidad', 'mislata_humedad', 'CE', 'derroche', 'derroche_hora_siguiente'
]

df_basico = df_nn[columnas_basicas]
df_basico.to_csv(ruta_dataset_basico, index=False)
print("Dataset 1 guardado con exito.")