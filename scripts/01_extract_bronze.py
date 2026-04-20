import pandas as pd
from sqlalchemy import create_engine
import os
 
user = "postgres"
password = "qwerty1234"
host = "localhost"
port = "5432"
db = "postgres"

try:
    conn_string = f'postgresql://{user}:{password}@{host}:{port}/{db}'
    engine = create_engine(conn_string)

    print("Conectando a la base de datos...")

    query = "SELECT * FROM public.ltss"
    df = pd.read_sql(query, engine)

    ruta_script = os.path.dirname(os.path.abspath(__file__))
    
    raiz_proyecto = os.path.dirname(ruta_script)
    
    directorio_bronze = os.path.join(raiz_proyecto, 'data', 'bronze')

    if not os.path.exists(directorio_bronze):
        os.makedirs(directorio_bronze)
        print(f"Carpeta creada: {directorio_bronze}")

    output_path = os.path.join(directorio_bronze, 'sensors_raw.csv')
    df.to_csv(output_path, index=False)

    print(f"Registros extraídos: {len(df)}")
    print(f"Ubicación: {output_path}")

except Exception as e:
    print(f"Error al descargar los datos: {e}")