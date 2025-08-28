# CSV de entrada — instrucciones concisas

Archivo esperado por defecto:
- `X_nuevo_prediccion.csv` en la raíz (misma carpeta que `main.py`).
- Alternativa: subir un `.csv` o `.xlsx` desde la UI de Streamlit cuando se ejecute la app.

Formatos aceptados: `.csv`, `.xlsx`.

Columnas requeridas (mínimo)
- Binarias: `GENERO`, `POSEE_AUTO`
- Ordinales: `DESC_ESCOLARIDAD_MAX`, `HORA_OFICIAL_INICIO_LABORAL`

Columnas adicionales
- Las columnas que maneja el `OneHotEncoder` se definen en `models/misc/onehot_encoder.joblib` (revisar `feature_names_in_` o `categories_`).
- Cualquier otra columna entra en el "remainder" y se transformará internamente a `remainder__{col}`.

Plantilla rápida (si existe `models/X_train_balanced.csv`):
```python
import pandas as pd
from pathlib import Path
p = Path('models/X_train_balanced.csv')
if p.exists():
    cols = pd.read_csv(p, nrows=0).columns.tolist()
    pd.DataFrame(columns=cols).to_csv('X_nuevo_prediccion.csv', index=False)
    print('Plantilla creada: X_nuevo_prediccion.csv')
else:
    print('No se encontró models/X_train_balanced.csv')
```

Ejemplo mínimo (CSV):
```
GENERO,POSEE_AUTO,DESC_ESCOLARIDAD_MAX,HORA_OFICIAL_INICIO_LABORAL,EDAD,SALARIO
M,SI,Secundaria,08:00,34,45000
F,NO,Universitaria,09:00,28,38000
```

Verificaciones antes de usar
- `models/misc/onehot_encoder.joblib`, `ordinal_encoder.joblib`, `binary_encoder.joblib`, `scaler_trained.joblib` deben existir.
- Al menos un modelo `.joblib` en `models/trainedModels/`.

Nota: si `models/X_train_balanced.csv` existe, la app alineará las columnas de entrada a ese esquema (añade columnas faltantes con 0 y ordena).

Fin.