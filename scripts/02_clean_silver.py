import pandas as pd
import numpy as np
import os

path_bronce = "../data/bronze/sensors_raw.csv"
ruta_salida = "../data/silver/sensores_filtrados_limpios.csv"
ruta_salida_temp = "../data/silver/Sensor_temperatura/temperatura_media_por_hora.csv"
ruta_salida_hum = "../data/silver/Sensor_temperatura/humedad_media_por_hora.csv"
ruta_salida_sol_elev = "../data/silver/Sensores_sol/sol_elevacion_media_por_hora.csv"
ruta_salida_sol_azim = "../data/silver/Sensores_sol/sol_azimut_media_por_hora.csv"
ruta_salida_viento = "../data/silver/Sensores_Mislata/mislata_viento_media_por_hora.csv"
ruta_salida_viento_dir = "../data/silver/Sensores_Mislata/mislata_viento_dir_media_por_hora.csv"
ruta_salida_nubes = "../data/silver/Sensores_Mislata/mislata_nubosidad_media_por_hora.csv"
ruta_salida_mislata_hum = "../data/silver/Sensores_Mislata/mislata_humedad_media_por_hora.csv"
ruta_salida_ventanas = "../data/silver/Sensores_ventanas_puerta/tiempo_apertura_puerta_ventanas.csv"
ruta_salida_derroche = "../data/silver/Sensores_ventanas_puerta/target_derroche_energetico.csv"

mapeo = {
    'binary_sensor.sensor_puerta_1_contact': 'puerta',
    'binary_sensor.sensor_ventana_1_contact': 'ventana_1',
    'binary_sensor.sensor_ventana_2_contact': 'ventana_2',
    'binary_sensor.sensor_ventana_3_contact': 'ventana_3',
    'binary_sensor.sensor_ventana_4_contact': 'ventana_4',
    'binary_sensor.sensor_ventana_5_contact': 'ventana_5',
    'binary_sensor.sensor_ventana_6_contact': 'ventana_6',
    'binary_sensor.sensor_ventana_7_contact': 'ventana_7',
    'binary_sensor.sensor_ventana_8_contact': 'ventana_8',
    'binary_sensor.sensor_ventana_9_contact': 'ventana_9',
    'binary_sensor.sensor_ventana_10_contact': 'ventana_10',
    'binary_sensor.sensor_ventana_12_contact': 'ventana_12',
    'sensor.sensor_temperatura_3_temperature': 'temp_interior',
    'sensor.sensor_temperatura_3_humidity': 'hum_interior',
    'sensor.sun_solar_elevation': 'sol_elevacion',
    'sensor.sun_solar_azimuth': 'sol_azimut',
    'sensor.mislata_humedad': 'mislata_humedad',
    'sensor.mislata_temperatura': 'mislata_temperatura',
    'sensor.mislata_viento': 'mislata_viento',
    'sensor.mislata_direccion_viento': 'mislata_viento_dir',
    'sensor.mislata_nubosidad': 'mislata_nubosidad'
}

df = pd.read_csv(path_bronce)
df = df[df['entity_id'].isin(mapeo.keys())].copy()
df['sensor'] = df['entity_id'].map(mapeo)
df['valor'] = pd.to_numeric(df['state'].replace({'on': 1, 'off': 0}), errors='coerce')
df = df.dropna(subset=['valor'])

df_final = df[['time', 'sensor', 'valor']].copy()

os.makedirs("../data/silver", exist_ok=True)
df_final.to_csv(ruta_salida, index=False)
print("Sensores base guardado.")

df_final['time'] = pd.to_datetime(df_final['time'], format='ISO8601', utc=True).dt.tz_convert('Europe/Madrid').dt.tz_localize(None)

# PROCESAR TEMPERATURA
df_temp = df_final[df_final["sensor"] == "temp_interior"].copy()
Q1, Q3 = df_temp["valor"].quantile([0.25, 0.75])
IQR = Q3 - Q1
df_temp = df_temp[(df_temp["valor"] >= Q1 - 1.5 * IQR) & (df_temp["valor"] <= Q3 + 1.5 * IQR)]
df_hourly_temp = df_temp.set_index("time").resample("h")["valor"].mean().dropna().reset_index()
df_hourly_temp.rename(columns={"valor": "temp_media"}, inplace=True)
df_hourly_temp["dia"] = df_hourly_temp["time"].dt.date
df_hourly_temp["hora"] = df_hourly_temp["time"].dt.hour
df_hourly_temp["temp_media"] = df_hourly_temp["temp_media"].round(1)
df_hourly_temp[["dia", "hora", "temp_media"]].to_csv(ruta_salida_temp, index=False)

# PROCESAR HUMEDAD
df_hum = df_final[df_final["sensor"] == "hum_interior"].copy()
df_hourly_hum = df_hum.set_index("time").resample("h")["valor"].mean().dropna().reset_index()
df_hourly_hum.rename(columns={"valor": "humedad_media"}, inplace=True)
df_hourly_hum["dia"] = df_hourly_hum["time"].dt.date
df_hourly_hum["hora"] = df_hourly_hum["time"].dt.hour
df_hourly_hum["humedad_media"] = df_hourly_hum["humedad_media"].round(1)
df_hourly_hum[["dia", "hora", "humedad_media"]].to_csv(ruta_salida_hum, index=False)

# PROCESAR ELEVACION SOL
df_sol_elev = df_final[df_final["sensor"] == "sol_elevacion"].copy()
df_hourly_sol_elev = df_sol_elev.set_index("time").resample("h")["valor"].mean().dropna().reset_index()
df_hourly_sol_elev.rename(columns={"valor": "sol_elevacion_media"}, inplace=True)
df_hourly_sol_elev["dia"] = df_hourly_sol_elev["time"].dt.date
df_hourly_sol_elev["hora"] = df_hourly_sol_elev["time"].dt.hour
df_hourly_sol_elev["sol_elevacion_media"] = df_hourly_sol_elev["sol_elevacion_media"].round(1)
df_hourly_sol_elev[["dia", "hora", "sol_elevacion_media"]].to_csv(ruta_salida_sol_elev, index=False)

# PROCESAR AZIMUT SOL
df_sol_azim = df_final[df_final["sensor"] == "sol_azimut"].copy()
df_hourly_sol_azim = df_sol_azim.set_index("time").resample("h")["valor"].mean().dropna().reset_index()
df_hourly_sol_azim.rename(columns={"valor": "sol_azimut_media"}, inplace=True)
df_hourly_sol_azim["dia"] = df_hourly_sol_azim["time"].dt.date
df_hourly_sol_azim["hora"] = df_hourly_sol_azim["time"].dt.hour
df_hourly_sol_azim["sol_azimut_media"] = df_hourly_sol_azim["sol_azimut_media"].round(1)
df_hourly_sol_azim[["dia", "hora", "sol_azimut_media"]].to_csv(ruta_salida_sol_azim, index=False)

# PROCESAR VIENTO
df_viento = df_final[df_final["sensor"] == "mislata_viento"].copy()
df_hourly_viento = df_viento.set_index("time").resample("h")["valor"].mean().dropna().reset_index()
df_hourly_viento.rename(columns={"valor": "viento_medio"}, inplace=True)
df_hourly_viento["dia"] = df_hourly_viento["time"].dt.date
df_hourly_viento["hora"] = df_hourly_viento["time"].dt.hour
df_hourly_viento["viento_medio"] = df_hourly_viento["viento_medio"].round(1)
df_hourly_viento[["dia", "hora", "viento_medio"]].to_csv(ruta_salida_viento, index=False)

# PROCESAR DIRECCION VIENTO
df_vdir = df_final[df_final["sensor"] == "mislata_viento_dir"].copy()
df_hourly_vdir = df_vdir.set_index("time").resample("h")["valor"].apply(
    lambda x: x.mode()[0] if not x.mode().empty else None
).dropna().reset_index()
df_hourly_vdir.rename(columns={"valor": "viento_dir_moda"}, inplace=True)
df_hourly_vdir["dia"] = df_hourly_vdir["time"].dt.date
df_hourly_vdir["hora"] = df_hourly_vdir["time"].dt.hour
df_hourly_vdir["viento_dir_moda"] = df_hourly_vdir["viento_dir_moda"].round(1)
df_hourly_vdir[["dia", "hora", "viento_dir_moda"]].to_csv(ruta_salida_viento_dir, index=False)

# PROCESAR NUBOSIDAD
df_nubes = df_final[df_final["sensor"] == "mislata_nubosidad"].copy()
df_hourly_nubes = df_nubes.set_index("time").resample("h")["valor"].mean().dropna().reset_index()
df_hourly_nubes.rename(columns={"valor": "nubosidad_media"}, inplace=True)
df_hourly_nubes["dia"] = df_hourly_nubes["time"].dt.date
df_hourly_nubes["hora"] = df_hourly_nubes["time"].dt.hour
df_hourly_nubes["nubosidad_media"] = df_hourly_nubes["nubosidad_media"].round(1)
df_hourly_nubes[["dia", "hora", "nubosidad_media"]].to_csv(ruta_salida_nubes, index=False)

# PROCESAR MISLATA HUMEDAD
df_mislata_hum = df_final[df_final["sensor"] == "mislata_humedad"].copy()
df_hourly_mislata_hum = df_mislata_hum.set_index("time").resample("h")["valor"].mean().dropna().reset_index()
df_hourly_mislata_hum.rename(columns={"valor": "mislata_humedad_media"}, inplace=True)
df_hourly_mislata_hum["dia"] = df_hourly_mislata_hum["time"].dt.date
df_hourly_mislata_hum["hora"] = df_hourly_mislata_hum["time"].dt.hour
df_hourly_mislata_hum["mislata_humedad_media"] = df_hourly_mislata_hum["mislata_humedad_media"].round(1)
df_hourly_mislata_hum[["dia", "hora", "mislata_humedad_media"]].to_csv(ruta_salida_mislata_hum, index=False)

# VENTANAS Y PUERTAS
df_vp = df_final[df_final['sensor'].str.contains('ventana|puerta', case=False, na=False)].copy()
df_vp = df_vp[~df_vp['sensor'].str.contains('ventana_11', case=False, na=False)]

def procesar_sensor(group):
    resampled = group.set_index('time')['valor'].resample('1min').ffill().fillna(0)
    return resampled.resample('h').sum()

df_minutos = df_vp.groupby('sensor').apply(procesar_sensor, include_groups=False).reset_index()

if 0 in df_minutos.columns:
    df_minutos.rename(columns={0: 'minutos'}, inplace=True)
else:
    df_minutos.rename(columns={'valor': 'minutos'}, inplace=True)

df_minutos['dia'] = df_minutos['time'].dt.date
df_minutos['hora'] = df_minutos['time'].dt.hour

def aplicar_factor(row):
    sensor = row['sensor']
    minutos = row['minutos']
    if "puerta" in sensor: return minutos * 2
    if "ventana" in sensor:
        num_str = ''.join(filter(str.isdigit, sensor))
        if num_str and int(num_str) % 2 != 0: return minutos * 2
    return minutos

df_minutos['minutos'] = df_minutos.apply(aplicar_factor, axis=1)

df_pivot = df_minutos.pivot_table(index=['dia', 'hora'], columns='sensor', values='minutos', fill_value=0).reset_index()
sensor_cols = [c for c in df_pivot.columns if c not in ['dia', 'hora']]
df_pivot['total_minutos'] = df_pivot[sensor_cols].sum(axis=1)
df_pivot.to_csv(ruta_salida_ventanas, index=False)

# TARGET DERROCHE
umbral_derroche = 1080 * 0.45
df_derroche = df_pivot[['dia', 'hora', 'total_minutos']].copy()
df_derroche['derroche'] = (df_derroche['total_minutos'] > umbral_derroche).astype(int)
df_derroche.to_csv(ruta_salida_derroche, index=False)

print("Capa Plata terminada")