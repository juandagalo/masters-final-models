import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

st.set_page_config(page_title='Predicciones', layout='wide')

BASE = Path('models')
MODELS_DIRS = [BASE / 'trainedModels']
ENC_PATHS = {
    'binary': BASE / 'misc' / 'binary_encoder.joblib',
    'ordinal': BASE / 'misc' / 'ordinal_encoder.joblib',
    'onehot': BASE / 'misc' / 'onehot_encoder.joblib',
    'scaler': BASE / 'misc' / 'scaler_trained.joblib'
}

def load_models():
    for d in MODELS_DIRS:
        if d.exists():
            return sorted(d.glob('*.joblib'))
    return []

def prepare(df):
    # minimal, relies on saved encoders
    be, oe, ohe, scaler = [joblib.load(p) for p in ENC_PATHS.values()]
    binary_cols = ['GENERO', 'POSEE_AUTO']
    ordinal_cols = ['DESC_ESCOLARIDAD_MAX', 'HORA_OFICIAL_INICIO_LABORAL']

    Xb = pd.DataFrame(be.transform(df[binary_cols].astype(object)), columns=binary_cols)
    Xo = pd.DataFrame(oe.transform(df[ordinal_cols].astype(object)), columns=ordinal_cols)

    ohe_in = list(ohe.feature_names_in_) if hasattr(ohe, 'feature_names_in_') else list(ohe.feature_names)
    ohe_cols = []
    for i, cats in enumerate(ohe.categories_):
        name = ohe_in[i]
        ohe_cols += [f"{name}__{c}" for c in cats]
    Xoh = pd.DataFrame(ohe.transform(df[ohe_in]).toarray(), columns=ohe_cols)

    remainder = [c for c in df.columns if c not in (binary_cols + ordinal_cols + ohe_in)]
    Xrem = df[remainder].copy()
    Xrem.columns = [f'remainder__{c}' for c in Xrem.columns]

    Xcand = pd.concat([Xb, Xo, Xoh, Xrem], axis=1)
    train_cols_path = BASE / 'X_train_balanced.csv'
    if train_cols_path.exists():
        cols = pd.read_csv(train_cols_path, nrows=0).columns.tolist()
        for c in cols:
            if c not in Xcand.columns:
                Xcand[c] = 0
        Xcand = Xcand[cols]
    Xs = pd.DataFrame(scaler.transform(Xcand), columns=Xcand.columns)
    return Xs

st.title('Predicciones — minimal')

uploaded = st.file_uploader('CSV con ejemplos (si no subes, uso X_nuevo_prediccion.csv)', type=['csv', 'xlsx'])
df = None
if uploaded is not None:
    if str(uploaded.name).lower().endswith('.csv'):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)
elif Path('X_nuevo_prediccion.csv').exists():
    df = pd.read_csv('X_nuevo_prediccion.csv')

if df is None:
    st.info('Sube un CSV o coloca X_nuevo_prediccion.csv en el directorio.')
    st.stop()

models = load_models()
if not models:
    st.error('No hay modelos en exported_data_and_preprocessing/New_trained_models o trained_models')
    st.stop()

model_names = [p.name for p in models]
sel = st.selectbox('', model_names, index=0)
mdl = joblib.load(models[model_names.index(sel)])

try:
    Xp = prepare(df.copy())
except Exception as e:
    st.error('Error al preparar datos: ' + str(e))
    st.stop()

pred = mdl.predict(Xp)
out = df.copy()
out['prediction'] = pred
if hasattr(mdl, 'predict_proba'):
    probs = mdl.predict_proba(Xp)
    for i in range(probs.shape[1]):
        out[f'prob_{i}'] = probs[:, i]

st.dataframe(out)


