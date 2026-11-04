"""Actividad 2.2: comparacion de algoritmos candidatos con validacion cruzada
de 5 particiones.
"""

import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import brier_score_loss, r2_score, roc_auc_score
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.neighbors import NearestNeighbors

import comun as c


def cv_reg(modelo, X, y, base=None):
    """R2 y error absoluto mediano (%) fuera de muestra."""
    pred, t0 = np.zeros(len(y)), time.time()
    for tr, te in KFold(5, shuffle=True, random_state=42).split(X):
        pred[te] = (
            base[te] if modelo is None else modelo().fit(X[tr], y[tr]).predict(X[te])
        )
    return (
        r2_score(y, pred),
        np.median(np.exp(np.abs(pred - y)) - 1) * 100,
        time.time() - t0,
    )


def cv_clf(modelo, X, y):
    """AUC y Brier fuera de muestra."""
    p, t0 = np.zeros(len(y)), time.time()
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=7).split(X, y):
        p[te] = modelo().fit(X[tr], y[tr]).predict_proba(X[te])[:, 1]
    return roc_auc_score(y, p), brier_score_loss(y, p), time.time() - t0


# 1. Modulo A: regresion del valor de mercado ----------------------------------
c.titulo("1. Modulo A: candidatos para estimar log(valor) (5 particiones)")
va = c.dataset_valor()
X, y, cat = c.matriz_valor(va)
Xi = X.fillna(X.median())
# one-hot para los modelos lineales
cat_cols = [k for k, es in zip(X.columns, cat) if es]
Xoh = pd.get_dummies(Xi, columns=cat_cols, dtype=float)
Xs = ((Xoh - Xoh.mean()) / Xoh.std().replace(0, 1)).values
base = (
    va.groupby("current_club_domestic_competition_id")
    .log_valor.transform("mean")
    .fillna(va.log_valor.mean())
    .values
)
cand_a = {
    "Linea base (media de la liga)": (None, Xs),
    "Regresion Ridge (lineal)": (lambda: Ridge(alpha=1.0), Xs),
    "Random Forest": (
        lambda: RandomForestRegressor(
            300, min_samples_leaf=5, n_jobs=-1, random_state=42
        ),
        Xi.values,
    ),
    "Gradient Boosting (HGB)": (
        lambda: HistGradientBoostingRegressor(
            max_iter=600,
            learning_rate=0.05,
            min_samples_leaf=30,
            l2_regularization=1.0,
            categorical_features=cat,
            random_state=42,
        ),
        X.values,
    ),
}
res_a = []
for nombre, (m, M) in cand_a.items():
    r2, mae, seg = cv_reg(m, M, y, base)
    res_a.append([nombre, r2, mae, seg])
ta = pd.DataFrame(
    res_a, columns=["modelo", "R2", "error_mediano_%", "segundos"]
).round(3)
print(ta.to_string(index=False))

# 2. Modulo C: clasificacion del exito del fichaje -----------------------------
c.titulo(
    "2. Modulo C: candidatos para P(exito del fichaje) (5 particiones estratificadas)"
)
tr, XT = c.dataset_traspasos()
yt, Z, XTv = tr.exito.values, c.estandarizar(XT), XT.values
cand_c = {
    "Linea base (tasa general)": (lambda: DummyClassifier(strategy="prior"), Z),
    "Regresion logistica (L2)": (lambda: LogisticRegression(C=0.5, max_iter=2000), Z),
    "Random Forest": (
        lambda: RandomForestClassifier(
            400, min_samples_leaf=20, n_jobs=-1, random_state=7
        ),
        np.nan_to_num(XTv),
    ),
    "Gradient Boosting (HGB)": (
        lambda: HistGradientBoostingClassifier(
            max_iter=400, learning_rate=0.05, min_samples_leaf=40, random_state=7
        ),
        XTv,
    ),
}
res_c = []
for nombre, (m, M) in cand_c.items():
    auc, bri, seg = cv_clf(m, M, yt)
    res_c.append([nombre, auc, bri, seg])
tc = pd.DataFrame(res_c, columns=["modelo", "AUC", "Brier", "segundos"]).round(3)
print(tc.to_string(index=False))

# 3. Modulo B: metrica de similitud para reemplazos ----------------------------
c.titulo(
    "3. Modulo B: metrica de similitud (vecinos con la misma subposicion, top 10)"
)
dims = [
    "goles_90",
    "asistencias_90",
    "pases_clave_90",
    "tiros_90",
    "regates_exito_90",
    "entradas_90",
    "intercepciones_90",
    "pct_duelos",
    "calificacion",
]
cam = va[
    (va.minutos >= 900) & va.sub_position.notna() & (va.sub_position != "Goalkeeper")
].reset_index(drop=True)
M = cam[dims].apply(pd.to_numeric, errors="coerce")
M = M.fillna(M.median())
Zm = ((M - M.mean()) / M.std()).clip(-3, 3).values
sp = cam.sub_position.to_numpy(dtype=object)
for metrica in ["euclidean", "cosine", "manhattan"]:
    nn = NearestNeighbors(n_neighbors=11, metric=metrica).fit(Zm)
    idx = nn.kneighbors(Zm, return_distance=False)[:, 1:]
    misma = (sp[idx] == sp[:, None]).mean()
    print(f"{metrica:<10} precision@10 misma subposicion: {misma:.3f}")
print(
    "Azar (proporcion esperada):"
    f" {(cam.sub_position.value_counts(normalize=True) ** 2).sum():.3f}"
)

# 4. Flexibilidad: costo de reentrenar con todos los datos ---------------------
c.titulo("4. Costo de reentrenamiento completo (una corrida)")
t0 = time.time()
cand_a["Gradient Boosting (HGB)"][0]().fit(X.values, y)
ta_s = time.time() - t0
t0 = time.time()
LogisticRegression(C=0.5, max_iter=2000).fit(Z, yt)
tc_s = time.time() - t0
print(
    f"Modulo A (HGB, {len(y):,} jugadores): {ta_s:.1f} s | Modulo C (logistica,"
    f" {len(yt):,} traspasos): {tc_s:.2f} s"
)

fig, ax = plt.subplots(1, 2, figsize=(9, 3))
ax[0].barh(ta.modelo, ta.R2, color="#A6272A")
ax[0].set_title("Modulo A: R2 fuera de muestra")
ax[0].set_xlim(0, 1)
ax[1].barh(tc.modelo, tc.AUC, color="#C8891A")
ax[1].set_title("Modulo C: AUC fuera de muestra")
ax[1].set_xlim(0.4, 0.85)
fig.tight_layout()
fig.savefig(c.SALIDA / "a22_comparacion.png", dpi=150)
