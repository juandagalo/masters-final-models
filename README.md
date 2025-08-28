# Predicciones — README

Este repositorio contiene una app minimal en Streamlit (`main.py`) que carga modelos entrenados y transformadores guardados (joblib) para generar predicciones sobre nuevos ejemplos almacenados en un CSV.

Este README explica paso a paso cómo preparar/actualizar el CSV que la app espera (`X_nuevo_prediccion.csv`), cómo comprobar que los artefactos necesarios existen y cómo ejecutar la app localmente.

## Resumen rápido
- Archivo de entrada esperado (opcional): `X_nuevo_prediccion.csv` en la raíz del proyecto. También puedes subir un CSV/XLSX desde la UI de Streamlit.
- Formatos aceptados: `.csv` y `.xlsx`.
- Comando para iniciar la app:

```powershell
streamlit run main.py
```

## Archivos importantes
- `main.py` — script principal de Streamlit.
- `models/trainedModels/` — carpeta con modelos guardados en formato `.joblib`.
- `models/misc/` — encoders y scaler guardados (por ejemplo: `onehot_encoder.joblib`, `ordinal_encoder.joblib`, `binary_encoder.joblib`, `scaler_trained.joblib`).
- `models/X_train_balanced.csv` — (opcional) archivo con las columnas usadas en entrenamiento; `main.py` lo usa para alinear columnas si existe.

> Nota: Si `models/X_train_balanced.csv` existe, la app ajustará las columnas de entrada para coincidir con las columnas de entrenamiento. Esto evita errores por columnas faltantes o en distinto orden.

## Requisitos mínimos (instalar si aún no lo hiciste)
En PowerShell, desde la carpeta del proyecto:

```powershell
python -m pip install -r requirements.txt
```

Si quieres crear un virtualenv recomendado:

```powershell
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## ¿Dónde poner/actualizar el CSV?
1. Nombre y ubicación por defecto: coloca el archivo con nombre exacto `X_nuevo_prediccion.csv` en la raíz del repositorio (misma carpeta que `main.py`).
2. Alternativa: no pongas el archivo en el disco y, al ejecutar `streamlit run main.py`, sube el CSV o XLSX usando el componente de carga que aparece en la UI.

## Estructura y columnas del CSV — qué debes verificar
`main.py` realiza las siguientes transformaciones y depende de columnas concretas:
- Columnas binarias (esperadas por los encoders binarios):
  - `GENERO`
  - `POSEE_AUTO`

- Columnas ordinales (esperadas por el encoder ordinal):
  - `DESC_ESCOLARIDAD_MAX`
  - `HORA_OFICIAL_INICIO_LABORAL`

- Columnas que pasan por OneHotEncoder: dependen del `onehot_encoder.joblib`. Para conocer exactamente qué columnas (nombres) espera tu encoder, puedes inspeccionarlo localmente (ejemplo abajo).

- Resto de columnas: cualquier otra columna numérica (o categórica transformada previamente) se incluirá como `remainder__{column}` durante la preparación.

Importante: las transformaciones en `main.py` hacen lo siguiente:
- Carga los encoders y scaler desde `models/misc/`.
- Aplica transformaciones en el orden: binary encoder -> ordinal encoder -> onehot encoder -> remainder.
- Si `models/X_train_balanced.csv` existe, la aplicación alinea las columnas de entrada a ese esquema (añade columnas faltantes con 0 y ordena).

### Cómo inspeccionar los encoders para saber qué columnas incluir
Crea un pequeño script `inspect_encoders.py` (o ejecuta en REPL) para listar las entradas que espera cada encoder:

```python
import joblib
from pathlib import Path
p = Path('models/misc')
print('Files in models/misc:', list(p.glob('*.joblib')))

onehot = joblib.load(p / 'onehot_encoder.joblib')
print('onehot.feature_names_in_ (if disponible):')
try:
    print(list(onehot.feature_names_in_))
except Exception:
    pass

print('onehot.categories_ (categorías por característica):')
print([list(c) for c in onehot.categories_])

ord = joblib.load(p / 'ordinal_encoder.joblib')
print('ordinal encoder info (si aplica):', getattr(ord, '__dict__', repr(ord)))

bin_enc = joblib.load(p / 'binary_encoder.joblib')
print('binary encoder info (si aplica):', getattr(bin_enc, '__dict__', repr(bin_enc)))
```

Este script te ayudará a ver exactamente qué columnas necesita el `onehot_encoder` y cómo están ordenadas sus entradas.

## Ejemplo mínimo de CSV
Un CSV mínimo (valores ficticios) podría verse así (separa columnas por comas):

```csv
GENERO,POSEE_AUTO,DESC_ESCOLARIDAD_MAX,HORA_OFICIAL_INICIO_LABORAL,EDAD,SALARIO
M,SI,Secundaria,08:00,34,45000
F,NO,Universitaria,09:00,28,38000
```

Notas:
- Asegúrate de que los valores categóricos coincidan con las categorías que los encoders conocen (o estén presentes en `onehot_encoder.categories_`). Si una categoría nueva aparece, el `onehot` podría lanzar un error en `transform` (dependiendo de cómo se guardó).
- Las columnas adicionales (por ejemplo `EDAD`, `SALARIO`) irán a la parte `remainder` y se renombrarán internamente a `remainder__EDAD`, etc.

## Cómo generar un archivo con solo el header de `X_train_balanced.csv` (útil para crear plantilla)
Si `models/X_train_balanced.csv` existe y quieres crear un CSV vacío que contenga exactamente las columnas de entrenamiento (útil para rellenarlo con nuevos ejemplos), ejecuta en Python:

```python
import pandas as pd
from pathlib import Path
p = Path('models/X_train_balanced.csv')
if p.exists():
    cols = pd.read_csv(p, nrows=0).columns.tolist()
    df = pd.DataFrame(columns=cols)
    df.to_csv('X_nuevo_prediccion.csv', index=False)
    print('Plantilla creada: X_nuevo_prediccion.csv')
else:
    print('No se encontró models/X_train_balanced.csv')
```

Puedes ejecutar ese script con `python create_template.py` o lanzar las líneas interactivamente.

## Verificación rápida antes de ejecutar
1. Asegúrate de que existen los encoders y scaler:
   - `models/misc/onehot_encoder.joblib`
   - `models/misc/ordinal_encoder.joblib`
   - `models/misc/binary_encoder.joblib`
   - `models/misc/scaler_trained.joblib`
2. Asegúrate de que hay al menos un modelo en `models/trainedModels/` (*.joblib).
3. Coloca `X_nuevo_prediccion.csv` en la raíz o sube el CSV desde la UI.

Si algo falta, la app mostrará un mensaje de error y hará `st.stop()` para evitar fallos no gestionados.

## Ejecutar la app
En PowerShell (activando virtualenv si aplica):

```powershell
streamlit run main.py
```

Abre en el navegador la URL que Streamlit indique (normalmente http://localhost:8501).

## Troubleshooting común
- Error al cargar encoders: verifica que los archivos `.joblib` existen y no están corruptos.
- Error en `prepare`: suele indicar columnas faltantes o incompatibles con los encoders; inspecciona `onehot_encoder.categories_` y `models/X_train_balanced.csv`.
- Si `onehot.transform(...).toarray()` falla, puede ser por incompatibilidad de versión de scikit-learn o por que el encoder fue guardado con parámetros distintos.

## Ayuda / próximos pasos
Si quieres, puedo:
- Añadir un script `inspect_encoders.py` en el repo y ejecutarlo para listar categorías y columnas esperadas (útil para crear la plantilla exacta).
- Generar una `X_nuevo_prediccion_template.csv` basada en `models/X_train_balanced.csv` si está presente.

---
Archivo creado por petición del mantenedor del repositorio para documentar cómo actualizar el CSV y ejecutar la app.