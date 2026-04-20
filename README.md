# Proyecto de Eficiencia Energetica - Aula IoT

Este proyecto tiene como objetivo reducir el consumo energetico en un entorno educativo, detectando y prediciendo situaciones de derroche (como el uso de climatizacion con puertas o ventanas abiertas) con una hora de antelacion. Para ello, utilizamos una infraestructura IoT real, procesamiento de datos avanzado y modelos de Inteligencia Artificial.

## Estructura del Repositorio
```text
energy-efficiency-medallion/
├── dashboard/         # Paneles de visualizacion (Grafana/JSON)
├── data/              # CSV's en niveles Bronze, Silver y Gold
├── docker/            # Base de datos PostgreSQL
├── docs/              # Informe tecnico y manuales del proyecto
├── models/            # Modelos entrenados (.pkl para ML y .keras para IA)
├── notebooks/         # Notebooks Jupyter (EDA, entrenamiento) y api.py
├── scripts/           # Scripts generacion de csv's en bronze, silver y gold
├── slides/            # Presentacion para la defensa del proyecto
├── .gitignore         # Archivos excluidos del repositorio
└── README.md          # Documentacion principal del repositorio
```
---

## Cronograma
* **Duracion:** 4 semanas (13h/semana).
* **Periodo:** 1 de marzo al 2 de abril.

---

## Infraestructura Tecnica
El sistema se basa en una arquitectura de datos moderna integrada con:
* **Home Assistant:** Servidor domotico central.
* **Broker:** Mosquitto (MQTT).
* **Pasarela:** Zigbee2MQTT + SLZB-06.
* **Base de Datos:** PostgreSQL en la IP `172.16.204.240`.
* **Sensores:** Aqara (Apertura y ambiente) y Shelly Pro EM-50 (Consumo electrico).

---

## Fases y Desarrollo del Proyecto

### 1. Arquitectura de Datos (Medallion)
Para asegurar la calidad y trazabilidad de la informacion, estructuramos los datos en tres capas:
* **Capa Bronze (RAW):** Ingesta historica en bruto directamente desde PostgreSQL y APIs externas (meteorologia y posicion solar).
* **Capa Silver (Clean):** Depuracion de los datos crudos, tratamiento de valores nulos y estandarizacion de formatos de fecha y hora.
* **Capa Gold (IA Ready):** Datos estructurados y listos para los modelos predictivos, incluyendo la integracion de variables meteorologicas y la generacion del *Target*.

### 2. Analisis Exploratorio de Datos (EDA)
Antes de entrenar los modelos, analizamos el comportamiento de las variables fisicas del aula:
* **Analisis de Correlacion:** Calculamos las matrices de correlacion lineal (Pearson) para los 5 sensores de temperatura y humedad del aula.
* **Eliminacion de redundancia:** Descubrimos una correlacion casi perfecta (entre 0.94 y 1.00) entre los dispositivos. Para evitar datos repetidos, decidimos quedarnos unicamente con el **Sensor 3** como referencia para toda el aula, descartando las columnas del resto.
* **Agrupacion por horas:** Como el objetivo es predecir a una hora vista, convertimos los datos por segundo en bloques de 1 hora. Usamos la **media** para sacar la tendencia general (temperatura, etc.) y la **moda** (el valor mas repetido) exclusivamente para la direccion del viento, al ser puntos cardinales.

### 3. Analisis de Sensores de Ventanas y Puerta
Para calcular el derroche energetico de forma logica y precisa, realizamos un tratamiento especial con los sensores de los accesos:
* **Filtrado de datos:** Descartamos las lecturas de temperatura y humedad de estos dispositivos, utilizando unicamente su estado binario (abierto o cerrado).
* **Falta de correlacion:** A diferencia de la temperatura, las ventanas se abren de forma independiente. Por tanto, conservamos todos los sensores.
* **Ponderacion por tamano:** Para que los datos reflejen el impacto termico real, multiplicamos por 2 los minutos de apertura de las 6 ventanas grandes y de la puerta. Las ventanas pequenas cuentan normal. (La ventana 11 fue descartada por averia en el sensor).
* **Calculo del Derroche:** Transformamos los eventos de apertura a "minutos por hora". Hemos establecido el umbral de derroche en un **45%**: si la suma ponderada de minutos que los accesos estan abiertos supera el 45% de esa hora, se clasifica como situacion de derroche.

### 4. Machine Learning 
**El problema:** No teniamos un sensor fisico que nos dijera si la calefaccion estaba encendida o apagada, dato vital para entrenar a la IA.
**La solucion:** 1. Entrenamos un modelo **Lineal (sklearn)** relacionando nuestro Sensor 3 (aula) con el Sensor 5 (cuarto de calderas). *Metricas excelentes: MAE 0.54 grados C y R^2 0.93.*
2. Aplicamos un **Algoritmo de Etiquetado** basado en la programacion real del termostato del centro (franjas horarias y temperaturas de corte).
3. **Resultado:** Generamos con exito la variable `CE` (Calefaccion Encendida).

### 5. Prediccion de Derroche (Red Neuronal)
Con la capa Gold lista, disenamos una Red Neuronal para predecir el riesgo de derroche a una hora vista.
* **Ingenieria de Variables (Seno/Coseno):** Transformamos matematicamente variables temporales (hora, mes) y direccionales (viento) para que la red entienda los ciclos continuos del tiempo.
* **El problema del desbalanceo:** Como casi nunca hay derroche (98% del tiempo todo esta bien), la primera red fallo. Lo solucionamos aplicando **pesos (1:32)** para forzar a la IA a priorizar los fallos, y bajamos el *Learning Rate* a 0.0001.
* **Modelo Ganador:** Perceptron Multicapa (MLP) de `128 -> 64 -> 32 -> 1` neuronas, activacion `ReLU`.

### 6. Despliegue en Produccion (API REST)
Empaquetamos el "cerebro" de nuestra IA para que interactue con el mundo real.
* **Tecnologia:** Flask (Python).
* **Endpoint `/predict`:** Recibe un JSON con los datos actuales del aula, replica las transformaciones del entrenamiento (Seno/Coseno, estandarizacion con nuestro `scaler.pkl`), hace la inferencia con el modelo `.keras` y devuelve la prediccion instantanea.
* **Ejecucion:** Para levantar el motor de inferencia, ejecutar el archivo `api.py` ubicado en la carpeta `notebooks/`.

### 7. Monitorizacion en Tiempo Real (Dashboard Grafana)
Un panel visual, claro y directo para la toma de decisiones:
* **Monitorizacion de Aperturas:** Lineas de estado (verde/rojo) y contadores inteligentes de aperturas usando la variable interactiva `$sensor`.
* **Evolucion Termica:** Graficas comparativas (Interior vs Exterior) con degradados de color (frio/confort/calor).
* **Indicadores Rapidos (Gauges):** Vistazo inmediato a la temperatura actual.
* **Analisis Meteorologico:** Panel de viento para justificar caidas termicas naturales frente a ineficiencias.

---

## Conclusiones
* **El sistema funciona de principio a fin:** Desde captar el dato fisico hasta predecir con IA en tiempo real.
* **Ingenio frente a limitaciones:** Superamos la falta de hardware inventando nuestro propio "sensor virtual" de calefaccion mediante Machine Learning y logica de negocio.
* **IA adaptada a la realidad:** Demostramos que entender los datos (ciclos horarios, desbalanceo de clases) es tan importante como la arquitectura de la red neuronal.
* **Listo para produccion:** Gracias a la API y Grafana, el proyecto es una herramienta 100% funcional aplicable desde hoy mismo en el centro.

---
