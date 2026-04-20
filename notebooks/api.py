from flask import Flask, request, jsonify, render_template
import tensorflow as tf
import joblib
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model

app = Flask(__name__)

modelo = load_model('../models/modelo_128_64_32_1_relu.keras')
scaler = joblib.load('../models/scaler.pkl')
orden_columnas = joblib.load('../models/orden_columnas.pkl')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        df = pd.DataFrame([data])

        # Aplicar Seno y Coseno
        def transformacion_ciclica(df, columna, max_valor):
            df[columna + '_sin'] = np.sin(2 * np.pi * df[columna] / max_valor)
            df[columna + '_cos'] = np.cos(2 * np.pi * df[columna] / max_valor)
            return df.drop(columns=[columna])

        df = transformacion_ciclica(df, 'mes', 12)
        df = transformacion_ciclica(df, 'dia_de_la_semana', 7)
        df = transformacion_ciclica(df, 'hora', 24)
        df = transformacion_ciclica(df, 'mislata_viento_dir', 360)
        df = transformacion_ciclica(df, 'sol_azimut', 360)

        df = df[orden_columnas]

        x_scaled = scaler.transform(df)

        prediccion = modelo.predict(x_scaled, verbose=0)
        prediccion = float(prediccion[0][0])

        return jsonify({"prediccion": prediccion})
    
    except KeyError as e:
        return jsonify({"status": "error", "message": f"Falta el campo: {str(e)}"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)